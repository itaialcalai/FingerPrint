# Itai Alcalai
# plot2_actions.py

import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
import os
import pandas as pd
import matplotlib
# Set Matplotlib to use the 'Agg' backend for non-GUI environments
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import threading
from utils import get_color
import warnings

# Suppress specific Matplotlib warnings
warnings.filterwarnings("ignore", message="Starting a Matplotlib GUI outside of the main thread will likely fail")

# Dictionaries to manage plot events and threads for different files
plot_events = {}
plot_threads = {}

def list_files():
    """
    Lists all files in the unzipped directory.

    Returns:
        list: A list of filenames present in the 'unzipped_dir' directory.
    """
    return os.listdir('unzipped_dir')

def plot_2d_layout():
    """
    Generates the layout for the 2D plot screen.

    Returns:
        html.Div: A Dash HTML component containing the layout for 2D plotting.
    """
    files = list_files()
    # Generate the 2D plot layout with dropdowns for file selection and a button to initiate plotting
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
        html.Button("Plot Default", id="plot-default-button", n_clicks=0, style={"marginTop": "20px", "display": "block", "margin": "0 auto"}),
        html.Div(id="plot-output-2d", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Store(id="plot2d-status-store"),  # Store for plot status
        dcc.Interval(id="plot2d-check-interval", interval=1000, n_intervals=0),  # Interval to check the plot status
        dbc.Button("Back to Plot Menu", id="back-to-main-menu-2", color="secondary", style={"marginTop": "20px", "display": "block", "marginLeft": "auto", "marginRight": "auto"})
    ])

