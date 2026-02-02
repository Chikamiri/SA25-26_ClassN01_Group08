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
        self.RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
        self.RABBITMQ_URL = os.getenv("RABBITMQ_URL", f"amqp://guest:guest@{self.RABBITMQ_HOST}:5672/")

    def send_ticket_email(self, booking_id, email, seat_number, movie_title):
        try:
            if self.RABBITMQ_HOST != 'localhost':
                 params = pika.ConnectionParameters(host=self.RABBITMQ_HOST, port=5672)
            elif 'localhost' in self.RABBITMQ_URL:
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

    def create_seats(self, showtime_id, rows_count, seats_per_row):
        self.booking_repo.create_seats_realistic(showtime_id, rows_count, seats_per_row)

    def get_seats(self, showtime_id):
        # We need to get room info from Movie Service to initialize if needed
        try:
            resp = requests.get(f"{self.MOVIE_SERVICE_URL}/api/showtimes/{showtime_id}")
            if resp.status_code == 200:
                showtime = resp.json()
                room_id = showtime.get('room_id')
                if room_id:
                    room_resp = requests.get(f"{self.MOVIE_SERVICE_URL}/api/rooms/{room_id}")
                    if room_resp.status_code == 200:
                        room = room_resp.json()
                        # Call get_seats_by_showtime with room info for lazy init
                        return self.booking_repo.get_seats_by_showtime_realistic(
                            showtime_id, 
                            room['rows'], 
                            room['seats_per_row']
                        )
        except Exception as e:
            print(f"Error fetching room info for seats: {e}")

        return self.booking_repo.get_seats_by_showtime(showtime_id)

    def get_all_bookings(self):
        return self.booking_repo.get_all_bookings()

    def get_my_bookings(self, email):
        return self.booking_repo.get_bookings_by_customer(email)

    def get_booking_details(self, booking_id):
        return self.booking_repo.get_booking(booking_id)

    def delete_booking(self, booking_id):
        return self.booking_repo.delete_booking(booking_id)

    def get_affected_customers(self, showtime_id):
        return self.booking_repo.get_affected_customers(showtime_id)