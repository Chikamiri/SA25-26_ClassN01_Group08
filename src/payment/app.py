import sys
import os
import requests
import pika
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://127.0.0.1:5002")
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

def send_invoice_event(invoice_data):
    try:
        if 'localhost' in RABBITMQ_URL:
             params = pika.ConnectionParameters(host='localhost', port=5672)
        else:
             params = pika.URLParameters(RABBITMQ_URL)
        
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        channel.queue_declare(queue='invoice_events', durable=True)
        
        message = {
            "type": "INVOICE_PRINT",
            "customer": invoice_data['customer'],
            "amount": invoice_data['amount'],
            "booking_id": invoice_data['booking_id'],
            "date": invoice_data['date']
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='invoice_events',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        print(f"[RabbitMQ] Sent invoice event for Booking #{invoice_data['booking_id']}")
    except Exception as e:
        print(f"[ERROR] Failed to send RabbitMQ event: {e}")

@app.route('/api/payments', methods=['POST'])
def process_payment():
    data = request.json
    booking_id = data.get('booking_id')
    
    if not booking_id:
        return jsonify({"error": "Missing booking_id"}), 400
    
    try:
        resp = requests.get(f"{BOOKING_SERVICE_URL}/api/bookings/{booking_id}")
        
        if resp.status_code == 404:
            return jsonify({"error": "Booking not found"}), 404
        if resp.status_code != 200:
            return jsonify({"error": "Cannot verify booking details"}), 500
        
        booking_info = resp.json()
        
        amount = booking_info.get('amount')
        email = booking_info.get('customer_email')
        
        if not amount or not email:
            return jsonify({"error": "Invalid booking data (missing amount or email)"}), 400

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Booking Service is unreachable"}), 503
    except Exception as e:
        return jsonify({"error": f"Internal Error: {str(e)}"}), 500

    print(f"💰 Processing payment of {amount} VND for Booking #{booking_id} (User: {email})")

    invoice_data = {
        "customer": email,
        "amount": amount,
        "booking_id": booking_id,
        "date": "2026-01-13" 
    }
    
    send_invoice_event(invoice_data)
    
    print("\n----------------------------------------")
    print("[INFO] PAYMENT SUCCESSFUL")
    print(f"   Booking:  #{booking_id}")
    print(f"   To:       {email}")
    print(f"   Amount:   {amount} VND")
    print("----------------------------------------\n")

    return jsonify({
        "message": "Payment successful",
        "amount_paid": amount,
        "booking_id": booking_id,
        "status": "PAID"
    }), 201

if __name__ == '__main__':
    print("Payment Service running on port 5003...")
    app.run(debug=True, port=5003)