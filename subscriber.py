import base64
import paho.mqtt.client as mqtt
import time
import json
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from jwt import encode, decode

class Subscriber:
    """_summary_
    The Subscriber class is responsible for subscribing to MQTT topics and receiving messages.
    Attributes:
        __broker_hostname (str): The hostname of the MQTT broker.
        __port (int): The port number of the MQTT broker.
        __client (mqtt.Client): The MQTT client instance.
        __jwt_token (bytes): The JWT token used for authentication.
        __weather_forecast_data (dict): The weather forecast data received from the publisher.
        __motion_detection_data (dict): The motion detection data received from the publisher.
    Methods:
        __on_connect: Callback function called when the client connects to the broker.
        __on_message: Callback function called when the client receives a message from the broker.
        loop: Starts the MQTT client loop and receives messages.
        get_jwt_token: Returns the JWT token.
        __generate_jwt_token: Generates a new JWT token.
        __validate_jwt_token: Validates the JWT token.
        __verify_signature: Verifies the digital signature.
        get_weather_forecast_message: Returns the weather forecast message.
        get_motion_detection_message: Returns the motion detection message.
    """
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

    """_summary_
      This function is called when the client connects to the broker.
      Args:
          client (mqtt.Client): The MQTT client instance.
          userdata (Any): User data of any type.
          flags (dict): Response flags sent by the broker.
          return_code (int): The connection result.
      Returns:
          None
    """
    def __on_connect(self, client, userdata, flags, return_code):
        if return_code == 0:
            print("subsciber connected")
            client.subscribe("public-keys/#")
            client.subscribe("event/#")
            client.subscribe("jwt-token")
            client.subscribe("weather-forecast")
            client.subscribe("motion-detection")
        else:
            print("Could not connect, return code:", return_code)
    """_summary_
      This function is called when the client receives a message from the broker.
      Args:
          client (mqtt.Client): The MQTT client instance.
          userdata (Any): User data of any type.
          message (mqtt.MQTTMessage): An instance of MQTTMessage.
      Returns:
          None
    """
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

    """_summary_
      This function is used to validate the JWT token.
      Args:
          token (str): The JWT token. 
      Returns:
          bool: True if the token is valid, False otherwise.
    """
    def __validate_jwt_token(self, token):
        try:
            decoded_token = decode(token, verify=False)
            return decoded_token["exp"] > datetime.utcnow()
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    """_summary_
      This function is used to verify the digital signature.
      Args:
          payload (str): The payload containing the digital signature and the message.
      Returns:
          bool: True if the signature is valid, False otherwise.
    """
    def __verify_signature(self, payload):
        try:
            # Load the public key content from the file
            with open("keys/public.pem", "rb") as key_file:
                public_key_bytes = key_file.read()

            public_key = serialization.load_pem_public_key(
                public_key_bytes,
                backend=default_backend()
            )

            signature = json.loads(payload)["signature"]
            message = json.loads(payload)["message"].encode("utf-8")

            public_key.verify(
                base64.b64decode(signature),
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return True
        except Exception as e:
            print("Signature verification error:", e)
            return False

    """_summary_
      This function starts the MQTT client loop and receives messages.
      Args:
          exit_event (threading.Event): The event used to stop the loop.
      Returns:
          None
    """
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
    """_summary_
      This function returns the JWT token.
      Args:
          None
      Returns:
          bytes: The JWT token.
    """
    def get_jwt_token(self):
        # if it is None then generate one
        if self.__jwt_token is None:
            self.__jwt_token = self.__generate_jwt_token()
            self.__jwt_token = self.__jwt_token.encode("utf-8")
        return self.__jwt_token
    
    """_summary_
      This function generates a new JWT token.
      Args:
          None
      Returns:
          bytes: The JWT token.
    """
    def __generate_jwt_token(self):
        # Generate JWT token with expiration time
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        payload = {
            "exp": expiration_time,
            "iat": datetime.utcnow(),
        }
        token = encode(payload, "your_secret_key", algorithm="HS256")
        return token

    """_summary_
      This function returns the weather forecast message.
      Args:
          None
      Returns:
          dict: The weather forecast message.
    """
    def get_weather_forecast_message(self):
        if self.__weather_forecast_data is None:
            # return 401 error
            return "No data", 401
        return self.__weather_forecast_data
    
    """_summary_
      This function returns the motion detection message.
      Args:
          None
      Returns:
          dict: The motion detection message.
    """
    def get_motion_detection_message(self):
        if self.__motion_detection_data is None:
            # return 401 error
            return "No data", 401
        return self.__motion_detection_data
    