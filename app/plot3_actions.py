import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
import os
import pandas as pd
import plotly.graph_objects as go
import threading
from utils import get_color
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail")

# A dictionary to keep track of plot events for different files
plot_events = {}
plot_errors = {}

def list_files():
    # List files in the unzipped directory
    return os.listdir('unzipped_dir')

def plot_3d_layout():
    files = list_files()
    return html.Div([
        html.H3("Plot 3D", style={"textAlign": "center", "marginTop": "20px"}),
        html.Div("Choose three files:", style={"textAlign": "center", "marginTop": "20px"}),
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
        dcc.Dropdown(
            id='file3-dropdown',
            options=[{'label': file, 'value': file} for file in files],
            placeholder="Select the third file",
            style={"width": "50%", "margin": "0 auto", "marginTop": "10px"}
        ),
        html.Div(id="plot-output-3d", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Store(id="plot3d-status-store"),
        dcc.Interval(id="plot3d-check-interval", interval=1000, n_intervals=0)
    ])

def plot_data3(file_path1, file_path2, file_path3, well_data, plot_event, plot_error):
    try:
        well_names = well_data[0]
        control_wells = well_data[1]

        def read_file(file_path):
            with open(file_path, 'r') as file:
                first_line = file.readline().strip()
                skip_first_line = 'sep=' in first_line

            reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
            return reader

        reader1 = read_file(file_path1)
        reader2 = read_file(file_path2)
        reader3 = read_file(file_path3)
        probe1 = get_color(file_path1)
        probe2 = get_color(file_path2)
        probe3 = get_color(file_path3)

        output_dir = f"3D_plots_{probe1}_{probe2}_{probe3}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        current_well = None
        rfus1_all = []
        rfus2_all = []
        rfus3_all = []
        rfus1_positive = []
        rfus2_positive = []
        rfus3_positive = []
        positive_count = 0
        threshold1 = None
        threshold2 = None
        threshold3 = None
        plot_count = 0

        def plot_3d_scatter(well, threshold1, threshold2, threshold3, output_dir, plot_count):
            fig = go.Figure()
            
            # Plot all valid samples in gray
            fig.add_trace(go.Scatter3d(
                x=rfus1_all, y=rfus2_all, z=rfus3_all, mode='markers',
                marker=dict(size=5, color='gray', opacity=0.5),
                name='All Valid Samples'
            ))

            # Plot positive samples in red
            fig.add_trace(go.Scatter3d(
                x=rfus1_positive, y=rfus2_positive, z=rfus3_positive, mode='markers',
                marker=dict(size=5, color='red', opacity=0.8),
                name=f'+ {probe1} + {probe2} + {probe3} | {positive_count}'
            ))

            # Add threshold lines
            fig.add_trace(go.Scatter3d(
                x=[threshold1, threshold1], y=[min(rfus2_all), max(rfus2_all)], z=[min(rfus3_all), max(rfus3_all)],
                mode='lines', line=dict(color=probe1, width=2), name=f'Threshold {probe1}'
            ))

            fig.add_trace(go.Scatter3d(
                x=[min(rfus1_all), max(rfus1_all)], y=[threshold2, threshold2], z=[min(rfus3_all), max(rfus3_all)],
                mode='lines', line=dict(color=probe2, width=2), name=f'Threshold {probe2}'
            ))

            fig.add_trace(go.Scatter3d(
                x=[min(rfus1_all), max(rfus1_all)], y=[min(rfus2_all), max(rfus2_all)], z=[threshold3, threshold3],
                mode='lines', line=dict(color=probe3, width=2), name=f'Threshold {probe3}'
            ))

            fig.update_layout(
                scene=dict(
                    xaxis_title=f'{probe1} Probe RFU',
                    yaxis_title=f'{probe2} Probe RFU',
                    zaxis_title=f'{probe3} Probe RFU'
                ),
                title=f'{probe1} vs {probe2} vs {probe3} 3D Scatter Plot for Well {well}'
            )
            
            fig.write_html(os.path.join(output_dir, f'{probe1}_{probe2}_{probe3}_plot_{plot_count}_{well}.html'))

        for chunk1, chunk2, chunk3 in zip(reader1, reader2, reader3):
            for index, (row1, row2, row3) in enumerate(zip(chunk1.iterrows(), chunk2.iterrows(), chunk3.iterrows())):
                row1 = row1[1]
                row2 = row2[1]
                row3 = row3[1]

                if current_well is None or row1['Well'] != current_well:
                    if rfus1_all:
                        well_name = well_names.get(current_well, current_well)
                        plot_3d_scatter(well_name, threshold1, threshold2, threshold3, output_dir, plot_count)
                        rfus1_all = []
                        rfus2_all = []
                        rfus3_all = []
                        rfus1_positive = []
                        rfus2_positive = []
                        rfus3_positive = []
                        positive_count = 0
                        plot_count += 1
                    current_well = row1['Well']
                    threshold1 = row1['Threshold']
                    threshold2 = row2['Threshold']
                    threshold3 = row3['Threshold']
                    
                if 'RFU' in row1 and pd.notna(row1['RFU']) and 'RFU' in row2 and pd.notna(row2['RFU']) and 'RFU' in row3 and pd.notna(row3['RFU']):
                    rfus1_all.append(row1['RFU'])
                    rfus2_all.append(row2['RFU'])
                    rfus3_all.append(row3['RFU'])
                    if row1['RFU'] > threshold1 and row2['RFU'] > threshold2 and row3['RFU'] > threshold3:
                        rfus1_positive.append(row1['RFU'])
                        rfus2_positive.append(row2['RFU'])
                        rfus3_positive.append(row3['RFU'])
                        positive_count += 1

        if rfus1_all:
            well_name = well_names.get(current_well, current_well)
            plot_3d_scatter(well_name, threshold1, threshold2, threshold3, output_dir, plot_count)

        plot_event.set()
    except Exception as e:
        plot_error.set()
        plot_events[(file_path1, file_path2, file_path3)] = f"Error: {str(e)}"

def register_plot3_callbacks(app):
    @app.callback(
        Output("initial-screen", "children", allow_duplicate=True),
        Input("plot-3d", "n_clicks"),
        [State("well-names-store", "data")],
        prevent_initial_call=True
    )
    def plot_3d_screen(n_clicks, data):
        if n_clicks:
            return plot_3d_layout()
        return dash.no_update

    @app.callback(
        [Output("plot-output-3d", "children"),
         Output("plot3d-status-store", "data")],
        [Input("file1-dropdown", "value"),
         Input("file2-dropdown", "value"),
         Input("file3-dropdown", "value")],
        [State("well-names-store", "data")],
        prevent_initial_call=True
    )
    def plot_3d(selected_file1, selected_file2, selected_file3, well_names):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update

        if not selected_file1 or not selected_file2 or not selected_file3:
            return html.Div("Please select all three files to proceed.", style={"color": "red"}), dash.no_update

        if not well_names:
            return html.Div("Well names data is missing. Please ensure the well names are initialized.", style={"color": "red"}), dash.no_update

        file_path1 = os.path.join('unzipped_dir', selected_file1)
        file_path2 = os.path.join('unzipped_dir', selected_file2)
        file_path3 = os.path.join('unzipped_dir', selected_file3)
        probe_name1 = get_color(selected_file1)
        probe_name2 = get_color(selected_file2)
        probe_name3 = get_color(selected_file3)

        plot_event = threading.Event()
        plot_error = threading.Event()
        plot_events[(file_path1, file_path2, file_path3)] = plot_event
        plot_errors[(file_path1, file_path2, file_path3)] = plot_error

        threading.Thread(target=plot_data3, args=(file_path1, file_path2, file_path3, well_names, plot_event, plot_error)).start()

        return (html.Div(f"Processing 3D plot for probes {probe_name1}, {probe_name2}, and {probe_name3}...", id="plot3d-status", style={"color": "blue"}),
                {"status": "processing", "file_paths": (file_path1, file_path2, file_path3)})

    @app.callback(
        Output("plot3d-status", "children"),
        Input("plot3d-check-interval", "n_intervals"),
        State("plot3d-status-store", "data"),
        prevent_initial_call=True
    )
    def update_plot3d_status(n_intervals, plot3d_status_store):
        if plot3d_status_store and plot3d_status_store.get("status") == "processing":
            file_paths = tuple(plot3d_status_store.get("file_paths"))
            probe_name1 = get_color(file_paths[0])
            probe_name2 = get_color(file_paths[1])
            probe_name3 = get_color(file_paths[2])
            if plot_errors[file_paths].is_set():
                output_message = html.Div(f"Error occurred while processing 3D plot for probes {probe_name1}, {probe_name2}, and {probe_name3}: {plot_events[file_paths]}", style={"color": "red"})
                return output_message
            if plot_events[file_paths].is_set():
                output_message = html.Div(f"Completed 3D plot for probes {probe_name1}, {probe_name2}, and {probe_name3}!", style={"color": "green"})
                return output_message
        return dash.no_update
