import sys
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

MOVIE_SERVICE_URL = "http://127.0.0.1:5001"
BOOKING_SERVICE_URL = "http://127.0.0.1:5002"
PAYMENT_SERVICE_URL =  "http://127.0.0.1:5003"


VALID_API_KEY = "BO_CHIKA"


@app.before_request
def check_security():
    client_key = request.headers.get('peko-key')
    
    if client_key != VALID_API_KEY:
        return jsonify({"error": "Unauthorized: Invalid or missing API Key"}), 401

def validate_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False, jsonify({"error": "Authorization token is missing"}), 401
    
    # Simulate token validation
    token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
    if not token or token == "invalid_token": # Replace with actual token validation logic
        return False, jsonify({"error": "Invalid token"}), 401
    
    return True, None, None

def forward_request(service_url, path):
    url = f"{service_url}{path}"
    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            params=request.args,
            cookies=request.cookies,
            allow_redirects=False
        )
        return (response.content, response.status_code, response.headers.items())
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Service is down or unreachable"}), 503


@app.route('/api/movies', methods=['GET', 'POST'])
@app.route('/api/movies/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def movie_proxy(path=''):
    is_valid, response, status_code = validate_token()
    if not is_valid:
        return response, status_code
    return forward_request(MOVIE_SERVICE_URL, request.path)

@app.route('/api/showtimes', methods=['GET', 'POST'])
@app.route('/api/showtimes/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def showtime_proxy(path=''):
    is_valid, response, status_code = validate_token()
    if not is_valid:
        return response, status_code
    return forward_request(MOVIE_SERVICE_URL, request.path)

@app.route('/api/bookings', methods=['GET', 'POST'])
@app.route('/api/bookings/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def booking_proxy(path=''):
    is_valid, response, status_code = validate_token()
    if not is_valid:
        return response, status_code
    return forward_request(BOOKING_SERVICE_URL, request.path)

@app.route('/api/payments', methods=['GET', 'POST'])
@app.route('/api/payments/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def payment_proxy(path=''):
    return forward_request(PAYMENT_SERVICE_URL, request.path)

if __name__ == '__main__':
    print("🚪 API Gateway (Secured) running on port 5000...")
    app.run(debug=True, port=5000)