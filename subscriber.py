import threading
import paho.mqtt.client as mqtt
import time
import json
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, utils, rsa
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from jwt import encode, decode

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

    def __on_connect(self, client, userdata, flags, return_code):
        if return_code == 0:
            print("Subscriber connected")
            client.subscribe("jwt-token")
            client.subscribe("public-keys/*")
            client.subscribe("event/Client1")
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

        elif "public_key" in payload:
            if not self.__verify_signature(payload):
                print("Digital signature verification failed")
                return
            
            # Extract and process the public key
            public_key_data = json.loads(payload)
            print("Received public key:", public_key_data["public_key"])

        elif "message" in payload and "signature" in payload:
            if not self.__verify_signature(payload):
                print("Digital signature verification failed")
                return

            # Extract and process the message
            message_data = json.loads(payload)
            print("Received message:", message_data["message"])

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
            signature = json.loads(payload)["signature"]
            message = json.loads(payload)["message"].encode("utf-8")

            # Replace with your actual public key
            public_key_bytes = b"keys/public.pem"

            public_key = serialization.load_pem_public_key(
                public_key_bytes,
                backend=default_backend()
            )

            
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
                time.sleep(1)
        finally:
            self.__client.loop_stop()

    def get_jwt_token(self):
        # if it is None then generate one
        if self.__jwt_token is None:
            self.__jwt_token  = self.__generate_jwt_token()
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

