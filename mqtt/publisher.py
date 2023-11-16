import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

broker_hostname = "localhost"
port = 1899  # Set the port to 1899

motion_var = False  # Simulate motion detection

def on_connect(client, userdata, flags, return_code):
    print("CONNACK received with code %s." % return_code)
    if return_code == 0:
        print("Connected")
    else:
        print("Could not connect, return code:", return_code)

client = mqtt.Client(client_id="Client1", userdata=None)

# Change with your user and password auth
client.username_pw_set(username="user1", password="password1")

client.on_connect = on_connect

client.connect(broker_hostname, port, 60)
client.loop_start()

topic = "motion_event"

try:
    while True:
        time.sleep(1)

        # Simulate motion detection
        motion_var = not motion_var

        if motion_var:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            message = {
                "motion_door": True,
                "timestamp": timestamp,
                "picture": "url_to_image.png",  # URL to the picture (optional)
            }
            payload = json.dumps(message)

            result = client.publish(topic=topic, payload=payload)
            status = result.rc
            if status == mqtt.MQTT_ERR_SUCCESS:
                print(f"Message published to topic '{topic}': {payload}")
            else:
                print(f"Failed to send message to topic '{topic}'")

except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
