import paho.mqtt.client as mqtt 
import time

class Publisher:
    def __init__(self, private_key, public_key):
        self.__broker_hostname = "localhost"
        self.__port = 1883
        self.__private_key = private_key
        self.__public_key = public_key
        self.__client = mqtt.Client(client_id="Client1", userdata=None)
        self.__client.on_connect = self.__on_connect
        # change with your user and password auth
        self.__client.username_pw_set(username="user_name", password="password")
        self.__client.connect(self.__broker_hostname, self.__port, 60)
   

    def __on_connect(self, client, userdata, flags, return_code):
        print("CONNACK received with code %s." % return_code)
        if return_code == 0:
            print("connected")
        else:
            print("could not connect, return code:", return_code)

    #client.loop_forever()

    def loop(self):
        self.__client.loop_start()
        topic = "public-keys/Client1"
        try:
            result = self.__client.publish(topic=topic, payload=self.__public_key)
            status = result[0]
            if status == 0:
                print("Message "+ str(self.__public_key) + " is published to topic " + topic)
            else:
                print("Failed to send message to topic " + topic)
        finally:
            self.__client.loop_stop()


    