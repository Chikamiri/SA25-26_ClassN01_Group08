from movie.persistence.movie_repository import MovieRepository
from booking.persistence.booking_repository import BookingRepository

class MovieService:
    def __init__(self):
        self.movie_repo = MovieRepository()
        self.booking_repo = BookingRepository()

    def create_movie(self, title, genre, duration, release_date):
        if duration <= 0:
            raise ValueError("Invalid time")
        return self.movie_repo.add_movie(title, genre, duration, release_date)

    def create_showtime_with_seats(self, movie_id, start_time, total_seats):
        if total_seats > 36:
            raise ValueError("Invalid seats number")

        movie = self.movie_repo.get_movie(movie_id)
        if not movie:
            raise ValueError(f"Invalid movie id {movie_id}")

        # 3. Tạo suất chiếu (movies.db)
        showtime_id = self.movie_repo.add_showtime(movie_id, start_time)

        # 4. Tự động sinh ghế (booking.db)
        self.booking_repo.create_seats(showtime_id, total_seats)

        return {
            "message": "Successful",
            "showtime_id": showtime_id,
            "movie": movie.title,
            "seats_created": total_seats
        }