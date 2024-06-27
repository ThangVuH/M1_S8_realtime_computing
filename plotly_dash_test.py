import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import datetime
import random

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000,  # in milliseconds
            n_intervals=0
        )
    ]
)

@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    data = {
        'time': datetime.datetime.now(),
        'value': random.random()
    }
    # Create the graph with subplots
    fig = go.Figure(data=[
        go.Scatter(
            x=[data['time']],
            y=[data['value']],
            mode='lines+markers'
        )
    ])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
