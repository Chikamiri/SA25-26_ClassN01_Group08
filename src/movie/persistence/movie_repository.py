import sqlite3
import os
from movie.models.movie_model import Movie, Showtime

class MovieRepository:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, '..', 'db', 'movies.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS movies (
                            id INTEGER PRIMARY KEY, -- Bỏ AUTOINCREMENT để linh hoạt nhập ID
                            title TEXT NOT NULL,
                            genre TEXT,
                            duration INTEGER NOT NULL,
                            release_date TEXT)""")
            
            conn.execute("""CREATE TABLE IF NOT EXISTS showtimes (
                            id INTEGER PRIMARY KEY, -- Bỏ AUTOINCREMENT để linh hoạt nhập ID
                            movie_id INTEGER NOT NULL,
                            start_time TEXT NOT NULL,
                            end_time TEXT NOT NULL)""")

    def add_movie(self, id, title, genre, duration, release_date):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if id is not None:
                sql = "INSERT INTO movies (id, title, genre, duration, release_date) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (id, title, genre, duration, release_date))
                return id
            else:
                sql = "INSERT INTO movies (title, genre, duration, release_date) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (title, genre, duration, release_date))
                return cursor.lastrowid

    def search_movies(self, keyword=None, genre=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM movies WHERE 1=1"
            params = []
            if keyword:
                sql += " AND title LIKE ?"
                params.append(f"%{keyword}%")
            if genre:
                sql += " AND genre LIKE ?"
                params.append(f"%{genre}%")
            
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            return [Movie(*row) for row in rows]

    def get_all_movies(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM movies")
            rows = cursor.fetchall()
            return [Movie(*row) for row in rows]

    def get_movie(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
            row = cursor.fetchone()
            return Movie(*row) if row else None

    def update_movie(self, movie_id, title, genre, duration, release_date):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            sql = "UPDATE movies SET title=?, genre=?, duration=?, release_date=? WHERE id=?"
            cursor.execute(sql, (title, genre, duration, release_date, movie_id))
            return cursor.rowcount > 0

    def delete_movie(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movies WHERE id=?", (movie_id,))
            return cursor.rowcount > 0

    # --- CRUD SHOWTIME ---
    def add_showtime(self, id, movie_id, start_time, end_time):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if id is not None:
                sql = "INSERT INTO showtimes (id, movie_id, start_time, end_time) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (id, movie_id, start_time, end_time))
                return id
            else:
                sql = "INSERT INTO showtimes (movie_id, start_time, end_time) VALUES (?, ?, ?)"
                cursor.execute(sql, (movie_id, start_time, end_time))
                return cursor.lastrowid

    def get_all_showtimes(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM showtimes")
            rows = cursor.fetchall()
            return [Showtime(*row) for row in rows]

    def get_showtime(self, showtime_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM showtimes WHERE id = ?", (showtime_id,))
            row = cursor.fetchone()
            return Showtime(*row) if row else None

    def update_showtime(self, showtime_id, start_time, end_time):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            sql = "UPDATE showtimes SET start_time=?, end_time=? WHERE id=?"
            cursor.execute(sql, (start_time, end_time, showtime_id))
            return cursor.rowcount > 0

    def delete_showtime(self, showtime_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM showtimes WHERE id=?", (showtime_id,))
            return cursor.rowcount > 0