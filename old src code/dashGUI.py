import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from handlers import handle_plot1, handle_plot2, handle_plot3, handle_plot4, handle_plot5
from helper_functions import create_well_name_dict, default_well_matrix

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Button("Select zipped files", id="select-zip-button", color="primary", style={"width": "100%"}),
            html.Div(id="well-selection", style={"display": "none"}),
            html.Div([
                dbc.Button(f"Plot{i}", id=f"plot{i}-button", color="secondary", style={"width": "100%", "marginTop": "10px"}, disabled=True) 
                for i in range(1, 6)
            ]),
            dbc.Button("Exit", id="exit-button", color="danger", style={"width": "100%", "marginTop": "10px"})
        ], width=2),
        dbc.Col([
            html.Div(id="screen-content", style={"padding": "20px"})
        ], width=10)
    ])
])

@app.callback(
    Output("well-selection", "style"),
    Output("screen-content", "children"),
    Output({"type": "plot-button", "index": dash.ALL}, "disabled"),
    Input("select-zip-button", "n_clicks"),
    State("screen-content", "children")
)
def handle_select_zip(n_clicks, screen_content):
    if n_clicks:
        return {"display": "block"}, html.Div("Initialization Complete\nChoose an Action", style={"fontSize": 24}), [False]*5
    return {"display": "none"}, screen_content, [True]*5

@app.callback(
    Output("screen-content", "children"),
    Input({"type": "plot-button", "index": dash.ALL}, "n_clicks"),
    State("screen-content", "children")
)
def handle_plot_button(n_clicks, screen_content):
    ctx = dash.callback_context
    if not ctx.triggered:
        return screen_content
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    plot_number = int(button_id.split("-")[0].replace("plot", ""))

    well_names = create_well_name_dict(default_well_matrix())

    if plot_number == 1:
        return handle_plot1(screen_content, well_names)
    elif plot_number == 2:
        return handle_plot2(screen_content, well_names)
    elif plot_number == 3:
        return handle_plot3(screen_content, well_names)
    elif plot_number == 4:
        return handle_plot4(screen_content, well_names)
    elif plot_number == 5:
        return handle_plot5(screen_content, well_names)

@app.callback(
    Output("screen-content", "children"),
    Input("exit-button", "n_clicks")
)
def handle_exit(n_clicks):
    if n_clicks:
        return "Application Closed"

if __name__ == "__main__":
    app.run_server(debug=True)
