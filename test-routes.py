import unittest
from subscriber import Subscriber as Subscriber
import json
from datetime import datetime
import requests


class TestFlaskAPI(unittest.TestCase):
  def setUp(self):
    self.subscriber = Subscriber()
    self.jwt_token = self.subscriber.get_jwt_token()
    self.jwt_token_str = self.jwt_token.decode("utf-8")
    self.headers = {'Authorization': 'Bearer ' + self.jwt_token_str}
    self.urls = ["http://localhost:5000/weather-forecast/postal-code/M5S1A1", "http://localhost:5000/motiondetection?postal_code=M5S1A1"]

  def test_get_weather_forecast_success(self):
    response = requests.get(self.urls[0], headers=self.headers)
    data = json.loads(response.text)
    self.assertEqual(response.status_code, 200)
    self.assertTrue('Datetime' in data)
    self.assertTrue('TemperatureC' in data)
    self.assertTrue('Conditions' in data)
    self.assertTrue('Intensity' in data)
    self.assertTrue('PostalCode' in data)
    
  def test_get_weather_forecast_invalid_token(self):
    self.headers = {'Authorization': 'invalid ' + self.jwt_token_str + "invalid"}
    response = requests.get(self.urls[0], headers=self.headers)
    data = json.loads(response.text)
    self.assertEqual(response.status_code, 401)
    self.assertTrue('error' in data)
    self.assertEqual(data['error'], "Invalid token")
    
  def test_motion_detection_success(self):
    response = requests.get(self.urls[1], headers=self.headers)
    data = json.loads(response.text)
    self.assertEqual(response.status_code, 200)
    self.assertTrue('postal_code' in data)
    self.assertTrue('detection' in data)
    self.assertTrue('datetime' in data)
    self.assertTrue('type' in data['detection'])
    self.assertTrue('value' in data['detection'])
    
  def test_motion_detection_invalid_token(self):
    self.headers = {'Authorization': 'invalid ' + self.jwt_token_str + "invalid"}
    response = requests.get(self.urls[1], headers=self.headers)
    data = json.loads(response.text)
    self.assertEqual(response.status_code, 401)
    self.assertTrue('error' in data)
    self.assertEqual(data['error'], "Invalid token")

if __name__ == '__main__':
  unittest.main()
