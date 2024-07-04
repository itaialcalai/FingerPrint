import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("DPCR Automation", style={"textAlign": "center", "marginTop": "20px"})
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Label("Please select zipped data working dir", style={"marginTop": "20px"}),
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
        ], width=12)
    ])
])

@app.callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified")
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            html.Ul([html.Li(f"{name}") for name in list_of_names])
        ]
        return children

if __name__ == "__main__":
    app.run_server(debug=True)
