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
                'margin-bottom': '5%' if id_suffix != '1' else '0'
            }
        ),
        html.Div([
            html.Div(id=f'my-thermometer-{id_suffix}-datetime'),
            html.Div(id=f'my-thermometer-{id_suffix}-conditions')
        ], style={'display': 'flex', 'flex-direction': 'column'})
    ], style={'display': 'flex', 'flex-direction': 'column', 'margin-right': '5%'})

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
], style={
    'display': 'flex',
    'flex-direction': 'row',
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

        values.append(response_json['temperatureC'])
        dates.append(response_json['datetime'])
        conditions.append(response_json['conditions'])

        return [value for value in values + dates + conditions]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=False)
