import paho.mqtt.client as mqtt
import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64

# Replace these values with your actual broker information
broker_address = "your_broker_address"
broker_port = 1883
topic = "your_topic"

# Replace with the path to your PEM file
pem_path = "path_to_your.pem"

# Load the private key for signing
with open(pem_path, "rb") as file:
    private_key = RSA.import_key(file.read())

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe to the topic for public keys
    client.subscribe(topic)

# Callback when a message is received from the broker
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload)
        signature_b64 = payload.get("signature", "")
        data = payload.get("data", "")

        # Verify the signature
        if verify_signature(data, signature_b64):
            print("Signature verified. Processing the message:", data)
            # Your logic to process the received data goes here
        else:
            print("Signature verification failed. Discarding the message.")
    except Exception as e:
        print(f"Error processing message: {e}")

# Function to sign the data
def sign_data(data):
    h = SHA256.new(data.encode("utf-8"))
    signature = pkcs1_15.new(private_key).sign(h)
    return base64.b64encode(signature).decode("utf-8")

# Function to verify the signature
def verify_signature(data, signature_b64):
    try:
        signature = base64.b64decode(signature_b64)
        h = SHA256.new(data.encode("utf-8"))
        pkcs1_15.new(private_key).verify(h, signature)
        return True
    except (ValueError, TypeError, pkcs1_15.VerificationError):
        return False

# Create an MQTT client
client = mqtt.Client()

# Set the callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, broker_port, 60)

# Publish the first message with the public key
public_key = private_key.publickey().export_key().decode("utf-8")
first_message = {
    "public_key": public_key,
    "signature": sign_data(public_key),
}
client.publish(topic, json.dumps(first_message))

# Start the MQTT client loop
client.loop_start()

# Keep the client running
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Disconnecting...")
    # Disconnect on keyboard interrupt
    client.disconnect()
