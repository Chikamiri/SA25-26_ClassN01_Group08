from datetime import datetime
from movie.persistence.movie_repository import MovieRepository
from booking.persistence.booking_repository import BookingRepository

class MovieService:
    def __init__(self):
        self.movie_repo = MovieRepository()
        self.booking_repo = BookingRepository()

    def add_movie(self, id, title, genre, duration, release_date):
        if duration <= 0:
            raise ValueError("Movie duration must be positive")
        
        if id and self.movie_repo.get_movie(id):
             raise ValueError(f"Movie ID {id} already exists")

        return self.movie_repo.add_movie(id, title, genre, duration, release_date)

    def search_movies(self, keyword, genre):
        results = self.movie_repo.search_movies(keyword, genre)
        return [m.to_dict() for m in results]

    def get_all_movies(self):
        return [m.to_dict() for m in self.movie_repo.get_all_movies()]

    def update_movie(self, movie_id, title, genre, duration, release_date):
        if duration <= 0:
            raise ValueError("Movie duration must be positive")
        success = self.movie_repo.update_movie(movie_id, title, genre, duration, release_date)
        if not success:
            raise ValueError("Movie not found to update")
        return {"message": "Movie updated successfully", "id": movie_id}

    def delete_movie(self, movie_id):
        success = self.movie_repo.delete_movie(movie_id)
        if not success:
            raise ValueError("Movie not found to delete")
        return {"message": "Movie deleted successfully", "id": movie_id}

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

    def add_showtime(self, id, movie_id, start_time, end_time, total_seats):
        movie = self.validate_showtime_duration(movie_id, start_time, end_time)
        
        if total_seats > 64:
            raise ValueError("Maximum seats allowed is 64")
        
        if id and self.movie_repo.get_showtime(id):
             raise ValueError(f"Showtime ID {id} already exists")

        showtime_id = self.movie_repo.add_showtime(id, movie_id, start_time, end_time)
        
        self.booking_repo.create_seats(showtime_id, total_seats)

        return {
            "message": "Showtime and seats created successfully",
            "showtime_id": showtime_id,
            "movie": movie.title,
            "duration_check": "OK"
        }

    def get_all_showtimes(self):
        return [s.to_dict() for s in self.movie_repo.get_all_showtimes()]

    def update_showtime(self, showtime_id, start_time, end_time):
        current_showtime = self.movie_repo.get_showtime(showtime_id)
        if not current_showtime:
            raise ValueError("Showtime not found")

        self.validate_showtime_duration(current_showtime.movie_id, start_time, end_time)
        self.movie_repo.update_showtime(showtime_id, start_time, end_time)
        return {"message": "Showtime updated successfully", "id": showtime_id}

    def delete_showtime(self, showtime_id):
        success = self.movie_repo.delete_showtime(showtime_id)
        if not success:
            raise ValueError("Showtime not found to delete")
        return {"message": "Showtime deleted successfully", "id": showtime_id}