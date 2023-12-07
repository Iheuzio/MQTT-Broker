import time
import datetime
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

## The Camera class contains code that is used to record and save a video 
## using the camera. Camera also creates and saves a text file containing information about the video
class Camera:
    def __init__(self):
        self.__camera = Picamera2() # camera is initialized
        video_config = self.__camera.create_video_configuration() # Video configuration is created 
        self.__camera.configure(video_config)
        self.__encoder = H264Encoder(bitrate=10000000) # The video uses the H264 encoding

    ## The take_picture method uses the camera to record a 3 second video
    ## and save it to a directory. Likewise, it also populates a the
    ## traffic_log.txt with information about the video.
    def take_picture(self, publisher):
        print ("Taking Video")
        timestamp = datetime.datetime.now() .strftime ("%Y-%m-%d-%H.%M.%S") 
        filename = datetime.datetime.now() .strftime ("./video/%Y-%m-%d-%H.%M.%S.h264")

        # starts recording 3 second video
        self.__camera.start_recording(self.__encoder, filename)
        print ("A car passed in red at  :  %s" % filename)
        
        # Information is written to a file named traffic_log.txt, if the file does exist, it is created
        f = open("traffic_log.txt", "a")
        f.write(f"A car passed in red at {timestamp}; check the record of the traffic offense in {filename}\n")
        f.close

        # sleep 3 seconds for recording 
        time.sleep(5)

        # starts recording 3 second video
        self.__camera.stop_recording()
        if self.__encoder.running:
            self.__encoder.stop()

        # print path to where file was saved
        print ("File Saved in :  %s" % filename)

        # publish
        publisher.publish_traffic_violation(timestamp, filename)

