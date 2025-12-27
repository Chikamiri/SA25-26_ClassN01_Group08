from movie.models.movie_model import Movie

# In-memory storage for now
movie_db = {}
next_id = 1

class MovieRepository:
    def save(self, title, genre, duration, release_date):
        global next_id
        movie_id = str(next_id)
        new_movie = Movie(movie_id, title, genre, duration, release_date)
        movie_db[movie_id] = new_movie
        next_id += 1
        return new_movie

    def find_by_id(self, movie_id):
        return movie_db.get(movie_id)

    def find_all(self):
        return list(movie_db.values())
