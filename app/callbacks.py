from dash.dependencies import Input, Output, State
from dash import html, dcc
import base64
import io
import zipfile
from utils import create_well_name_dict
import dash_bootstrap_components as dbc

def register_callbacks(app):
    @app.callback(
        Output("output-data-upload", "children"),
        Output("wells-selection-screen", "style"),
        Output("wells-selection-screen", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified")
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
                html.H2("Init Wells", style={"textAlign": "center", "marginTop": "20px"}),
                html.Div([
                    # Create 8 rows
                    *[dbc.Row(
                        # Create 3 columns for each row
                        [dbc.Col(dbc.Input(id=f"well-{row}-{col}", type="text", value=f"{chr(65+row)}{col+1}", style={"margin": "5px", "width": "60px"}))
                         for col in range(3)]
                    ) for row in range(8)],
                    dbc.Button("Apply", id="apply-wells", color="primary", style={"marginTop": "20px"})
                ])
            ])

            return uploaded_files, {"display": "block"}, wells_selection_layout

        return None, {"display": "none"}, None

    @app.callback(
        Output("output-data-upload", "children", allow_duplicate=True),
        Input("apply-wells", "n_clicks"),
        [State(f"well-{row}-{col}", "value") for row in range(8) for col in range(3)],
        prevent_initial_call=True
    )
    def apply_wells_selection(n_clicks, *wells_data):
        if n_clicks:
            wells_matrix = [wells_data[i:i+3] for i in range(0, len(wells_data), 3)]
            well_names = create_well_name_dict(wells_matrix)
            return html.Div([
                html.H3("Wells Initialization Complete"),
                html.Pre(str(well_names))
            ])
        return ""




