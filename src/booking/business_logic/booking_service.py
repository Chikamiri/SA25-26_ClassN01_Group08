import os
import requests
import json
import pika
from booking.persistence.booking_repository import BookingRepository
from dotenv import load_dotenv

load_dotenv()

class BookingService:
    def __init__(self):
        self.booking_repo = BookingRepository()
        self.MOVIE_SERVICE_URL = os.getenv("MOVIE_SERVICE_URL", "http://127.0.0.1:5001")
        self.RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

    def send_ticket_email(self, booking_id, email, seat_number, movie_title):
        try:
            if 'localhost' in self.RABBITMQ_URL:
                 params = pika.ConnectionParameters('localhost')
            else:
                 params = pika.URLParameters(self.RABBITMQ_URL)
            
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='ticket_events', durable=True)
            
            message = {
                "type": "OrderPlacedEvent",
                "ticket_id": booking_id,
                "email": email,
                "seat": seat_number,
                "movie_name": movie_title  
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='ticket_events',
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
            print(f"[RabbitMQ] Sent ticket event for Booking #{booking_id}")
        except Exception as e:
            print(f"[ERROR] RabbitMQ Error: {e}")

    def book_ticket(self, showtime_id, seat_number, email):
        if not self.booking_repo.is_seat_available(showtime_id, seat_number):
            raise ValueError(f"Seat {seat_number} is not available")

        price = 50000             
        movie_title = "Unknown"   
        
        try:
            resp = requests.get(f"{self.MOVIE_SERVICE_URL}/api/showtimes/{showtime_id}")
            if resp.status_code != 200:
                raise ValueError("Showtime not found")
            
            showtime_info = resp.json()
            price = showtime_info.get('price', 50000)
            movie_id = showtime_info.get('movie_id')

            if movie_id:
                movie_resp = requests.get(f"{self.MOVIE_SERVICE_URL}/api/movies/{movie_id}")
                if movie_resp.status_code == 200:
                    movie_title = movie_resp.json().get('title', "Unknown Movie")

        except requests.exceptions.ConnectionError:
            print("Warning: Cannot connect to Movie Service to verify details. Using defaults.")

        booking_id = self.booking_repo.create_booking(showtime_id, seat_number, email, price)
        
        self.send_ticket_email(booking_id, email, seat_number, movie_title)

        return {
            "message": "Booking successful", 
            "booking_id": booking_id, 
            "price": price, 
            "movie": movie_title
        }

    
    def cancel_all_bookings_for_showtime(self, showtime_id):
        return self.booking_repo.delete_all_bookings_by_showtime(showtime_id)

    def create_seats(self, showtime_id, total_seats):
        self.booking_repo.create_seats(showtime_id, total_seats)

    def get_all_bookings(self):
        return self.booking_repo.get_all_bookings()

    def get_booking_details(self, booking_id):
        return self.booking_repo.get_booking(booking_id)

    def delete_booking(self, booking_id):
        return self.booking_repo.delete_booking(booking_id)

    def get_affected_customers(self, showtime_id):
        return self.booking_repo.get_affected_customers(showtime_id)