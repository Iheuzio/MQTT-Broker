import signal
import threading
import time
from encryption_keys import generate_key_pair, load_keys, sign, verify
from publisher import Publisher
from subscriber import Subscriber
from dashboard import Dashboard
from Light import Light
from Camera import Camera

global light, camera
light = Light()
camera = Camera()

exit_event = threading.Event()
def signal_handler(signum, frame):
    exit_event.set()
signal.signal(signal.SIGINT, signal_handler)

password = b"password123"
# generate and store key pair in ./keys directory
generate_key_pair(password)
# load private and public keys
private_key, public_key = load_keys(password)
# test
# message = b"hello wrld"
# signature = sign(message, private_key)
# print(verify(signature, message, public_key))


# test msg
message = "testing"

# launch subsciber in a thread, update dashboard on message

subscriber = Subscriber()
subscriber_th = threading.Thread(target=subscriber.loop, args=[exit_event])
subscriber_th.start()

# launch publisher in a thread
publisher = Publisher(private_key, public_key)
publisher_th = threading.Thread(target=publisher.loop, args=[exit_event, message])
publisher_th.start()

# launch dashboard in a thread

def run_dashboard():
    dashboard_instance = Dashboard(subscriber)
    dashboard_instance.run_dashboard()
dashboard_th = threading.Thread(target=run_dashboard)
dashboard_th.start()

# test msg
message = "testing2"

# loop with traffic light, constantly checking the api's
# if conditions are met, trigger publish
# before publish, take picture and include path in the payload

## The loop method creates the threads for the light and camera.
## loop then checks for the conditions needed before starting each thread.
def loop():
    light_th = threading.Thread(target=light.loop, args=[exit_event])
    light_th.start()
    while not exit_event.is_set():
        # GET from APIs here
        if light.is_red(): # and movement (from API)
            print("redlight + movement")
            # camera thread will handle taking video, saving to file and publishing
            camera_th = threading.Thread(target=camera.take_picture, args=[publisher])
            camera_th.start()
            time.sleep(3)
loop()