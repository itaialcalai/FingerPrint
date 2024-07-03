import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import base64
import io
import zipfile
import dash_bootstrap_components as dbc
from utils import create_well_name_dict
from plot_actions import register_plot_callbacks

def register_callbacks(app):
    @app.callback(
        Output("initial-screen", "children"),
        Output("wells-selection-screen", "style"),
        Output("wells-selection-screen", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
        prevent_initial_call=True
    )
    def handle_file_upload(contents, filenames, last_modified):
        if contents is not None:
            for content, name in zip(contents, filenames):
                _, content_string = content.split(',')
                decoded = base64.b64decode(content_string)
                with zipfile.ZipFile(io.BytesIO(decoded), 'r') as zip_ref:
                    zip_ref.extractall('unzipped_dir')  # Extract the zip file to the 'unzipped_dir'
            
            uploaded_files = html.Div([
                html.Div("Directory successfully unzipped!", style={"color": "green", "marginTop": "10px"}),
                html.Ul([html.Li(f"{name}") for name in filenames])
            ])
            
            wells_selection_layout = html.Div([
                html.Div("Directory successfully unzipped!", style={"color": "green", "marginTop": "10px"}),
                html.Ul([html.Li(f"{name}") for name in filenames]),
                html.H2("Init Wells", style={"textAlign": "center", "marginTop": "20px"}),
                html.Div([
                    # Create 8 rows
                    *[dbc.Row(
                        # Create 3 columns for each row
                        [dbc.Col(dbc.Input(id=f"well-{row}-{col}", type="text", value=f"{chr(65+row)}{col+1}", style={"margin": "5px", "width": "60px"}))
                         for col in range(3)]
                    ) for row in range(8)],
                    html.Div("Enter control well names:", style={"marginTop": "20px"}),
                    dbc.Input(id="control-well-positive", placeholder="Positive Control Well", type="text", style={"margin": "5px", "width": "200px"}),
                    dbc.Input(id="control-well-mix-positive", placeholder="Mix Positive Control Well", type="text", style={"margin": "5px", "width": "200px"}),
                    dbc.Input(id="control-well-negative", placeholder="Negative Control Well", type="text", style={"margin": "5px", "width": "200px"}),
                    dbc.Button("Apply", id="apply-wells", color="primary", style={"marginTop": "20px"})
                ]),
                dcc.Store(id="control-wells-store")  # Add control-wells-store to the layout
            ])

            return uploaded_files, {"display": "block"}, wells_selection_layout

        return html.Div([
            html.Label("Please select zipped working directory", style={"marginTop": "20px"}),
            dcc.Upload(
                id="upload-data",
                children=html.Div([
                    "Drag and Drop or ",
                    html.A("Select Files")
                ]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "marginTop": "10px"
                },
                multiple=True
            ),
            html.Div(id="output-data-upload", style={"marginTop": "20px"})
        ]), {"display": "none"}, None

    @app.callback(
        Output("initial-screen", "children", allow_duplicate=True),
        Output("wells-selection-screen", "style", allow_duplicate=True),
        Output("well-names-store", "data"),
        Input("apply-wells", "n_clicks"),
        [State(f"well-{row}-{col}", "value") for row in range(8) for col in range(3)],
        State("control-well-positive", "value"),
        State("control-well-mix-positive", "value"),
        State("control-well-negative", "value"),
        prevent_initial_call=True
    )
    def apply_wells_selection(n_clicks, *wells_data):
        control_well_positive = wells_data[-3]
        control_well_mix_positive = wells_data[-2]
        control_well_negative = wells_data[-1]
        wells_data = wells_data[:-3]

        if n_clicks:
            wells_matrix = [wells_data[i:i+3] for i in range(0, len(wells_data), 3)]
            well_names = create_well_name_dict(wells_matrix)
            control_wells = {
                "positive": control_well_positive,
                "mix_positive": control_well_mix_positive,
                "negative": control_well_negative
            }
            init_well_data = (well_names, control_wells)
            print(f"Control wells set: {control_wells}")  # Debug statement
            return html.Div([
                html.H3("Init Complete Successfully!", style={"color": "green", "textAlign": "center", "marginTop": "20px"}),
                html.Div(f"Positive Control Well: {control_well_positive}", style={"textAlign": "center"}),
                html.Div(f"Mix Positive Control Well: {control_well_mix_positive}", style={"textAlign": "center"}),
                html.Div(f"Negative Control Well: {control_well_negative}", style={"textAlign": "center"}),
                html.H3("Choose Action", style={"textAlign": "center", "marginTop": "40px"}),
                dbc.Row([
                    dbc.Col(dbc.Button("Plot 1D", id="plot-1d", color="primary", style={"marginTop": "20px"}), width={"size": 2, "offset": 3}),
                    dbc.Col(dbc.Button("Plot 2D", id="plot-2d", color="primary", style={"marginTop": "20px"}), width={"size": 2}),
                    dbc.Col(dbc.Button("Plot 3D", id="plot-3d", color="primary", style={"marginTop": "20px"}), width={"size": 2})
                ])
            ]), {"display": "none"}, init_well_data
        return "", {"display": "block"}, dash.no_update
    
    # Register plot-related callbacks
    register_plot_callbacks(app)
