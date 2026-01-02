class Movie:
    def __init__(self, id, title, genre, duration, release_date):
        self.id = id
        self.title = title
        self.genre = genre
        self.duration = duration
        self.release_date = release_date

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "genre": self.genre,
            "duration": self.duration,
            "release_date": self.release_date
        }

class Showtime:
    def __init__(self, id, movie_id, start_time, end_time):
        self.id = id
        self.movie_id = movie_id
        self.start_time = start_time
        self.end_time = end_time
    
    def to_dict(self):
        return {
            "id": self.id,
            "movie_id": self.movie_id,
            "start_time": self.start_time,
            "end_time": self.end_time
        }