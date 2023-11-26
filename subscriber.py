import threading
import paho.mqtt.client as mqtt
import time
import json
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils, rsa
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from jwt import encode, decode
from flask import Flask, request, jsonify

class Subscriber:
    def __init__(self):
        self.__broker_hostname = "localhost"
        self.__port = 1883
        self.__client = mqtt.Client(client_id="Client2", userdata=None)
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        self.__client.username_pw_set(username="user_name2", password="password2")
        self.__client.connect(self.__broker_hostname, self.__port, 60)
        self.__jwt_token = None

        self.__weather_forecast_data = None
        self.__motion_detection_data = None

    def __on_connect(self, client, userdata, flags, return_code):
        if return_code == 0:
            print("Subscriber connected")
            client.subscribe("jwt-token")
            client.subscribe("weather-forecast")
            client.subscribe("motion-detection")
        else:
            print("Could not connect, return code:", return_code)

    def __on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")

        if message.topic == "jwt-token":
            if not self.__validate_jwt_token(payload):
                print("JWT token is expired or invalid")
            else:
                print("JWT token is valid")
                self.__jwt_token = payload

        elif message.topic == "weather-forecast":
            if not self.__verify_signature(payload):
                print("Digital signature verification failed for weather-forecast")
                return

            self.__weather_forecast_data = json.loads(payload)
            print("Received weather forecast:", self.__weather_forecast_data)

        elif message.topic == "motion-detection":
            if not self.__verify_signature(payload):
                print("Digital signature verification failed for motion-detection")
                return

            self.__motion_detection_data = json.loads(payload)
            print("Received motion detection:", self.__motion_detection_data)

    def __validate_jwt_token(self, token):
        try:
            decoded_token = decode(token, verify=False)
            return decoded_token["exp"] > datetime.utcnow()
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def __verify_signature(self, payload):
        try:
            # Replace with your actual public key
            public_key_bytes = b"keys/public.pem"

            public_key = serialization.load_pem_public_key(
                public_key_bytes,
                backend=default_backend()
            )

            signature = json.loads(payload)["signature"]
            message = json.loads(payload)["message"].encode("utf-8")

            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                utils.Prehashed(hashes.SHA256())
            )

            return True
        except Exception as e:
            print("Signature verification error:", e)
            return False

    def loop(self, exit_event):
        self.__client.loop_start()
        if exit_event.is_set():
            self.__client.loop_stop()
        try:
            while not exit_event.is_set():
                weather_forecast_data = self.__weather_forecast_data
                motion_detection_data = self.__motion_detection_data

                # Update dashboard with the latest data
                if weather_forecast_data:
                    return weather_forecast_data

                if motion_detection_data:
                    return motion_detection_data

                time.sleep(1)
        finally:
            self.__client.loop_stop()

    def get_jwt_token(self):
        # if it is None then generate one
        if self.__jwt_token is None:
            self.__jwt_token = self.__generate_jwt_token()
            self.__jwt_token = self.__jwt_token.encode("utf-8")
        return self.__jwt_token

    def __generate_jwt_token(self):
        # Generate JWT token with expiration time
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        payload = {
            "exp": expiration_time,
            "iat": datetime.utcnow(),
        }
        token = encode(payload, "your_secret_key", algorithm="HS256")
        return token

    def get_weather_forecast_message(self):
        if self.__weather_forecast_data is None:
            # return 401 error
            return "No data", 401
        return self.__weather_forecast_data
    
    def get_motion_detection_message(self):
        if self.__motion_detection_data is None:
            # return 401 error
            return "No data", 401
        return self.__motion_detection_data
    