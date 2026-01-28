import sys
import os
import requests
from flask import Flask, request, jsonify, Response
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MOVIE_SERVICE_URL = os.getenv('MOVIE_SERVICE_URL', 'http://127.0.0.1:5001')
BOOKING_SERVICE_URL = os.getenv('BOOKING_SERVICE_URL', 'http://127.0.0.1:5002')
PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://127.0.0.1:5003')
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://127.0.0.1:5004')
VALID_API_KEY = os.getenv('API_KEY_VALUE', 'BO_CHIKA')
API_KEY_NAME = os.getenv('API_KEY_NAME', 'peko-key')

@app.before_request
def check_api_key():
    if request.method == 'OPTIONS': return
    client_key = request.headers.get(API_KEY_NAME)
    if client_key != VALID_API_KEY:
        return jsonify({"error": f"Missing or Invalid Header: {API_KEY_NAME}"}), 401

def validate_and_forward(service_url, path, required_role=None):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Missing Authorization Token"}), 401
    
    try:
        token_parts = auth_header.split(" ")
        if len(token_parts) != 2 or token_parts[0] != "Bearer":
            return jsonify({"error": "Invalid Token Format. Use 'Bearer <token>'"}), 401
        
        token = token_parts[1]
        verify_resp = requests.get(f"{USER_SERVICE_URL}/api/auth/verify", params={'token': token})
        
        if verify_resp.status_code != 200:
            return jsonify({"error": "Invalid or Expired Token"}), 401
            
        user_info = verify_resp.json() 
        user_email = user_info['email']
        user_role = user_info['role']

        if required_role and user_role != required_role:
             return jsonify({"error": "Forbidden: Access Denied"}), 403

        new_headers = {key: value for (key, value) in request.headers if key != 'Host'}
        new_headers['X-User-Email'] = user_email 
        new_headers['X-User-Role'] = user_role

        url = f"{service_url}{path}"
        
        resp = requests.request(
            method=request.method,
            url=url,
            headers=new_headers,
            data=request.get_data(),
            params=request.args
        )
        return Response(resp.content, resp.status_code, dict(resp.headers))

    except Exception as e:
        return jsonify({"error": f"Gateway Error: {str(e)}"}), 500

@app.route('/api/auth/<path:path>', methods=['POST'])
def auth_proxy(path):
    url = f"{USER_SERVICE_URL}/api/auth/{path}"
    try:
        resp = requests.post(url, json=request.json)
        return Response(resp.content, resp.status_code, dict(resp.headers))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/movies', methods=['GET', 'POST'])
def handle_movies_list():
    if request.method == 'POST':
        return validate_and_forward(MOVIE_SERVICE_URL, request.path, required_role='admin')
    return validate_and_forward(MOVIE_SERVICE_URL, request.path)

@app.route('/api/movies/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def handle_movie_detail(path):
    if request.method in ['PUT', 'DELETE']:
        return validate_and_forward(MOVIE_SERVICE_URL, request.path, required_role='admin')
    return validate_and_forward(MOVIE_SERVICE_URL, request.path)

@app.route('/api/showtimes', methods=['GET', 'POST'])
def handle_showtimes_list():
    if request.method == 'POST':
        return validate_and_forward(MOVIE_SERVICE_URL, request.path, required_role='admin')
    return validate_and_forward(MOVIE_SERVICE_URL, request.path)

@app.route('/api/showtimes/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def handle_showtime_detail(path):
    if request.method in ['PUT', 'DELETE']:
        return validate_and_forward(MOVIE_SERVICE_URL, request.path, required_role='admin')
    return validate_and_forward(MOVIE_SERVICE_URL, request.path)

@app.route('/api/bookings', methods=['GET', 'POST'])
def handle_bookings():
    return validate_and_forward(BOOKING_SERVICE_URL, request.path)

@app.route('/api/bookings/<path:path>', methods=['GET', 'DELETE'])
def handle_booking_detail(path):
    return validate_and_forward(BOOKING_SERVICE_URL, request.path)

@app.route('/api/payments', methods=['POST'])
def handle_payments():
    return validate_and_forward(PAYMENT_SERVICE_URL, request.path)

if __name__ == '__main__':
    print("API Gateway running on port 5000...")
    app.run(debug=True, port=5000)