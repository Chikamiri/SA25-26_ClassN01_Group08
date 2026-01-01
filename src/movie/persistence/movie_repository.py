import sqlite3
import os
from movie.models.movie_model import Movie

class MovieRepository:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__)) 
        self.db_path = os.path.join(current_dir, '..', 'db', 'movies.db')

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS movies (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            genre TEXT,
                            duration INTEGER NOT NULL,
                            release_date TEXT)""")
            
            conn.execute("""CREATE TABLE IF NOT EXISTS showtimes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            movie_id INTEGER NOT NULL,
                            start_time TEXT NOT NULL)""")

    def add_movie(self, title, genre, duration, release_date):
        with sqlite3.connect(self.db_path) as conn: # Dùng self.db_path
            cursor = conn.cursor()
            sql = "INSERT INTO movies (title, genre, duration, release_date) VALUES (?, ?, ?, ?)"
            cursor.execute(sql, (title, genre, duration, release_date))
            return cursor.lastrowid

    def get_movie(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
            row = cursor.fetchone()
            if row:
                return Movie(id=row[0], title=row[1], genre=row[2], duration=row[3], release_date=row[4])
            return None

    def add_showtime(self, movie_id, start_time):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO showtimes (movie_id, start_time) VALUES (?, ?)", (movie_id, start_time))
            return cursor.lastrowid