import random
from threading import Thread, Event
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder


movement_detected = Event()
end_program = Event()

class TrafficLight:
  def __init__(self, delay=0.001):
    self.time_to_sleep = delay
  
  def runSimulation(self, movement_detected):
    start_time = time.time()  
    picam2 = Picamera2()
    while True:
      time.sleep(self.time_to_sleep)
      if end_program.is_set():
        return
      if movement_detected.is_set():
        print("Movement detected, car has passed the RED light")
        video_config = picam2.create_video_configuration()
        picam2.configure(video_config)
        encoder = H264Encoder(bitrate=10000000)
        output = "test_video.h264"  
        picam2.start_recording(encoder, output)
        time.sleep(5)
        picam2.stop_recording()
        print("Video has been recorded offence has been captured")
        movement_detected.clear()
        elapsed_time = time.time() - start_time
      else:
        elapsed_time = time.time() - start_time
        print(f"Simulation is running... Traffic in RED, simulation continue... {elapsed_time:.2f} seconds elapsed")
        red_light_thread = Thread(target=self.red_light_interval, args=(start_time,))
        red_light_thread.start()
        red_light_thread.join()
        # random switch 1 or 2 if 1 run green else blue
        if random.randint(1, 2) == 1:
          elapsed_time = time.time() - start_time
          print(f"Simulation is running... Traffic in GREEN, simulation continue... {elapsed_time:.2f} seconds elapsed")
          time.sleep(5) # wait for 5 seconds
        else:
          elapsed_time = time.time() - start_time
          print(f"Simulation is running... Traffic in GREEN, simulation continue... {elapsed_time:.2f} seconds elapsed")
          time.sleep(5) # wait for 5 seconds
        

  def red_light_interval(self, start_time):
    while True:
      if end_program.is_set():
        return
      if time.time() - start_time >= 5:
        return
      if movement_detected.is_set():
        return
      time.sleep(0.1)

class MovementSensor:
  def __init__(self, delay=0.5):
    self.time_to_sleep = delay
  
  def detectMovement(self, movement_detected):
    while True:
      time.sleep(self.time_to_sleep)
      if end_program.is_set():
        return
      else:
        movement_detected.clear()
      movement_detected.set()
  
  def timestamp(self):
    start_time = time.time()
    while True:
      if end_program.is_set():
        return
      elapsed_time = time.time() - start_time
      print(f"Elapsed time: {elapsed_time:.2f} seconds")
      time.sleep(1)

def main():
  end_program.clear()

  trafficLight = TrafficLight(1)
  trafficThread = Thread(target=trafficLight.runSimulation, args=(movement_detected, ))
  
  movementSensor = MovementSensor(2)
  movementSensorThread = Thread(target=movementSensor.detectMovement, args=(movement_detected, ))
  timestampThread = Thread(target=movementSensor.timestamp)

  movementSensorThread.start()
  trafficThread.start()
  timestampThread.start()

  movementSensorThread.join()
  trafficThread.join()
  timestampThread.join()

def destroy():
   print("Remember to also clear the GPIO state...")
   end_program.set()
   print("Finishing Traffic Light simulation...")

if __name__ == '__main__':     # Program entrance
  print ('Program is starting ... ')
  MovementSensor.setup()
  try:
    main()
  except KeyboardInterrupt:  # Press ctrl-c to end the program.    
    destroy()