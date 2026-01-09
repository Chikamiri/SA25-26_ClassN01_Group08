import sys
import os
import sqlite3
import requests
import json
import pika
from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BOOKING_SERVICE_URL = os.environ.get("BOOKING_SERVICE_URL", "http://127.0.0.1:5002")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def get_db_connection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_folder = os.path.join(current_dir, 'db')
    db_path = os.path.join(db_folder, 'payments.db')
    os.makedirs(db_folder, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            customer_name TEXT,
            status TEXT DEFAULT 'PAID',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def send_invoice_event(invoice_data):
    try:
        if 'localhost' in RABBITMQ_URL:
             connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
        else:
             params = pika.URLParameters(RABBITMQ_URL)
             connection = pika.BlockingConnection(params)
             
        channel = connection.channel()
        channel.queue_declare(queue='invoice_events', durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key='invoice_events',
            body=json.dumps(invoice_data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        print(f"Event sent to RabbitMQ: {invoice_data}")
    except Exception as e:
        print(f"Error sending event to RabbitMQ: {e}")

@app.route('/api/payments', methods=['POST'])
def create_payment():
    data = request.json
    booking_id = data.get('booking_id')
    amount = data.get('amount')

    if not booking_id or not amount:
        return jsonify({"error": "Missing booking_id or amount"}), 400

    customer_name = "Unknown"
    try:
        response = requests.get(f"{BOOKING_SERVICE_URL}/api/bookings/{booking_id}")
        if response.status_code == 200:
            booking_info = response.json()
            customer_name = booking_info.get('customer_name', 'Unknown')
        else:
            return jsonify({"error": "Booking ID invalid or not found"}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to Booking Service"}), 503

    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "INSERT INTO invoices (booking_id, amount, customer_name, status, created_at) VALUES (?, ?, ?, ?, ?)",
        (booking_id, amount, customer_name, 'PAID', created_at)
    )
    invoice_id = cursor.lastrowid
    conn.commit()
    conn.close()

    event_data = {
        "type": "INVOICE_PRINT",
        "invoice_id": invoice_id,
        "booking_id": booking_id,
        "customer": customer_name,
        "amount": amount,
        "date": created_at
    }
    send_invoice_event(event_data)

    return jsonify({
        "message": "Payment successful",
        "invoice_id": invoice_id,
        "customer": customer_name,
        "amount": amount
    }), 201

@app.route('/api/payments', methods=['GET'])
def get_all_invoices():
    conn = get_db_connection()
    invoices = conn.execute("SELECT * FROM invoices").fetchall()
    conn.close()
    return jsonify([dict(row) for row in invoices]), 200

if __name__ == '__main__':
    print("Payment Service running on port 5003...")
    app.run(debug=True, port=5003)