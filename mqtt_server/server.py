import paho.mqtt.client as mqtt
import jwt
import time

# Replace with your secret key for JWT
SECRET_KEY = "secretkey"

# Dictionary to store public keys received from clients
public_keys = {}

# Callback when a client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

# Callback when a message is published
def on_publish(client, userdata, mid):
    print(f"Message {mid} published")

# Callback when a message is received from a client
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8")

    if topic == "public_key":
        # Store the public key in the dictionary
        public_keys[msg.info["id"]] = payload
    else:
        # Verify the JWT signature using the public key
        try:
            decoded_token = jwt.decode(payload, public_keys[msg.info["id"]], algorithms=["HS256"])
            print(f"Received message: {decoded_token}")
        except jwt.ExpiredSignatureError:
            print("Token has expired")
        except jwt.InvalidTokenError:
            print("Invalid token")

# Set up the MQTT broker
broker = mqtt.Client()
broker.on_connect = on_connect
broker.on_publish = on_publish
broker.on_message = on_message

# Set up authentication for the broker
broker.authenticate = lambda client, username, password, userdata: True

# Start the MQTT broker on the specified port
broker.username_pw_set(username="user1", password="password1")

broker.connect("localhost", 1899)

try:
    # Run the broker loop
    broker.loop_forever()
except KeyboardInterrupt:
    # Handle Ctrl+C to gracefully stop the broker
    print("Broker stopped")
