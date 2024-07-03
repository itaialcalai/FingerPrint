import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
import os
import pandas as pd
import matplotlib
# Set Matplotlib to use the 'Agg' backend
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import threading
from utils import get_color
from threshold_calibration import get_calibrated_threshold
import warnings

# Suppress the specific Matplotlib warning
warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail")

# A dictionary to keep track of plot events for different files
plot_events = {}
# A dictionary to store error messages
plot_errors = {}
# A dictionary to store print messages
plot_prints = {}

def list_files():
    # List files in the unzipped directory
    return os.listdir('unzipped_dir')

def plot_1d_layout():
    files = list_files()
    return html.Div([
        html.H3("Plot 1D", style={"textAlign": "center", "marginTop": "20px"}),
        html.Div("Choose a file:", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Dropdown(
            id='file-dropdown',
            options=[{'label': file, 'value': file} for file in files],
            placeholder="Select a file",
            style={"width": "50%", "margin": "0 auto"}
        ),
        html.H4("Please choose threshold:", style={"textAlign": "center", "marginTop": "20px"}),
        dbc.Row([
            dbc.Col(dbc.Button("Default", id="default-threshold", color="primary", style={"marginTop": "20px"}), width={"size": 2, "offset": 3}),
            dbc.Col(dbc.Button("Calibrated", id="calibrated-threshold", color="primary", style={"marginTop": "20px"}), width={"size": 2})
        ]),
        html.Div(id="plot-output", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Store(id="plot-status-store"),  # Store for plot status
        dcc.Store(id="control-wells-store"),  # Store for control well names
        dcc.Interval(id="plot-check-interval", interval=1000, n_intervals=0)  # Interval to check the plot status
    ])

def plot_data1(file_path, well_names, threshold_type, control_wells=None):
    try:
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
            skip_first_line = 'sep=' in first_line

        reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
        output_dir = f"1D_plots_{os.path.splitext(os.path.basename(get_color(file_path)))[0]}_{threshold_type}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        current_well = None
        rfus = []
        threshold = None
        plot_count = 0

        for chunk in reader:
            for index, row in chunk.iterrows():
                if current_well is None or row['Well'] != current_well:
                    if rfus:
                        well_name = well_names.get(current_well, current_well)  # Get well name from well_names dict
                        # threshold handle
                        if threshold_type == 'default':
                            if threshold is None and 'Threshold' in chunk.columns:
                                threshold = row['Threshold']
                        else:
                            if threshold is None and control_wells:
                                plot_prints[file_path] = "Calibrating threshold..."
                                try:
                                    threshold = get_calibrated_threshold(file_path, well_names, control_wells)
                                    plot_prints[file_path] = "Calibrated successfully, continuing to plot..."
                                except Exception as e:
                                    plot_errors[file_path] = "Error calibrating threshold: " + str(e)
                                    return False
                        # Assign indices according to dPCR device logic
                        x_indices = [(i % 80) + 1 for i in range(len(rfus))]  # -> [1-80], [1-80],...
                        plt.figure(figsize=(10, 6))
                        plt.scatter(x_indices, rfus, alpha=0.5)
                        plt.axhline(y=threshold, color='r', linestyle='-')
                        plt.title(f'Probe Scatter Plot for Well {well_name}')
                        plt.xlabel('Sample Index')
                        plt.ylabel('RFU')
                        plt.savefig(os.path.join(output_dir, f'plot_{plot_count}_{well_name}.png'))
                        plt.close()
                        rfus = []
                        plot_count += 1
                    current_well = row['Well']
                    if threshold_type == 'default':
                        if row['Threshold'] != threshold:
                            threshold = row['Threshold']

                if 'RFU' in row and pd.notna(row['RFU']):
                    rfus.append(row['RFU'])
        # Handle the last set of RFUs collected
        if rfus:
            x_indices = [(i % 80) + 1 for i in range(len(rfus))]
            plt.figure(figsize=(10, 6))
            plt.scatter(x_indices, rfus, alpha=0.5)
            plt.axhline(y=threshold, color='r', linestyle='-')
            plt.title(f'Probe Scatter Plot for Well {current_well}')
            plt.xlabel('Sample Index')
            plt.ylabel('RFU')
            well_name = well_names.get(current_well, current_well)
            plt.savefig(os.path.join(output_dir, f'plot_{plot_count}_{well_name}.png'))
            plt.close()

        # Set the event to indicate completion
        plot_events[file_path].set()
    except Exception as e:
        plot_events[file_path].set()
        plot_errors[file_path] = str(e)
    return True

def register_plot1_callbacks(app):
    @app.callback(
        Output("initial-screen", "children", allow_duplicate=True),
        Input("plot-1d", "n_clicks"),
        [State("well-names-store", "data")],
        prevent_initial_call=True
    )
    def plot_1d_screen(n_clicks, data):
        if n_clicks:
            control_wells = data[1]
            names = data[0]
            return plot_1d_layout()
        return dash.no_update

    @app.callback(
        [Output("plot-output", "children"),
         Output("plot-status-store", "data")],
        [Input("default-threshold", "n_clicks"),
         Input("calibrated-threshold", "n_clicks")],
        [State("file-dropdown", "value"),
         State("well-names-store", "data")],  # Add control-wells-store to the states
        prevent_initial_call=True
    )
    def plot_1d(n_clicks_default, n_clicks_calibrated, selected_file, data):  # Add control_wells parameter
        control_wells = data[1]
        well_names = data[0]

        ctx = dash.callback_context
        if not ctx.triggered:
            plot_prints[selected_file] = "No button clicks detected."
            return (html.Div("No button clicks detected.", style={"color": "red"}), dash.no_update)

        if not selected_file:
            plot_prints[selected_file] = "No file selected."
            return (html.Div("No file selected.", style={"color": "red"}), dash.no_update)

        if not well_names:
            plot_prints[selected_file] = "Well names not provided."
            return (html.Div("Well names not provided.", style={"color": "red"}), dash.no_update)

        if not control_wells:  # Check if control wells are provided
            plot_prints[selected_file] = "Control wells not provided."
            return (html.Div("Control wells not provided.", style={"color": "red"}), dash.no_update)

        plot_prints[selected_file] = "Button clicked, checking states..."
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        threshold_type = 'default' if button_id == 'default-threshold' else 'calibrated'

        file_path = os.path.join('unzipped_dir', selected_file)
        probe_name = get_color(selected_file)

        plot_event = threading.Event()
        plot_events[file_path] = plot_event
        plot_errors[file_path] = None  # Clear previous errors

        threading.Thread(target=plot_data1, args=(file_path, well_names, threshold_type, control_wells)).start()

        threshold_type_text = "default" if threshold_type == 'default' else 'calibrated'
        return (html.Div(f"Processing 1D plot with {threshold_type_text} threshold for probe {probe_name}...", id="plot-status", style={"color": "blue"}),
                {"status": "processing", "file_path": file_path, "threshold_type": threshold_type})

    @app.callback(
        Output("plot-status", "children"),
        Input("plot-check-interval", "n_intervals"),
        State("plot-status-store", "data"),
        prevent_initial_call=True
    )
    def update_plot_status(n_intervals, plot_status_store):
        if plot_status_store and plot_status_store.get("status") == "processing":
            file_path = plot_status_store.get("file_path")
            probe_name = get_color(file_path)
            threshold_type = plot_status_store.get("threshold_type")
            threshold_type_text = "default" if threshold_type == 'default' else "calibrated"
            if plot_events[file_path].is_set():
                if file_path in plot_errors and plot_errors[file_path]:
                    error_message = html.Div(f"Error: 1D plot with {threshold_type_text} threshold for probe {probe_name} - {plot_errors[file_path]}", style={"color": "red"})
                    return error_message
                elif file_path in plot_prints and plot_prints[file_path] in ["No button clicks detected.", "No file selected.", "Well names not provided.", "Control wells not provided."]:
                    print_message = html.Div(f"{plot_prints[file_path]}", style={"color": "red"})
                    return print_message
                else:
                    output_message = html.Div(f"Completed 1D plot with {threshold_type_text} threshold for probe {probe_name}!", style={"color": "green"})
                    return output_message
            elif file_path in plot_prints and plot_prints[file_path]:
                print_message = html.Div(f"{plot_prints[file_path]}", style={"color": "blue"})
                return print_message
        return dash.no_update
