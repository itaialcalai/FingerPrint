import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from callbacks import register_callbacks

# Create Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Define layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("DPCR Automation", style={"textAlign": "center", "marginTop": "20px"})
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id="initial-screen", children=[
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
            ]),
            html.Div(id="wells-selection-screen", style={"display": "none"})
        ], width=12)
    ])
])

# Register callbacks
register_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)

