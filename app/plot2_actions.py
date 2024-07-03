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
import warnings



# Suppress the specific Matplotlib warning
warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail")

# A dictionary to keep track of plot events for different files
plot_events = {}

def list_files():
    # List files in the unzipped directory
    return os.listdir('unzipped_dir')

def plot_2d_layout():
    files = list_files()
    return html.Div([
        html.H3("Plot 2D", style={"textAlign": "center", "marginTop": "20px"}),
        html.Div("Choose two files:", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Dropdown(
            id='file1-dropdown',
            options=[{'label': file, 'value': file} for file in files],
            placeholder="Select the first file",
            style={"width": "50%", "margin": "0 auto"}
        ),
        dcc.Dropdown(
            id='file2-dropdown',
            options=[{'label': file, 'value': file} for file in files],
            placeholder="Select the second file",
            style={"width": "50%", "margin": "0 auto", "marginTop": "10px"}
        ),
        html.Div(id="plot-output-2d", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Store(id="plot2d-status-store"),
        dcc.Interval(id="plot2d-check-interval", interval=1000, n_intervals=0)
    ])

def plot_data2(file_path1, file_path2, well_data, plot_event):
    well_names = well_data[0]
    control_wells = well_data[1]
    print(f'In plot well names is', well_names)
    def read_file(file_path):
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()
            skip_first_line = 'sep=' in first_line

        reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
        return reader

    reader1 = read_file(file_path1)
    reader2 = read_file(file_path2)
    probe1 = get_color(file_path1)
    probe2 = get_color(file_path2)

    output_dir = f"2D_plots_{probe1}_{probe2}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    current_well = None
    rfus1_above = []
    rfus2_above = []
    rfus1_below = []
    rfus2_below = []
    rfus1_above_below = []
    rfus2_above_below = []
    rfus1_below_above = []
    rfus2_below_above = []
    ab_ab = 0
    ab_bl = 0
    bl_ab = 0
    bl_bl = 0
    invalid_x = 0
    invalid_y = 0
    threshold1 = None
    threshold2 = None
    plot_count = 0

    def plot_2d_scatter(well, threshold1, threshold2, output_dir, plot_count):
        print("In scatter")
        plt.figure()
        plt.scatter(rfus1_above, rfus2_above, color='red', alpha=0.8)
        plt.scatter(rfus1_above_below, rfus2_above_below, color=probe1[0], alpha=0.5)
        plt.scatter(rfus1_below_above, rfus2_below_above, color=probe2[0], alpha=0.5)
        plt.scatter(rfus1_below, rfus2_below, color='gray', alpha=0.3)
        plt.axhline(y=threshold2, color=probe2[0], linestyle='--', linewidth=1)
        plt.axvline(x=threshold1, color=probe1[0], linestyle='--', linewidth=1)
        plt.xlabel(f'{probe1} Probe RFU')
        plt.ylabel(f'{probe2} Probe RFU')
        plt.title(f'{probe1} vs {probe2} 2D Scatter Plot for Well {well}')

        legend_labels = [
            f'+ {probe1} + {probe2} | {ab_ab}',
            f'+ {probe1}, - {probe2} | {ab_bl}',
            f'- {probe1}, + {probe2} | {bl_ab}',
            f'- {probe1}, - {probe2} | {bl_bl}',
            f'Invalid {probe1} | {invalid_x}',
            f'Invalid {probe2} | {invalid_y}'
        ]

        colors = ['red', probe1[0], probe2[0], 'gray', 'white', 'white']

        for label, color in zip(legend_labels, colors):
            plt.scatter([], [], color=color, label=label)
        plt.legend()
        plt.savefig(os.path.join(output_dir, f'{probe1}_{probe2}_plot_{plot_count}_{well}.png'))
        plt.close()
        print("finish scatter")

    for chunk1, chunk2 in zip(reader1, reader2):
        for index, (row1, row2) in enumerate(zip(chunk1.iterrows(), chunk2.iterrows())):
            row1 = row1[1]
            row2 = row2[1]

            if current_well is None or row1['Well'] != current_well:
                if rfus1_above or rfus1_below or rfus1_above_below or rfus1_below_above:
                    well_name = well_names.get(current_well, current_well)
                    plot_2d_scatter(well_name, threshold1, threshold2, output_dir, plot_count)
                    rfus1_above = []
                    rfus2_above = []
                    rfus1_below = []
                    rfus2_below = []
                    rfus1_above_below = []
                    rfus2_above_below = []
                    rfus1_below_above = []
                    rfus2_below_above = []
                    invalid_x = invalid_y = ab_ab = ab_bl = bl_ab = bl_bl = 0
                    plot_count += 1
                current_well = row1['Well']
                threshold1 = row1['Threshold']
                threshold2 = row2['Threshold']

            if 'RFU' in row1 and pd.notna(row1['RFU']) and 'RFU' in row2 and pd.notna(row2['RFU']):
                if row1['RFU'] > threshold1 and row2['RFU'] > threshold2:
                    rfus1_above.append(row1['RFU'])
                    rfus2_above.append(row2['RFU'])
                    ab_ab += 1
                elif row1['RFU'] > threshold1 and row2['RFU'] <= threshold2:
                    rfus1_above_below.append(row1['RFU'])
                    rfus2_above_below.append(row2['RFU'])
                    ab_bl += 1
                elif row1['RFU'] <= threshold1 and row2['RFU'] > threshold2:
                    rfus1_below_above.append(row1['RFU'])
                    rfus2_below_above.append(row2['RFU'])
                    bl_ab += 1
                else:
                    rfus1_below.append(row1['RFU'])
                    rfus2_below.append(row2['RFU'])
                    bl_bl += 1
            elif 'RFU' in row1 and not pd.notna(row1['RFU']):
                invalid_x += 1
            elif 'RFU' in row2 and not pd.notna(row2['RFU']):
                invalid_y += 1

    if rfus1_above or rfus1_below or rfus1_above_below or rfus1_below_above:
        well_name = well_names.get(current_well, current_well)
        plot_2d_scatter(well_name, threshold1, threshold2, output_dir, plot_count)
    
    plot_event.set()
    return True

def register_plot2_callbacks(app):
    @app.callback(
        Output("initial-screen", "children", allow_duplicate=True),
        Input("plot-2d", "n_clicks"),
        [State("well-names-store", "data")],
        prevent_initial_call=True
    )
    def plot_2d_screen(n_clicks, data):
        if n_clicks:
            return plot_2d_layout()
        return dash.no_update

    @app.callback(
        [Output("plot-output-2d", "children"),
         Output("plot2d-status-store", "data")],
        [Input("file1-dropdown", "value"),
         Input("file2-dropdown", "value")],
        [State("well-names-store", "data")],
        prevent_initial_call=True
    )
    def plot_2d(selected_file1, selected_file2, well_names):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update

        if not selected_file1 or not selected_file2:
            return dash.no_update, dash.no_update

        if not well_names:
            return dash.no_update, dash.no_update

        file_path1 = os.path.join('unzipped_dir', selected_file1)
        file_path2 = os.path.join('unzipped_dir', selected_file2)
        probe_name1 = get_color(selected_file1)
        probe_name2 = get_color(selected_file2)

        plot_event = threading.Event()
        plot_events[(file_path1, file_path2)] = plot_event

        threading.Thread(target=plot_data2, args=(file_path1, file_path2, well_names, plot_event)).start()

        return (html.Div(f"Processing 2D plot for probes {probe_name1} and {probe_name2}...", id="plot2d-status", style={"color": "blue"}),
                {"status": "processing", "file_paths": (file_path1, file_path2)})

    @app.callback(
        Output("plot2d-status", "children"),
        Input("plot2d-check-interval", "n_intervals"),
        State("plot2d-status-store", "data"),
        prevent_initial_call=True
    )
    def update_plot2d_status(n_intervals, plot2d_status_store):
        if plot2d_status_store and plot2d_status_store.get("status") == "processing":
            file_paths = tuple(plot2d_status_store.get("file_paths"))
            probe_name1 = get_color(file_paths[0])
            probe_name2 = get_color(file_paths[1])
            if plot_events[file_paths].is_set():
                output_message = html.Div(f"Completed 2D plot for probes {probe_name1} and {probe_name2}!", style={"color": "green"})
                return output_message
        return dash.no_update
