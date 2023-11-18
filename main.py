import signal
import threading
from encryption_keys import generate_key_pair, load_keys, sign, verify
from publisher import Publisher
from subscriber import Subscriber
from dashboard import dashboard

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

# code for traffic light


# code for camera

# test msg
message = "testing"

# launch publisher in a thread
publisher = Publisher(private_key, public_key)
publisher_th = threading.Thread(target=publisher.loop, args=[exit_event, message])
publisher_th.start()


# launch dashboard in a thread

def run_dashboard():
    dashboard.run_dashboard()
dashboard_th = threading.Thread(target=run_dashboard)
dashboard_th.start()

# launch subsciber in a thread, update dashboard on message



subscriber = Subscriber()
subscriber_th = threading.Thread(target=subscriber.loop, args=[exit_event])
subscriber_th.start()

# test msg
message = "testing2"

# loop with traffic light, constantly checking the api's
# if conditions are met, trigger publish
# before publish, take picture and include path in the payload

while not exit_event.is_set():
    # check apis here
    pass
