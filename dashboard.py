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
            ], style={'display': 'flex', 'flexDirection': 'column'})
        ], style={'display': 'flex', 'flexDirection': 'column', 'marginRight': '5%'})
    
    def setup_layout(self):
        self.app = Dash(__name__)
        self.app.layout = html.Div([
            *[
                self.create_thermometer(str(i))
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
                    dcc.Link('Motion Detection', href='http://localhost:5000/motiondetection?postal_code=M5S1A1')
                ], style={'marginTop': '5%'}),
            ], style={'marginTop': '5%'})
        ], style={
            'display': 'flex',
            'flexDirection': 'row',
        })

        time = [datetime.datetime.now()]
        @self.app.callback(
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
        def update_thermometer(n, time=time):
            # check if 5 seconds have passed
            if (datetime.datetime.now() - time[0]).total_seconds() < 5:
                return no_update

            time[0] = datetime.datetime.now()  # Update the time

            try:
                # Get the JWT token from the subscriber instance
                jwt_token = self.subscriber.get_jwt_token()  # Replace with the actual method in your Subscriber class
                # Convert the JWT token to a string
                jwt_token_str = json.dumps(jwt_token)

                headers = {'Authorization': jwt_token_str}
                url = "http://localhost:5000/weather-forecast/postal-code/M5S1A1"
                response = requests.get(url, headers=headers)
                response_json = response.json()
                # print(response_json)
            except Exception as e:
                raise Exception(f'Could not connect to the server: {str(e)}')

            values = []
            dates = []
            conditions = []
            intensities = []

            values.append(response_json['TemperatureC'])  # Use 'TemperatureC' here
            dates.append(response_json['Datetime'])  # Use 'Datetime' here
            conditions.append(response_json['Conditions'])  # Use 'Conditions' here
            intensities.append(response_json['Intensity'])  # Use 'Intensity' here

            return [value for value in values + dates + conditions + intensities]

    def run_dashboard(self):
        self.app.run_server(debug=False, host='localhost', threaded=False)
        print("Dashboard running on http://localhost:8050/")
