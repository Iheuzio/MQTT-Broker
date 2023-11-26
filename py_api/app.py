import json
import random
from flask import Flask, request, jsonify
from random import choice
from datetime import datetime
import jwt
from functools import wraps
from jwt import encode, decode
from datetime import datetime

app = Flask(__name__)

SECRET_KEY = "your_secret_key"

_conditions = ["Snowfall", "Rain", "Sunny", "Cloudy"]
_intensities = ["heavy", "medium", "light", "n/a"]
_postalCodes = ["M9A1A8", "M5S1A1", "M4W1A5", "M6G1A1", "M5R1A6"]


def authorize_jwt_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        print("Received token:", token)  # Added for troubleshooting
        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Remove 'Bearer ' from the token
            token = token[7:]
            # Decode the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # Check if the token has expired
            if 'exp' in payload and datetime.now().timestamp() > payload['exp']:
                return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": "Invalid token", "exception": str(e)}), 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/weather-forecast/postal-code/<postalCode>', methods=['GET'])
@authorize_jwt_token
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
@authorize_jwt_token
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
    app.run(debug=False)
