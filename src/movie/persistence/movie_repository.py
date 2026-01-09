import sqlite3
import os
from movie.models.movie_model import Movie, Showtime

class MovieRepository:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'movies.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                genre TEXT NOT NULL,
                duration INTEGER NOT NULL,
                release_date TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS showtimes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                FOREIGN KEY(movie_id) REFERENCES movies(id)
            )
        ''')
        
        conn.commit()
        conn.close()


    def add_movie(self, id, title, genre, duration, release_date):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if id is not None:
            cursor.execute(
                'INSERT INTO movies (id, title, genre, duration, release_date) VALUES (?, ?, ?, ?, ?)',
                (id, title, genre, duration, release_date)
            )
            new_id = id
        else:
            cursor.execute(
                'INSERT INTO movies (title, genre, duration, release_date) VALUES (?, ?, ?, ?)',
                (title, genre, duration, release_date)
            )
            new_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return new_id

    def get_movie(self, movie_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Movie(id=row[0], title=row[1], genre=row[2], duration=row[3], release_date=row[4])
        return None

    def get_all_movies(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM movies')
        rows = cursor.fetchall()
        conn.close()
        return [Movie(id=r[0], title=r[1], genre=r[2], duration=r[3], release_date=r[4]) for r in rows]

    def search_movies(self, query):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{query}%',))
        rows = cursor.fetchall()
        conn.close()
        return [Movie(id=r[0], title=r[1], genre=r[2], duration=r[3], release_date=r[4]) for r in rows]

    def update_movie(self, movie_id, title, genre, duration, release_date):
        conn = self._get_connection()
        conn.execute(
            'UPDATE movies SET title = ?, genre = ?, duration = ?, release_date = ? WHERE id = ?',
            (title, genre, duration, release_date, movie_id)
        )
        conn.commit()
        conn.close()

    def delete_movie(self, movie_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM showtimes WHERE movie_id = ?', (movie_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            conn.close()
            return False 
            
        cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0


    def add_showtime(self, id, movie_id, start_time, end_time):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if id is not None:
             cursor.execute(
                'INSERT INTO showtimes (id, movie_id, start_time, end_time) VALUES (?, ?, ?, ?)',
                (id, movie_id, start_time, end_time)
            )
             new_id = id
        else:
            cursor.execute(
                'INSERT INTO showtimes (movie_id, start_time, end_time) VALUES (?, ?, ?)',
                (movie_id, start_time, end_time)
            )
            new_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return new_id

    def get_showtime(self, showtime_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM showtimes WHERE id = ?', (showtime_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Showtime(id=row[0], movie_id=row[1], start_time=row[2], end_time=row[3])
        return None

    def get_all_showtimes(self, movie_id=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        if movie_id:
            cursor.execute('SELECT * FROM showtimes WHERE movie_id = ?', (movie_id,))
        else:
            cursor.execute('SELECT * FROM showtimes')
        rows = cursor.fetchall()
        conn.close()
        return [Showtime(id=r[0], movie_id=r[1], start_time=r[2], end_time=r[3]) for r in rows]

    def update_showtime(self, showtime_id, start_time, end_time):
        conn = self._get_connection()
        conn.execute('UPDATE showtimes SET start_time = ?, end_time = ? WHERE id = ?', (start_time, end_time, showtime_id))
        conn.commit()
        conn.close()

    def delete_showtime(self, showtime_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM showtimes WHERE id = ?', (showtime_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0