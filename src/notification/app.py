import sys
import os
import pika
import json
import time
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

def connect_rabbitmq():
    while True:
        try:
            print("[INFO] Connecting to RabbitMQ...")
            if 'localhost' in RABBITMQ_URL:
                 params = pika.ConnectionParameters(host='localhost', port=5672)
            else:
                 params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            print("[INFO] Successfully connected to RabbitMQ!")
            return connection
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        event_type = data.get('type', 'UNKNOWN')

        if event_type == 'OrderPlacedEvent':
            ticket_id = data.get('ticket_id')
            email = data.get('email')
            movie_name = data.get('movie_name')

            print("\n----------------------------------------")
            print("[MOCK EMAIL SERVICE] Sending Ticket Confirmation")
            print(f"   Subject: Booking Confirmed!")
            print(f"   To:      {email}")
            print(f"   Ticket:  #{ticket_id}")
            print(f"   Movie:   {movie_name}")
            print("   Status:  SENT")
            print("----------------------------------------\n")
        
        else:
            print(f"[INFO] Ignored event type: {event_type}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[ERROR] Error processing message: {e}")

def start_consumer():
    connection = connect_rabbitmq()
    channel = connection.channel()

    channel.queue_declare(queue='ticket_events', durable=True)
    channel.basic_consume(queue='ticket_events', on_message_callback=callback)

    print("[INFO] Notification Service is running & listening on 'ticket_events'...")
    channel.start_consuming()

if __name__ == '__main__':
    try:
        start_consumer()
    except KeyboardInterrupt:
        print("Stopping Notification Service...")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)