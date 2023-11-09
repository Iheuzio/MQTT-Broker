import datetime
import random
import requests
import json
import threading
from dash import Dash, html, dcc, Input, Output, no_update
import dash_daq as daq
from flask import Flask, jsonify, request

server = Flask(__name__)
app = Dash(__name__, server=server)

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
            html.Div(id=f'my-thermometer-{id_suffix}-date'),
            html.Div(id=f'my-thermometer-{id_suffix}-summary')
        ], style={'display': 'flex', 'flex-direction': 'column'})
    ], style={'display': 'flex', 'flex-direction': 'column', 'margin-right': '5%'})

app.layout = html.Div([
    *[
        create_thermometer(str(i))
        for i in range(1, 6)
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
        ], style={'margin-top': '5%'})
    ], style={'margin-top': '5%'})
], style={
    'display': 'flex',
    'flex-direction': 'row',
})

update_lock = threading.Lock()
time = datetime.datetime.now()

@app.callback(
    [
        Output(f'my-thermometer-{i}', 'value') for i in range(1, 6)
    ] + [
        Output(f'my-thermometer-{i}-date', 'children') for i in range(1, 6)
    ] + [
        Output(f'my-thermometer-{i}-summary', 'children') for i in range(1, 6)
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
            url = "http://localhost:5080/WeatherForecast"
            response = requests.get(url)
            response_json = response.json()
        except:
            raise Exception('Could not connect to server')
        
        values = []
        dates = []
        summaries = []
        for i in range(5):
            values.append(response_json[i]['temperatureC'])
            dates.append(response_json[i]['date'])
            summaries.append(response_json[i]['summary'])
        return [value for value in values + dates + summaries]

# MotionDetectionController (should not use route here, must use the controller)
# http://localhost:5081/motiondetection?postal_code=M5S%201A1
@server.route('/motiondetection')
def motion_detection():
    postal_code = request.args.get('postal_code')
    if not postal_code:
        return jsonify({'error': 'Postal code not provided'}), 400
    if postal_code not in ['M9A 1A8', 'M5S 1A1', 'M4W 1A5', 'M6G 1A1', 'M5R 1A6']:
        return jsonify({'error': 'Invalid postal code'}), 400
    detection_type = 'motion' if random.randint(0, 1) == 0 else 'collision'
    detection_value = random.choice([True, False])
    date_time = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    result = {
        'postal_code': postal_code,
        'detection': {'type': detection_type, 'value': detection_value},
        'datetime': date_time
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', threaded=False)
