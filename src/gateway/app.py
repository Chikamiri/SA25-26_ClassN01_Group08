import sys
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

MOVIE_SERVICE_URL = "http://127.0.0.1:5001"
BOOKING_SERVICE_URL = "http://127.0.0.1:5002"

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
    return forward_request(MOVIE_SERVICE_URL, request.path)

@app.route('/api/showtimes', methods=['GET', 'POST'])
@app.route('/api/showtimes/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def showtime_proxy(path=''):
    return forward_request(MOVIE_SERVICE_URL, request.path)

@app.route('/api/bookings', methods=['GET', 'POST'])
@app.route('/api/bookings/<path:path>', methods=['GET', 'PUT', 'DELETE'])
def booking_proxy(path=''):
    return forward_request(BOOKING_SERVICE_URL, request.path)

if __name__ == '__main__':
    print("🚪 API Gateway running on port 5000...")
    app.run(debug=True, port=5000)