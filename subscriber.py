import paho.mqtt.client as mqtt
import time

class Subscriber:
    def __init__(self):
        self.__broker_hostname = "localhost"
        self.__port = 1883
        self.__client = mqtt.Client(client_id="Client2", userdata=None)
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message
        # change with your user and password auth
        self.__client.username_pw_set(username="user_name2", password="password2")
        self.__client.connect(self.__broker_hostname, self.__port, 60)

    def __on_connect(self, client, userdata, flags, return_code):
        if return_code == 0:
            print("subsciber connected")
            client.subscribe("public-keys/#")
            client.subscribe("event/#")
        else:
            print("could not connect, return code:", return_code)

    def __on_message(self, client, userdata, message):
        # if the message is other client's public key, save it to .pem file
        # if it's collision event, update the dashboard
        print("Received message: " ,str(message.payload.decode("utf-8")))

    def loop(self, exit_event):
        self.__client.loop_start()
        if exit_event.is_set():
                self.__client.loop_stop()
        try:
            
            time.sleep(10)
        finally:
            print("finally subscriber")
            self.__client.loop_stop()

