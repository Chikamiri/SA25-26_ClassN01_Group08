import requests
import json
import pika
import os
from datetime import datetime
from dotenv import load_dotenv
from movie.persistence.movie_repository import MovieRepository

load_dotenv()

class MovieService:
    def __init__(self):
        self.movie_repo = MovieRepository()
        self.BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://127.0.0.1:5002")
        self.RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

    
    def add_movie(self, id, title, genre, duration, release_date):
        if id and self.movie_repo.get_movie(id):
            raise ValueError(f"Movie ID {id} already exists")
            
        return self.movie_repo.add_movie(id, title, genre, duration, release_date)

    def validate_showtime_duration(self, movie_id, start_time_str, end_time_str):
        movie = self.movie_repo.get_movie(movie_id)
        if not movie:
            raise ValueError(f"Movie ID {movie_id} not found")
        fmt = "%Y-%m-%d %H:%M"
        try:
            start = datetime.strptime(start_time_str, fmt)
            end = datetime.strptime(end_time_str, fmt)
        except ValueError:
            raise ValueError("Invalid date format. Use: YYYY-MM-DD HH:MM")
        if start >= end:
            raise ValueError("End time must be after start time")
        diff_minutes = (end - start).total_seconds() / 60
        if diff_minutes > movie.duration:
            raise ValueError(f"Showtime duration ({diff_minutes} mins) exceeds movie duration ({movie.duration} mins)")
        return movie

    def get_all_movies(self):
        return [m.to_dict() for m in self.movie_repo.get_all_movies()]

    def search_movies(self, query):
        return [m.to_dict() for m in self.movie_repo.search_movies(query)]
    
    def update_movie(self, movie_id, title, genre, duration, release_date):
        if not self.movie_repo.get_movie(movie_id):
            raise ValueError("Movie ID not found")
        self.movie_repo.update_movie(movie_id, title, genre, duration, release_date)
        return {"message": "Movie updated", "id": movie_id}

    def delete_movie(self, movie_id):
        success = self.movie_repo.delete_movie(movie_id)
        if not success:
             raise ValueError("Movie ID not found or has existing showtimes")
        return {"message": "Movie deleted", "id": movie_id}

    def get_all_showtimes(self, movie_id=None):
        return [s.to_dict() for s in self.movie_repo.get_all_showtimes(movie_id)]


    def add_showtime(self, id, movie_id, start_time, end_time, total_seats):
        self.validate_showtime_duration(movie_id, start_time, end_time)
        
        if total_seats > 64:
            raise ValueError("Maximum seats allowed is 64")
        
        if id and self.movie_repo.get_showtime(id):
             raise ValueError(f"Showtime ID {id} already exists")

        showtime_id = self.movie_repo.add_showtime(id, movie_id, start_time, end_time)
        
        try:
            requests.post(f"{self.BOOKING_SERVICE_URL}/api/internal/seats", json={
                "showtime_id": showtime_id,
                "total_seats": total_seats
            })
        except Exception as e:
            print(f"Warning: Could not call Booking Service to create seats: {e}")

        return {
            "message": "Showtime created successfully",
            "showtime_id": showtime_id,
            "total_seats": total_seats
        }

    def send_notification_event(self, message_data):
        try:
            if 'localhost' in self.RABBITMQ_URL:
                 params = pika.ConnectionParameters(host='localhost', port=5672)
            else:
                 params = pika.URLParameters(self.RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='notification_events', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key='notification_events',
                body=json.dumps(message_data),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
        except Exception as e:
            print(f"Failed to send notification: {e}")

    def update_showtime(self, showtime_id, start_time, end_time):
        current_showtime = self.movie_repo.get_showtime(showtime_id)
        if not current_showtime:
            raise ValueError("Showtime ID not found")
        
        self.validate_showtime_duration(current_showtime.movie_id, start_time, end_time)
        self.movie_repo.update_showtime(showtime_id, start_time, end_time)
        
        try:
            url = f"{self.BOOKING_SERVICE_URL}/api/bookings/showtime/{showtime_id}/customers"
            response = requests.get(url)
            if response.status_code == 200:
                customers = response.json()
                movie = self.movie_repo.get_movie(current_showtime.movie_id)
                for cust in customers:
                    customer_email = cust.get('email', 'Unknown Email')
                    
                    event_data = {
                        "type": "SHOWTIME_CHANGED",
                        "email": customer_email,
                        "seat": cust['seat_number'],
                        "movie_title": movie.title,
                        "old_time": current_showtime.start_time,
                        "new_time": start_time
                    }
                    self.send_notification_event(event_data)
                print(f"Sent notifications to {len(customers)} customers.")
        except Exception as e:
            print(f"Could not fetch customers: {e}")

        return {"message": "Showtime updated", "id": showtime_id, "new_time": f"{start_time} - {end_time}"}

    def delete_showtime(self, showtime_id):
        success = self.movie_repo.delete_showtime(showtime_id)
        if not success:
            raise ValueError("Showtime not found to delete")
        return {"message": "Showtime deleted", "id": showtime_id}