import threading
import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime, timedelta
from jwt import encode, decode

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

    def loop(self, exit_event, message):
        public_key_sent = False
        self.__client.loop_start()
        if exit_event.is_set():
            self.__client.loop_stop()
        payload = message

        try:
            if not public_key_sent:
                topic = "public-keys/Client1"
                payload = str(self.__public_key)
            else:
                topic = "event/Client1"
            result = self.__client.publish(topic=topic, payload=payload)
            status = result[0]
            if status == 0:
                print("Message "+ str(payload) + " is published to topic " + topic)
                public_key_sent = True
            else:
                print("Failed to send message to topic " + topic)
        finally:
            self.__client.loop_stop()
