# import dash
# from dash.dependencies import Input, Output, State
# from dash import html, dcc
# import dash_bootstrap_components as dbc
# import os

# def list_files():
#     # List files in the unzipped directory
#     return os.listdir('unzipped_dir')

# def plot_1d_layout():
#     files = list_files()
#     return html.Div([
#         html.H3("Plot 1D", style={"textAlign": "center", "marginTop": "20px"}),
#         html.Div("Choose a file:", style={"textAlign": "center", "marginTop": "20px"}),
#         dcc.Dropdown(
#             id='file-dropdown',
#             options=[{'label': file, 'value': file} for file in files],
#             placeholder="Select a file",
#             style={"width": "50%", "margin": "0 auto"}
#         ),
#         html.H4("Please choose threshold:", style={"textAlign": "center", "marginTop": "20px"}),
#         dbc.Row([
#             dbc.Col(dbc.Button("Default", id="default-threshold", color="primary", style={"marginTop": "20px"}), width={"size": 2, "offset": 3}),
#             dbc.Col(dbc.Button("Calibrated", id="calibrated-threshold", color="primary", style={"marginTop": "20px"}), width={"size": 2})
#         ])
#     ])

# def register_plot_callbacks(app):
#     @app.callback(
#         Output("initial-screen", "children", allow_duplicate=True),
#         Input("plot-1d", "n_clicks"),
#         prevent_initial_call=True
#     )
#     def plot_1d_screen(n_clicks):
#         if n_clicks:
#             return plot_1d_layout()
#         return dash.no_update


import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc
import dash_bootstrap_components as dbc
import os
import pandas as pd
import matplotlib.pyplot as plt
import threading

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
        html.Div(id="plot-output", style={"textAlign": "center", "marginTop": "20px"})
    ])

def plot_data1(file_path, well_names, threshold_type):
    with open(file_path, 'r') as file:
        first_line = file.readline().strip()
        skip_first_line = 'sep=' in first_line

    reader = pd.read_csv(file_path, delimiter=',', skiprows=1 if skip_first_line else 0, chunksize=10000)
    output_dir = f"1D_plots_{os.path.splitext(os.path.basename(file_path))[0]}"
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
                        if threshold is None:
                            # threshold = get_calibrated_threshold(file_path, well_names)
                            threshold = 0.1
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

    return True

def register_plot_callbacks(app):
    @app.callback(
        Output("initial-screen", "children", allow_duplicate=True),
        Input("plot-1d", "n_clicks"),
        prevent_initial_call=True
    )
    def plot_1d_screen(n_clicks):
        if n_clicks:
            return plot_1d_layout()
        return dash.no_update

    @app.callback(
        Output("plot-output", "children"),
        Input("default-threshold", "n_clicks"),
        State("file-dropdown", "value"),
        prevent_initial_call=True
    )
    def plot_1d_default(n_clicks, selected_file):
        if n_clicks and selected_file:
            well_names = {}  # Provide your well names mapping here
            file_path = os.path.join('unzipped_dir', selected_file)
            plot_data1(file_path, well_names, 'default')
            return html.Div("1D plot with default threshold has been created.", style={"color": "green"})
        return dash.no_update
