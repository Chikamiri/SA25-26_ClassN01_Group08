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

    def process_refund_and_cancel(self, showtime_id, reason):
        """
        Gọi Booking Service để hủy vé hàng loạt và gửi mail hoàn tiền.
        """
        try:
            url = f"{self.BOOKING_SERVICE_URL}/api/internal/bookings/cancel_by_showtime/{showtime_id}"
            response = requests.delete(url)
            
            if response.status_code == 200:
                refund_list = response.json() 
                
                for item in refund_list:
                    event_data = {
                        "type": "REFUND_NOTIFICATION",
                        "email": item['email'],
                        "amount": item['amount'],
                        "reason": reason,
                        "seat": item['seat']
                    }
                    self.send_notification_event(event_data)
                
                return len(refund_list)
            else:
                print(f"Booking Service returned error: {response.text}")
                return 0
        except Exception as e:
            print(f"Error processing refund: {e}")
            return 0

    def add_movie(self, id, title, genre, duration, release_date):
        if id and self.movie_repo.get_movie(id):
            raise ValueError(f"Movie ID {id} already exists")
        new_id = self.movie_repo.add_movie(id, title, genre, duration, release_date)
        return {"message": "Movie created", "id": new_id}

    def get_all_movies(self):
        movies = self.movie_repo.get_all_movies()
        return [m.to_dict() for m in movies]
    
    def search_movies(self, query):
        movies = self.movie_repo.search_movies(query)
        return [m.to_dict() for m in movies]
    
    def get_movie_by_id(self, movie_id):
        movie = self.movie_repo.get_movie(movie_id)
        return movie.to_dict() if movie else None

    def update_movie(self, movie_id, title, genre, duration, release_date):
        if not self.movie_repo.get_movie(movie_id):
            raise ValueError("Movie ID not found")
        self.movie_repo.update_movie(movie_id, title, genre, duration, release_date)
        return {"message": "Movie updated", "id": movie_id}

    def delete_movie(self, movie_id):
        if not self.movie_repo.get_movie(movie_id):
             raise ValueError(f"Movie ID {movie_id} not found")
        showtimes = self.movie_repo.get_all_showtimes(movie_id)
        total_refunded = 0
        for st in showtimes:
            count = self.process_refund_and_cancel(st.id, reason=f"Movie '{movie_id}' deleted by Cinema")
            total_refunded += count
        self.movie_repo.delete_showtimes_by_movie_id(movie_id)
        success = self.movie_repo.delete_movie(movie_id)
        if not success:
            raise ValueError("Failed to delete movie record (Database Error)")
        return {
            "message": f"Movie deleted. Removed {len(showtimes)} showtimes. Refunded {total_refunded} bookings.",
            "id": movie_id
        }
    
    def get_all_showtimes(self, movie_id=None):
        showtimes = self.movie_repo.get_all_showtimes(movie_id)
        return [s.to_dict() for s in showtimes]
    
    def get_showtime(self, showtime_id):
        st = self.movie_repo.get_showtime(showtime_id)
        return st.to_dict() if st else None

    def add_showtime(self, id, movie_id, start_time, end_time, total_seats, price):
        self.validate_showtime_duration(movie_id, start_time, end_time)
        
        if total_seats > 64:
            raise ValueError("Maximum seats allowed is 64")
        
        if id and self.movie_repo.get_showtime(id):
             raise ValueError(f"Showtime ID {id} already exists")

        new_id = self.movie_repo.add_showtime(id, movie_id, start_time, end_time, price)
        
        try:
            requests.post(f"{self.BOOKING_SERVICE_URL}/api/internal/seats", json={
                "showtime_id": new_id,
                "total_seats": total_seats
            })
        except Exception as e:
            print(f"Warning: Could not call Booking Service: {e}")

        return {"message": "Showtime created", "id": new_id, "price": price}

    def update_showtime(self, showtime_id, start_time, end_time, price):
        current_showtime = self.movie_repo.get_showtime(showtime_id)
        if not current_showtime:
            raise ValueError("Showtime ID not found")
        
        self.validate_showtime_duration(current_showtime.movie_id, start_time, end_time)
        
        old_price = current_showtime.price
        new_price = price if price is not None else old_price
        
        is_price_changed = (new_price != old_price)
        
        self.movie_repo.update_showtime(showtime_id, start_time, end_time, new_price)
        
        if is_price_changed:
            count = self.process_refund_and_cancel(showtime_id, reason="Showtime price updated")
            return {"message": f"Updated. Price changed: {count} bookings refunded.", "id": showtime_id}
        

        try:
            url = f"{self.BOOKING_SERVICE_URL}/api/bookings/showtime/{showtime_id}/customers"
            response = requests.get(url)
            if response.status_code == 200:
                customers = response.json()
                movie = self.movie_repo.get_movie(current_showtime.movie_id)
                for cust in customers:
                    event_data = {
                        "type": "SHOWTIME_CHANGED",
                        "email": cust.get('email', 'Unknown'),
                        "seat": cust['seat_number'],
                        "movie_title": movie.title,
                        "old_time": current_showtime.start_time,
                        "new_time": start_time
                    }
                    self.send_notification_event(event_data)
        except Exception as e:
            print(f"Could not notify change: {e}")

        return {"message": "Showtime updated", "id": showtime_id}

    def delete_showtime(self, showtime_id):
        count = self.process_refund_and_cancel(showtime_id, reason="Showtime cancelled by Cinema")
        
        success = self.movie_repo.delete_showtime(showtime_id)
        if not success:
            raise ValueError("Showtime not found")
            
        return {"message": f"Deleted. {count} bookings refunded.", "id": showtime_id}