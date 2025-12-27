class Movie:
    def __init__(self, movie_id, title, genre, duration, release_date):
        self.id = movie_id
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
