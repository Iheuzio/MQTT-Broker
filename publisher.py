import threading
import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime, timedelta
from jwt import encode, decode
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
import base64

class Publisher:
    def __init__(self, private_key, public_key, subscriber):
        self.__broker_hostname = "localhost"
        self.__port = 1883
        self.__private_key = private_key
        self.__message = None
        self.__topic = "event/Client1"
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
        response = requests.get(url, headers=headers).json()
        self.weather_forecast_data = response
        return response

    def fetch_motion_detection(self):
        jwt_token = self.__subscriber.get_jwt_token()
        jwt_token_str = jwt_token.decode("utf-8")
        headers = {'Authorization': 'Bearer ' + jwt_token_str}
        url_motion = "http://localhost:5000/motiondetection?postal_code=M5S1A1"
        response_motion = requests.get(url_motion, headers=headers).json()
        self.motion_detection_data = response_motion
        return response_motion
    
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
        result = self.__client.publish(topic=topic, payload=self.sign_payload(payload))
        status = result.rc

        try:
            if not public_key_sent:
                topic = "public-keys/Client1"
                payload = str(self.__public_key)
            else:
                topic = "event/Client1"
            try:
                self.fetch_motion_detection()
                self.fetch_weather_forecast()
            except Exception as e:
                print(f'Could not connect to the server: {str(e)}')
            # Publish weather forecast data
            weather_forecast_payload = json.dumps(self.weather_forecast_data)
            self.publish_message("weather-forecast", self.sign_payload(weather_forecast_payload))

            # Publish motion detection data
            motion_detection_payload = json.dumps(self.motion_detection_data)
            self.publish_message("motion-detection", self.sign_payload(motion_detection_payload))

        finally:
            print("finally publisher")
            self.__client.loop_stop()

    def publish_traffic_violation(self, timestamp, filename):
        self.__topic = "event/Client1/traffic-violation"
        obj = {
            "type": "Traffic Violation",
            "timestamp": timestamp,
            "filename": filename
        }
        self.__message = obj
        print(f"publishing {self.__message}")

    def publish_collision(self, timestamp, weather):
        self.__topic = "event/Client1/collision"
        obj = {
            "type": "Collision",
            "timestamp": timestamp,
            "weather": weather
        }
        self.__message = obj
        print(f"publishing collision {self.__message}")

    def sign_payload(self, payload):
        # Replace with your actual private key
        private_key_bytes = b"keys/private.pem"

        with open(private_key_bytes, "rb") as key_file:
            private_key_content = key_file.read()


        private_key = serialization.load_pem_private_key(
            private_key_content,
            password=b'password123',  # replace 'your_password' with your actual password
            backend=default_backend()
        )



        signature = private_key.sign(
            payload.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Encode the signature in base64
        signature_b64 = base64.b64encode(signature).decode("utf-8")

        # Include the signature in the payload
        signed_payload = {"message": payload, "signature": signature_b64}
        return json.dumps(signed_payload)

    
    def publish_message(self, topic, payload):
        result = self.__client.publish(topic=topic, payload=payload)
        status = result.rc
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"Message {payload} is published to topic {topic}")
            public_key_sent = True
        else:
            print(f"Failed to send message to topic {topic}")
