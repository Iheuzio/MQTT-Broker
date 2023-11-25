import random
from flask import Flask, request, jsonify
from random import choice
from datetime import datetime

app = Flask(__name__)

_conditions = ["Snowfall", "Rain", "Sunny", "Cloudy"]
_intensities = ["heavy", "medium", "light", "n/a"]
_postalCodes = ["M9A1A8", "M5S1A1", "M4W1A5", "M6G1A1", "M5R1A6"]

@app.route('/weather-forecast/postal-code/<postalCode>', methods=['GET'])
def get_weather_forecast(postalCode):
    if postalCode not in _postalCodes:
        return jsonify("Unknown Postal Code"), 400

    conditions = choice(_conditions)
    if conditions in ["Snowfall", "Rain"]:
        intensity = choice(_intensities[:-1])
    else:
        intensity = _intensities[-1]

    return jsonify({
        "Datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "TemperatureC": choice(range(-40, 40)),
        "Conditions": conditions,
        "Intensity": intensity,
        "PostalCode": postalCode
    })

@app.route('/motiondetection', methods=['GET'])
def motion_detection():
    postal_code = request.args.get('postal_code')
    if not postal_code:
        return jsonify({'error': 'Postal code not provided'}), 400
    if postal_code not in _postalCodes:
        return jsonify({'error': 'Invalid postal code'}), 400
    detection_type = 'motion' if random.randint(0, 1) == 0 else 'collision'
    detection_value = random.choice([True, False])
    date_time = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    result = {
        'postal_code': postal_code,
        'detection': {'type': detection_type, 'value': detection_value},
        'datetime': date_time
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