def plot_data2(file_path1, file_path2, well_data, plot_event):
    """
    Processes data from the selected files to generate 2D plots.

    Args:
        file_path1 (str): Path to the first file containing the data.
        file_path2 (str): Path to the second file containing the data.
        well_data (tuple): Tuple containing well names and control wells.
        plot_event (threading.Event): Event to signal completion of the plotting process.

    Returns:
        bool: True if plotting is successful, False otherwise.
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

        # Initialize readers for the two selected files
        reader1 = read_file(file_path1)
        reader2 = read_file(file_path2)
        probe1 = get_color(file_path1)
        probe2 = get_color(file_path2)

        # Create output directory for plots
        output_dir = f"2D_plots_{probe1}_{probe2}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initialize variables for data processing
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
            """
            Generates a 2D scatter plot for the given well.

            Args:
                well (str): The well identifier.
                threshold1 (float): Threshold value for the first file.
                threshold2 (float): Threshold value for the second file.
                output_dir (str): Directory to save the plot.
                plot_count (int): Counter for the plot number.
            """
            # Generate the scatter plot with RFU values and thresholds
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

            # Create legend labels for the plot
            legend_labels = [
                f'+ {probe1} + {probe2} | {ab_ab}',
                f'+ {probe1}, - {probe2} | {ab_bl}',
                f'- {probe1}, + {probe2} | {bl_ab}',
                f'- {probe1}, - {probe2} | {bl_bl}',
                f'Invalid {probe1} | {invalid_x}',
                f'Invalid {probe2} | {invalid_y}'
            ]

            # Colors for the legend
            colors = ['red', probe1[0], probe2[0], 'gray', 'white', 'white']

            # Plot empty scatter points for the legend
            for label, color in zip(legend_labels, colors):
                plt.scatter([], [], color=color, label=label)
            plt.legend()
            # Save the plot to the output directory
            plt.savefig(os.path.join(output_dir, f'{probe1}_{probe2}_plot_{plot_count}_{well}.png'))
            plt.close()

        # Process each chunk of data from the readers
        for chunk1, chunk2 in zip(reader1, reader2):
            for index, (row1, row2) in enumerate(zip(chunk1.iterrows(), chunk2.iterrows())):
                row1 = row1[1]
                row2 = row2[1]

                # If a new well is encountered, plot the data for the previous well
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

                # Categorize RFU values based on thresholds
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

        # Plot the data for the last well
        if rfus1_above or rfus1_below or rfus1_above_below or rfus1_below_above:
            well_name = well_names.get(current_well, current_well)
            plot_2d_scatter(well_name, threshold1, threshold2, output_dir, plot_count)
        
        plot_event.set()
        return True

    except Exception as e:
        print(f"Error in plotting 2D data: {e}")
        plot_event.set()
        return False

def register_plot2_callbacks(app):
    """
    Registers callbacks for the 2D plot feature in the Dash app.

    Args:
        app (Dash): The Dash app instance.
    """
    @app.callback(
        Output("initial-screen", "children", allow_duplicate=True),
        Input("plot-2d", "n_clicks"),
        [State("well-names-store", "data")],
        prevent_initial_call=True
    )
    def plot_2d_screen(n_clicks, data):
        """
        Callback to update the screen layout when the 'Plot 2D' button is clicked.

        Args:
            n_clicks (int): Number of times the button has been clicked.
            data (dict): Stored well names and control wells data.

        Returns:
            html.Div: The layout for the 2D plot screen.
        """
        if n_clicks:
            return plot_2d_layout()
        return dash.no_update

    @app.callback(
        Output("initial-screen", "children", allow_duplicate=True),
        Input("back-to-main-menu-2", "n_clicks"),
        State("well-names-store", "data"),
        prevent_initial_call=True
    )
    def back_to_main_menu(n_clicks, data):
        """
        Callback to return to the main menu when the 'Back to Main Menu' button is clicked.

        Args:
            n_clicks (int): Number of times the button has been clicked.
            data (dict): Stored well names and control wells data.

        Returns:
            html.Div: The layout for the main menu screen.
        """
        if n_clicks:
            well_names, control_wells = data

            # Clean up resources
            for file_path in list(plot_threads.keys()):
                plot_threads[file_path].join(timeout=1)  # Attempt to stop the thread gracefully
                del plot_threads[file_path]

            return html.Div([
                html.H3("Init Complete Successfully!", style={"color": "green", "textAlign": "center", "marginTop": "20px"}),
                html.Div(f"Positive Control Well: {control_wells['positive']}", style={"textAlign": "center"}),
                html.Div(f"Mix Positive Control Well: {control_wells['mix_positive']}", style={"textAlign": "center"}),
                html.Div(f"Negative Control Well: {control_wells['negative']}", style={"textAlign": "center"}),
                html.H3("Choose Action", style={"textAlign": "center", "marginTop": "40px"}),
                dbc.Row([
                    dbc.Col(dbc.Button("Plot 1D", id="plot-1d", color="primary", style={"marginTop": "20px"}), width={"size": 2, "offset": 3}),
                    dbc.Col(dbc.Button("Plot 2D", id="plot-2d", color="primary", style={"marginTop": "20px"}), width={"size": 2}),
                    dbc.Col(dbc.Button("Plot 3D", id="plot-3d", color="primary", style={"marginTop": "20px"}), width={"size": 2})
                ])
            ])
        return dash.no_update

    @app.callback(
        [Output("plot-output-2d", "children"),
         Output("plot2d-status-store", "data")],
        Input("plot-default-button", "n_clicks"),
        [State("file1-dropdown", "value"),
         State("file2-dropdown", "value"),
         State("well-names-store", "data")],
        prevent_initial_call=True
    )
    def plot_2d(n_clicks, selected_file1, selected_file2, well_names):
        """
        Callback to initiate the 2D plotting process based on user inputs.

        Args:
            n_clicks (int): Number of times the 'Plot Default' button has been clicked.
            selected_file1 (str): The selected first file for plotting.
            selected_file2 (str): The selected second file for plotting.
            well_names (dict): Stored well names and control wells data.

        Returns:
            tuple: HTML div with plot status and plot status store data.
        """
        ctx = dash.callback_context
        if n_clicks == 0:
            return dash.no_update, dash.no_update

        if not selected_file1 or not selected_file2:
            return html.Div("Please select two files.", style={"color": "red"}), dash.no_update

        if not well_names:
            return html.Div("Well names not provided.", style={"color": "red"}), dash.no_update

        file_path1 = os.path.join('unzipped_dir', selected_file1)
        file_path2 = os.path.join('unzipped_dir', selected_file2)
        probe_name1 = get_color(selected_file1)
        probe_name2 = get_color(selected_file2)

        plot_event = threading.Event()
        plot_events[(file_path1, file_path2)] = plot_event

        # Start the plotting process in a new thread
        plot_thread = threading.Thread(target=plot_data2, args=(file_path1, file_path2, well_names, plot_event))
        plot_thread.start()
        plot_threads[(file_path1, file_path2)] = plot_thread

        return html.Div(f"Processing 2D plot for probes {probe_name1} and {probe_name2}...", id="plot2d-status", style={"color": "blue"}), {"status": "processing", "file_paths": (file_path1, file_path2)}

    @app.callback(
        Output("plot2d-status", "children"),
        Input("plot2d-check-interval", "n_intervals"),
        State("plot2d-status-store", "data"),
        prevent_initial_call=True
    )
    def update_plot2d_status(n_intervals, plot2d_status_store):
        """
        Callback to update the plot status at regular intervals.

        Args:
            n_intervals (int): Number of intervals passed.
            plot2d_status_store (dict): Stored plot status data.

        Returns:
            html.Div: Updated plot status message.
        """
        if plot2d_status_store and plot2d_status_store.get("status") == "processing":
            file_paths = tuple(plot2d_status_store.get("file_paths"))
            probe_name1 = get_color(file_paths[0])
            probe_name2 = get_color(file_paths[1])
            if plot_events[file_paths].is_set():
                output_message = html.Div(f"Completed 2D plot for probes {probe_name1} and {probe_name2}!", style={"color": "green"})
                return output_message
        return dash.no_update
