import paho.mqtt.client as mqtt
import json
from jwt import encode, decode
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
import base64

class Publisher:
    """
    The Publisher class is responsible for publishing messages to MQTT topics.

    Attributes:
        __broker_hostname (str): The hostname of the MQTT broker.
        __port (int): The port number of the MQTT broker.
        __private_key (bytes): The private key used for signing payloads.
        __message (dict): The message to be published.
        __public_key (str): The public key associated with the publisher.
        __jwt_token (bytes): The JWT token used for authentication.
        __client (mqtt.Client): The MQTT client instance.

    Methods:
        fetch_weather_forecast: Fetches weather forecast data from an API.
        fetch_motion_detection: Fetches motion detection data from an API.
        __on_connect: Callback function called when the client connects to the broker.
        loop: Starts the MQTT client loop and publishes messages.
        publish_traffic_violation: Publishes a traffic violation event.
        publish_collision: Publishes a collision event.
        sign_payload: Signs the payload using the private key.
        publish_message: Publishes a message to an MQTT topic.
    """

    def __init__(self, private_key, public_key, jwt_token):
        """
        Initializes a new instance of the Publisher class.

        Args:
            private_key (bytes): The private key used for signing payloads.
            public_key (str): The public key associated with the publisher.
            jwt_token (bytes): The JWT token used for authentication.
        """
        self.__broker_hostname = "localhost"
        self.__port = 1883
        self.__private_key = private_key
        self.__message = None
        self.__public_key = public_key
        self.__jwt_token = jwt_token
        self.__client = mqtt.Client(client_id="Client1", userdata=None)
        self.__client.on_connect = self.__on_connect
        self.__client.username_pw_set(username="user_name", password="password")
        self.__client.connect(self.__broker_hostname, self.__port, 60)
        self.weather_forecast_data = self.fetch_weather_forecast()
        self.motion_detection_data = self.fetch_motion_detection()

    def fetch_weather_forecast(self):
        """
        Fetches weather forecast data from an API.

        Returns:
            dict: The weather forecast data.
        """
        jwt_token_str = self.__jwt_token.decode("utf-8")
        headers = {'Authorization': 'Bearer ' + jwt_token_str}
        url = "http://localhost:5000/weather-forecast/postal-code/M5S1A1"
        response = requests.get(url, headers=headers).json()
        self.weather_forecast_data = response
        return response

    def fetch_motion_detection(self):
        """
        Fetches motion detection data from an API.

        Returns:
            dict: The motion detection data.
        """
        jwt_token_str = self.__jwt_token.decode("utf-8")
        headers = {'Authorization': 'Bearer ' + jwt_token_str}
        url_motion = "http://localhost:5000/motiondetection?postal_code=M5S1A1"
        response_motion = requests.get(url_motion, headers=headers).json()
        self.motion_detection_data = response_motion
        return response_motion
    
    def __on_connect(self, client, userdata, flags, return_code):
        """
        Callback function called when the client connects to the broker.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata: The user data associated with the client.
            flags: The flags associated with the connection.
            return_code: The return code indicating the connection status.
        """
        print("CONNACK received with code %s." % return_code)
        if return_code == 0:
            print("Publisher connected")
            if self.__jwt_token:
                topic = "jwt-token"
                result = self.__client.publish(topic=topic, payload=str(self.__jwt_token))
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
        """
        Starts the MQTT client loop and publishes messages.

        Args:
            exit_event: The event used to signal the loop to exit.
            message: The message to be published.
            topic: The MQTT topic to publish the message to.
        """
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
            self.__client.loop_stop()

    def publish_traffic_violation(self, timestamp, filename):
        """
        Publishes a traffic violation event.

        Args:
            timestamp: The timestamp of the event.
            filename: The filename associated with the event.
        """
        self.__topic = "event/Client1/traffic-violation"
        obj = {
            "type": "Traffic Violation",
            "timestamp": timestamp,
            "filename": filename
        }
        self.__message = obj
        print(f"publishing {self.__message}")

    def publish_collision(self, timestamp, weather):
        """
        Publishes a collision event.

        Args:
            timestamp: The timestamp of the event.
            weather: The weather condition associated with the event.
        """
        self.__topic = "event/Client1/collision"
        obj = {
            "type": "Collision",
            "timestamp": timestamp,
            "weather": weather
        }
        self.__message = obj
        print(f"publishing collision {self.__message}")

    def sign_payload(self, payload):
        """
        Signs the payload using the private key.

        Args:
            payload: The payload to be signed.

        Returns:
            str: The signed payload.
        """
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
        """
        Publishes a message to an MQTT topic.

        Args:
            topic: The MQTT topic to publish the message to.
            payload: The payload of the message.
        """
        result = self.__client.publish(topic=topic, payload=payload)
        status = result.rc
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"Message {payload} is published to topic {topic}")
            public_key_sent = True
        else:
            print(f"Failed to send message to topic {topic}")
