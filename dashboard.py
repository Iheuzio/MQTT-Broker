import datetime
import random
import requests
import json
import threading
from dash import Dash, html, dcc, Input, Output, no_update
import dash_daq as daq

class Dashboard:
    def __init__(self, Subscriber):
        self.app = None
        self.setup_layout()
        self.subscriber = Subscriber
        self.time = datetime.datetime.now()
        
    def create_thermometer(self, id_suffix):
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
    
    def setup_layout(self):
        self.app = Dash(__name__)
        self.app.layout = html.Div([
            *[
                self.create_thermometer(str(i))
                for i in range(1, 2)
            ],
            html.Div(id='motion-detection'),
            dcc.Interval(
                id='interval-component',
                interval=5 * 1000,  # in milliseconds
                n_intervals=0
            ),
           
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
        })

        @self.app.callback(
            [
                Output(f'my-thermometer-{i}', 'value') for i in range(1, 2)
            ] + [
                Output(f'my-thermometer-{i}-datetime', 'children') for i in range(1, 2)
            ] + [
                Output(f'my-thermometer-{i}-conditions', 'children') for i in range(1, 2)
            ] + [
                Output(f'my-thermometer-{i}-intensities', 'children') for i in range(1, 2)
            ] + [
                Output('motion-detection', 'children')
            ],
            Input('interval-component', 'n_intervals')
        )
        def update_thermometer(n):
            # check if 5 seconds have passed
            if (datetime.datetime.now() - self.time).total_seconds() < 5:
                return no_update

            self.time = datetime.datetime.now()  # Update the time

            try:
## Get the JWT token from the subscriber instance
                ## Get the JWT token from the subscriber instance
                jwt_token = self.subscriber.get_jwt_token()
                jwt_token_str = jwt_token.decode("utf-8")
                headers = {'Authorization': 'Bearer ' + jwt_token_str}
                url = "http://localhost:5000/weather-forecast/postal-code/M5S1A1"
                response = requests.get(url, headers=headers)
                response_json = response.json()
                print(response_json)
                
                url_motion = "http://localhost:5000/motiondetection?postal_code=M5S1A1"
                response_motion = requests.get(url_motion, headers=headers)
                response_motion_json = response_motion.json()
                print(response_motion_json)
            except Exception as e:
                raise Exception(f'Could not connect to the server: {str(e)}')

            values = []
            dates = []
            conditions = []
            intensities = []
            motiondetection = []
            try:
                values.append(response_json['TemperatureC'])  # Use 'TemperatureC' here
                dates.append(response_json['Datetime'])  # Use 'Datetime' here
                conditions.append(response_json['Conditions'])  # Use 'Conditions' here
                intensities.append(response_json['Intensity'])  # Use 'Intensity' here
                
                # Extract motion detection details
                motion_detection_data = response_motion_json.get('detection', {})
                motion_detection_type = motion_detection_data.get('type', '')
                motion_detection_value = motion_detection_data.get('value', False)
                motion_detection_datetime = response_motion_json.get('datetime', '')
                motion_detection_postal_code = response_motion_json.get('postal_code', '')

                # Format motion detection details
                motion_detection_str = f"Datetime: {str(motion_detection_datetime)}, Type: {str(motion_detection_type)}, Value: {str(motion_detection_value)}, Postal Code: {str(motion_detection_postal_code)}"

                motiondetection.append(html.P(motion_detection_str))
            except KeyError as e:
                # Handle the case where the key is not present in the response_json
                print(f"KeyError: {str(e)}")
                return no_update

            return [value for value in values + dates + conditions + intensities + motiondetection]

    def run_dashboard(self):
        self.app.run_server(debug=False, host='localhost', threaded=False)
        print("Dashboard running on http://localhost:8050/")
