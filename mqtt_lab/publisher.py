import paho.mqtt.client as mqtt 
import time

broker_hostname = "localhost"
port = 1883 

def on_connect(client, userdata, flags, return_code):
    print("CONNACK received with code %s." % return_code)
    if return_code == 0:
        print("connected")
    else:
        print("could not connect, return code:", return_code)

client = mqtt.Client(client_id="Client1", userdata=None)
client.on_connect = on_connect

# change with your user and password auth
client.username_pw_set(username="user_name", password="password")


client.connect(broker_hostname, port, 60)
#client.loop_forever()
client.loop_start()

topic = "Test"
msg_count = 0

try:
    while msg_count < 100:
        time.sleep(1)
        msg_count += 1
        result = client.publish(topic=topic, payload=msg_count)
        status = result[0]
        if status == 0:
            print("Message "+ str(msg_count) + " is published to topic " + topic)
        else:
            print("Failed to send message to topic " + topic)
finally:
    client.loop_stop()