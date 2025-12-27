from movie.persistence.movie_repository import MovieRepository

class MovieService:
    def __init__(self):
        self.repo = MovieRepository()

    def create_movie(self, title, genre, duration, release_date):
        if not title:
            raise ValueError("Title is required")
        if duration <= 0:
            raise ValueError("Duration must be positive")
        return self.repo.save(title, genre, duration, release_date)

    def get_movie_details(self, movie_id):
        movie = self.repo.find_by_id(movie_id)
        if not movie:
            raise ValueError(f"Movie with ID {movie_id} not found")
        return movie

    def get_all_movies(self):
        return self.repo.find_all()
