# Itai Alcalai
# app.py

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from callbacks import register_callbacks

# Create the Dash app instance
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Define the layout of the app
app.layout = dbc.Container([
    # First row for the header
    dbc.Row([
        dbc.Col([
            # Main title of the application
            html.H1("DPCR Automation", style={"textAlign": "center", "marginTop": "20px"})
        ], width=12)
    ]),
    # Second row for the main content
    dbc.Row([
        dbc.Col([
            # Initial screen for file upload
            html.Div(id="initial-screen", children=[
                # Label for file upload instruction
                html.Label("Please select zipped working directory", style={"marginTop": "20px"}),
                # File upload component
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
                    multiple=True  # Allow multiple files to be uploaded
                ),
                # Div to display uploaded file information
                html.Div(id="output-data-upload", style={"marginTop": "20px"})
            ]),
            # Placeholder for wells selection screen, hidden initially
            html.Div(id="wells-selection-screen", style={"display": "none"})
        ], width=12)
    ]),
    # Store to keep well names across callbacks
    dcc.Store(id="well-names-store")
])

# Register all callbacks from the callbacks module
register_callbacks(app)

# Run the app server
if __name__ == "__main__":
    app.run_server(debug=True)

