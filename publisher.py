import threading
import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime, timedelta
from jwt import encode, decode
import requests

class Publisher:
    def __init__(self, private_key, public_key, subscriber):
        self.__broker_hostname = "localhost"
        self.__port = 1883
        self.__private_key = private_key
        self.__public_key = public_key
        self.__subscriber = subscriber
        self.__client = mqtt.Client(client_id="Client1", userdata=None)
        self.__client.on_connect = self.__on_connect
        self.__client.username_pw_set(username="user_name", password="password")
        self.__client.connect(self.__broker_hostname, self.__port, 60)
        self.weather_forecast_data = self.fetch_weather_forecast()
        self.motion_detection_data = self.fetch_motion_detection()

    def fetch_weather_forecast(self):
        jwt_token = self.__subscriber.get_jwt_token()
        jwt_token_str = jwt_token.decode("utf-8")
        headers = {'Authorization': 'Bearer ' + jwt_token_str}
        url = "http://localhost:5000/weather-forecast/postal-code/M5S1A1"
        response = requests.get(url, headers=headers)
        return response.json()

    def fetch_motion_detection(self):
        jwt_token = self.__subscriber.get_jwt_token()
        jwt_token_str = jwt_token.decode("utf-8")
        headers = {'Authorization': 'Bearer ' + jwt_token_str}
        url_motion = "http://localhost:5000/motiondetection?postal_code=M5S1A1"
        response_motion = requests.get(url_motion, headers=headers)
        return response_motion.json()
    
    def __on_connect(self, client, userdata, flags, return_code):
        print("CONNACK received with code %s." % return_code)
        if return_code == 0:
            print("Publisher connected")
            jwt_token = self.__subscriber.get_jwt_token()
            if jwt_token:
                topic = "jwt-token"
                result = self.__client.publish(topic=topic, payload=str(jwt_token))
                status = result.rc
                if status == mqtt.MQTT_ERR_SUCCESS:
                    print("JWT token is published to topic " + topic)
                else:
                    print("Failed to send JWT token to topic " + topic)
            else:
                print("No JWT token received from the subscriber.")
        else:
            print("Could not connect, return code:", return_code)

    def loop(self, exit_event, message, topic):
        public_key_sent = False
        self.__client.loop_start()
        if exit_event.is_set():
            self.__client.loop_stop()
        payload = message
        result = self.__client.publish(topic=topic, payload=payload)
        status = result.rc

        try:
            if not public_key_sent:
                topic = "public-keys/Client1"
                payload = str(self.__public_key)
            else:
                topic = "event/Client1"

            # Publish weather forecast data
            weather_forecast_payload = json.dumps(self.weather_forecast_data)
            self.publish_message("weather-forecast", weather_forecast_payload)

            # Publish motion detection data
            motion_detection_payload = json.dumps(self.motion_detection_data)
            self.publish_message("motion-detection", motion_detection_payload)

        finally:
            self.__client.loop_stop()
    
    def publish_message(self, topic, payload):
        result = self.__client.publish(topic=topic, payload=payload)
        status = result.rc
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"Message {payload} is published to topic {topic}")
            public_key_sent = True
        else:
            print(f"Failed to send message to topic {topic}")
