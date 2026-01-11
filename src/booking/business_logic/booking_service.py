import pika
import json
import os
import requests
from dotenv import load_dotenv
from booking.persistence.booking_repository import BookingRepository

load_dotenv()

class BookingService:
    def __init__(self):
        self.repo = BookingRepository()
        self.RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
        self.MOVIE_SERVICE_URL = os.getenv('MOVIE_SERVICE_URL', 'http://127.0.0.1:5001')

    def send_order_event(self, event_data):
        try:
            if 'localhost' in self.RABBITMQ_URL:
                 params = pika.ConnectionParameters(host='localhost', port=5672)
            else:
                 params = pika.URLParameters(self.RABBITMQ_URL)
            
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='ticket_events', durable=True)
            
            channel.basic_publish(
                exchange='',
                routing_key='ticket_events',
                body=json.dumps(event_data),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
            print(f"[INFO] RabbitMQ Event Sent: {event_data}")
        except Exception as e:
            print(f"[ERROR] Failed to send RabbitMQ event: {e}")

    def get_movie_title_via_api(self, showtime_id):
        try:
            showtime_res = requests.get(f"{self.MOVIE_SERVICE_URL}/api/showtimes/{showtime_id}")
            if showtime_res.status_code != 200: return "Unknown Movie"
            movie_id = showtime_res.json().get('movie_id')

            movie_res = requests.get(f"{self.MOVIE_SERVICE_URL}/api/movies/{movie_id}")
            if movie_res.status_code != 200: return "Unknown Movie"

            return movie_res.json().get('title', 'Unknown Movie')
        except Exception as e:
            print(f"[WARNING] Could not fetch movie title: {e}")
            return "Unknown Movie (Service Error)"

    def book_ticket(self, showtime_id, seat_number, email):
        status = self.repo.check_seat_availability(showtime_id, seat_number)
        if status is None: raise ValueError("Seat not found")
        if status == 'booked': raise ValueError(f"Seat {seat_number} is already booked")

        booking_id = self.repo.create_booking(showtime_id, seat_number, email)
        
        real_movie_name = self.get_movie_title_via_api(showtime_id)

        event_payload = {
            "type": "OrderPlacedEvent",
            "ticket_id": booking_id,
            "email": email,            
            "movie_name": real_movie_name
        }
        self.send_order_event(event_payload)

        return {
            "message": "Booking successful",
            "ticket_id": booking_id,
            "email": email,
            "movie": real_movie_name
        }

    def get_seats(self, showtime_id): return self.repo.get_seats_by_showtime(showtime_id)
    def get_all_bookings(self): return self.repo.get_all_bookings()
    def get_booking_details(self, booking_id): return self.repo.get_booking_by_id(booking_id)
    def delete_booking(self, booking_id): 
        success = self.repo.delete_booking(booking_id)
        if not success: raise ValueError("Booking ID not found")
        return {"message": "Booking cancelled", "id": booking_id}
    def get_affected_customers(self, showtime_id): return self.repo.get_customers_by_showtime(showtime_id)
    def create_seats(self, showtime_id, total_seats): self.repo.create_seats(showtime_id, total_seats)