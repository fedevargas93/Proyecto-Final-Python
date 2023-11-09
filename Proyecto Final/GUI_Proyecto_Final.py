import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas_ta as ta

app = Dash()

app.layout = html.Div([
    html.H1(id="count-up", children="0"),  # Changed "title" to "children"
    dcc.Graph(id="candles"),
    dcc.Interval(id="interval", interval=2000),
])

@app.callback(
    Output("count-up", "children"),  # Fixed the Output parameter
    Input("interval", "n_intervals")
)
def update_figure(n_intervals):
    return str(n_intervals)

if __name__ == '__main__':
    app.run_server(debug=True)
