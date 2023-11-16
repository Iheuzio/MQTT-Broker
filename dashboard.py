import datetime
import json
import threading
import requests
from dash import Dash, html, dcc, Input, Output, no_update
import dash_daq as daq
import paho.mqtt.client as mqtt
import jwt

app = Dash(__name__)

# MQTT Configurations
MQTT_BROKER = "localhost"
MQTT_TOPIC = "your_topic"
MQTT_PORT = 1899  # Adjust according to your broker configuration

# JWT Secret Key
JWT_SECRET = "secretkey"

# MQTT Client Setup
mqtt_client = mqtt.Client()

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the team topic
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()}")

# Set MQTT callbacks
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to the MQTT broker
mqtt_client.username_pw_set(username="user1", password="password1")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

def get_json_motion():
    try:
        jwt_token = get_jwt_token()
        print(f"Generated JWT token: {jwt_token}")
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get('http://localhost:5081/motiondetection?postal_code=M5S%201A1', headers=headers)
        
        # Check the status code of the response
        if response.status_code != 200:
            print(f"Error in HTTP request. Status Code: {response.status_code}, Response: {response.text}")
            return None

        data = response.json()
        
        # Publish data to MQTT with JWT token
        payload = {'data': data, 'jwt_token': jwt_token}
        mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
        return data
    except Exception as e:
        print(f'Error in get_json_motion: {e}')
        return "None"


def get_jwt_token():
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    jwt_token = jwt.encode({'exp': expiration_time}, JWT_SECRET, algorithm='HS256')
    return jwt_token

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
        ], style={'display': 'flex', 'flexDirection': 'column'}),
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
    html.Div(id='motion-data')
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
    ] + [
        Output('motion-data', 'children')
    ],
    Input('interval-component', 'n_intervals')
)
def update_thermometer(n):
    global time
    if (datetime.datetime.now() - time).total_seconds() < 5:
        return no_update
    
    with update_lock:
        try:
            
            url = "http://localhost:5080/weather-forecast/postal-code/M5S%201A1"
            response_json = requests.get(url).json()
            motion_data = json.dumps(get_json_motion())
            # expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            # jwt_token = jwt.encode({'exp': expiration_time}, JWT_SECRET, algorithm='HS256')
            # print(f"Generated JWT token: {jwt_token}")
            # headers = {'Authorization': f'Bearer {jwt_token}'}
            # response = requests.get(url, headers=headers)
            # response_json = response.json()
            
            # # Publish data to MQTT with JWT token
            # payload = {'data': response_json, 'jwt_token': jwt_token}
            # mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
        except Exception as e:
            print(f'Error: {e}')
        
        values = [response_json['temperatureC']]
        dates = [response_json['datetime']]
        conditions = [response_json['conditions']]
        intensities = [response_json['intensity']]
        
        
        return [value for value in values + dates + conditions + intensities] + [motion_data]

# MQTT Loop
mqtt_client.loop_start()

if __name__ == '__main__':
    app.run(debug=True, host='localhost', threaded=False)
