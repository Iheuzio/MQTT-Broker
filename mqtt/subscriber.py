import paho.mqtt.client as mqtt
import json
from datetime import datetime

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("Connected")
        client.subscribe("motion_event")
    else:
        print("Could not connect, return code:", return_code)

def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    data = json.loads(payload)

    timestamp = data["timestamp"]
    picture_url = data.get("picture", "No picture available")  # Optional picture URL

    with open("motion_events.txt", "a") as file:
        message = f"{timestamp} new event detected in {message.topic} : movement in room : {picture_url}\n"
        file.write(message)

broker_hostname = "localhost"
port = 1899

client = mqtt.Client("Subscriber")
# Change with your user and password auth
client.username_pw_set(username="user1", password="password1")
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_hostname, port)
client.loop_start()

try:
    while True:
        pass

except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
