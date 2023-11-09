import datetime
import requests
import json
import threading
from dash import Dash, html, dcc, Input, Output, no_update
import dash_daq as daq

app = Dash(__name__)

def create_thermometer(id_suffix):
    return html.Div([
        daq.Thermometer(
            id=f'my-thermometer-{id_suffix}',
            value=0,
            min=-40,
            max=60,
            label='Temperature',
            showCurrentValue=True,
            units='C',
            style={
                'display': 'inline-block',
                'marginBottom': '5%' if id_suffix != '1' else '0'
            }
        ),
        html.Div([
            html.Div(id=f'my-thermometer-{id_suffix}-datetime'),
            html.Div(id=f'my-thermometer-{id_suffix}-conditions'),
            html.Div(id=f'my-thermometer-{id_suffix}-intensities')
        ], style={'display': 'flex', 'flexDirection': 'column'})
    ], style={'display': 'flex', 'flexDirection': 'column', 'marginRight': '5%'})

app.layout = html.Div([
    *[
        create_thermometer(str(i))
        for i in range(1, 2)
    ],
    dcc.Interval(
        id='interval-component',
        interval=5 * 1000,  # in milliseconds
        n_intervals=0
    ),
    html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div([
            dcc.Link('Motion Detection', href='http://localhost:5081/motiondetection?postal_code=M5S%201A1')
        ], style={'marginTop': '5%'})
    ], style={'marginTop': '5%'})
], style={
    'display': 'flex',
    'flexDirection': 'row',
})

update_lock = threading.Lock()
time = datetime.datetime.now()

@app.callback(
    [
        Output(f'my-thermometer-{i}', 'value') for i in range(1, 2)
    ] + [
        Output(f'my-thermometer-{i}-datetime', 'children') for i in range(1, 2)
    ] + [
        Output(f'my-thermometer-{i}-conditions', 'children') for i in range(1, 2)
    ] + [
        Output(f'my-thermometer-{i}-intensities', 'children') for i in range(1, 2)
    ],
    Input('interval-component', 'n_intervals')
)
def update_thermometer(n):
    
    # check if 5 seconds have passed
    global time
    if (datetime.datetime.now() - time).total_seconds() < 5:
        return no_update
    
    with update_lock:
        try:
            url = "http://localhost:5226/weather-forecast/postal-code/M9A1A8"
            response = requests.get(url)
            response_json = response.json()
            # print(response_json)
        except:
            raise Exception('Could not connect to server')
        
        values = []
        dates = []
        conditions = []
        intensities = []

        values.append(response_json['temperatureC'])
        dates.append(response_json['datetime'])
        conditions.append(response_json['conditions'])
        intensities.append(response_json['intensity'])
        
        return [value for value in values + dates + conditions + intensities]

if __name__ == '__main__':
    app.run(debug=True, host='localhost', threaded=False)
