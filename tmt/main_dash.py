import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px


historical_price = pd.read_csv('data/historical_price.csv', index_col = 0)

app = dash.Dash(__name__)
server = app.server
asset_names = historical_price.columns

app.layout = html.Div([
    html.Div([dcc.Dropdown(id='group-select', options=[{'label': i, 'value': i} for i in asset_names], multi=True)]),
    dcc.Graph('shot-dist-graph', config={'displayModeBar': False})
    ])

@app.callback(
    Output('shot-dist-graph', 'figure'),
    [Input('group-select', 'value')]
)
def update_graph(asset_name):
    return px.scatter(historical_price, y=asset_name, x=historical_price.index)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)