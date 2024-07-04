# Itai Alcalai
# plot3_actions.py

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
    """
    Lists all files in the unzipped directory.

    Returns:
        list: A list of filenames present in the 'unzipped_dir' directory.
    """
    # List files in the unzipped directory
    return os.listdir('unzipped_dir')

def plot_3d_layout():
    """
    Generates the layout for the 3D plot screen.

    Returns:
        html.Div: A Dash HTML component containing the layout for 3D plotting.
    """
    files = list_files()
    # Generate the layout for 3D plot with dropdowns for file selection
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
        dcc.Store(id="plot3d-status-store"),  # Store for plot status
        dcc.Interval(id="plot3d-check-interval", interval=1000, n_intervals=0)  # Interval to check the plot status
    ])

def plot_data3(file_path1, file_path2, file_path3, well_data, plot_event, plot_error):
    """
    Processes data from the selected files to generate 3D plots.

    Args:
        file_path1 (str): Path to the first file containing the data.
        file_path2 (str): Path to the second file containing the data.
        file_path3 (str): Path to the third file containing the data.
        well_data (tuple): Tuple containing well names and control wells.
        plot_event (threading.Event): Event to signal completion of the plotting process.
        plot_error (threading.Event): Event to signal an error in the plotting process.
    """
    try:
        well_names = well_data[0]
        control_wells = well_data[1]

        def read_file(file_path):
            """
            Reads a CSV file in chunks.

            Args:
                file_path (str): Path to the file to be read.

            Returns:
                pandas.io.parsers.TextFileReader: An iterator to read the file in chunks.
            """
            with open(file_path, 'r') as file:
                first_line = file.readline().strip()
                skip_first_line = 'sep=' in first_line

            # Read the CSV file in chunks to handle large files
            reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
            return reader

        # Initialize readers for the three selected files
        reader1 = read_file(file_path1)
        reader2 = read_file(file_path2)
        reader3 = read_file(file_path3)
        probe1 = get_color(file_path1)
        probe2 = get_color(file_path2)
        probe3 = get_color(file_path3)

        # Create output directory for plots
        output_dir = f"3D_plots_{probe1}_{probe2}_{probe3}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initialize variables for data processing
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
            """
            Generates a 3D scatter plot for the given well.

            Args:
                well (str): The well identifier.
                threshold1 (float): Threshold value for the first file.
                threshold2 (float): Threshold value for the second file.
                threshold3 (float): Threshold value for the third file.
                output_dir (str): Directory to save the plot.
                plot_count (int): Counter for the plot number.
            """
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
            
            # Save the plot to the output directory
            fig.write_html(os.path.join(output_dir, f'{probe1}_{probe2}_{probe3}_plot_{plot_count}_{well}.html'))

        # Process each chunk of data from the readers
        for chunk1, chunk2, chunk3 in zip(reader1, reader2, reader3):
            for index, (row1, row2, row3) in enumerate(zip(chunk1.iterrows(), chunk2.iterrows(), chunk3.iterrows())):
                row1 = row1[1]
                row2 = row2[1]
                row3 = row3[1]

                # If a new well is encountered, plot the data for the previous well
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

        # Plot the data for the last well
        if rfus1_all:
            well_name = well_names.get(current_well, current_well)
            plot_3d_scatter(well_name, threshold1, threshold2, threshold3, output_dir, plot_count)

        plot_event.set()
    except Exception as e:
        plot_error.set()
        plot_events[(file_path1, file_path2, file_path3)] = f"Error: {str(e)}"

def register_plot3_callbacks(app):
    """
    Registers callbacks for the 3D plot feature in the Dash app.

    Args:
        app (Dash): The Dash app instance.
    """
    @app.callback(
        Output("initial-screen", "children", allow_duplicate=True),
        Input("plot-3d", "n_clicks"),
        [State("well-names-store", "data")],
        prevent_initial_call=True
    )
    def plot_3d_screen(n_clicks, data):
        """
        Callback to update the screen layout when the 'Plot 3D' button is clicked.

        Args:
            n_clicks (int): Number of times the button has been clicked.
            data (dict): Stored well names and control wells data.

        Returns:
            html.Div: The layout for the 3D plot screen.
        """
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
        """
        Callback to initiate the 3D plotting process based on user inputs.

        Args:
            selected_file1 (str): The selected first file for plotting.
            selected_file2 (str): The selected second file for plotting.
            selected_file3 (str): The selected third file for plotting.
            well_names (dict): Stored well names and control wells data.

        Returns:
            tuple: HTML div with plot status and plot status store data.
        """
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

        # Start the plotting process in a new thread
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
        """
        Callback to update the plot status at regular intervals.

        Args:
            n_intervals (int): Number of intervals passed.
            plot3d_status_store (dict): Stored plot status data.

        Returns:
            html.Div: Updated plot status message.
        """
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
