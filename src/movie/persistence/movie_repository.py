import sqlite3
import os
from movie.models.movie_model import Movie, Showtime

class MovieRepository:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, '..', 'db', 'movies.db')
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
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rows INTEGER NOT NULL,
                seats_per_row INTEGER NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS showtimes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                room_id INTEGER,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                price INTEGER DEFAULT 50000,
                FOREIGN KEY(movie_id) REFERENCES movies(id),
                FOREIGN KEY(room_id) REFERENCES rooms(id)
            )
        ''')

        # Migration for room_id
        cursor.execute("PRAGMA table_info(showtimes)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'room_id' not in columns:
            cursor.execute("ALTER TABLE showtimes ADD COLUMN room_id INTEGER")
        
        conn.commit()
        conn.close()

    # --- Room Methods ---
    def get_all_rooms(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rooms')
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "name": r[1], "rows": r[2], "seats_per_row": r[3]} for r in rows]

    def get_room(self, room_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rooms WHERE id = ?', (room_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"id": row[0], "name": row[1], "rows": row[2], "seats_per_row": row[3]}
        return None

    # --- Movie Methods ---

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
        
        cursor.execute('DELETE FROM movies WHERE id = ?', (movie_id,))
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        return rows_affected > 0

    # --- Showtime Methods ---

    def add_showtime(self, id, movie_id, start_time, end_time, price, room_id=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if id is not None:
             cursor.execute(
                'INSERT INTO showtimes (id, movie_id, start_time, end_time, price, room_id) VALUES (?, ?, ?, ?, ?, ?)',
                (id, movie_id, start_time, end_time, price, room_id)
            )
             new_id = id
        else:
            cursor.execute(
                'INSERT INTO showtimes (movie_id, start_time, end_time, price, room_id) VALUES (?, ?, ?, ?, ?)',
                (movie_id, start_time, end_time, price, room_id)
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
            # Map row based on new schema
            # id, movie_id, room_id, start_time, end_time, price
            # But PRAGMA table_info says room_id was added later if migrated
            # To be safe, let's use dictionary-like access if we were using sqlite3.Row
            # but here we use indexes. 
            # Original: id[0], movie_id[1], start_time[2], end_time[3], price[4]
            # New: id[0], movie_id[1], room_id[2], start_time[3], end_time[4], price[5]
            
            # Let's check column names to be absolutely sure or just assume the new order
            # If we just added the column, it's usually at the end unless recreated.
            # In our _init_db we define it at index 2.
            
            # Re-fetch with row_factory for safety
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            row = cursor.execute('SELECT * FROM showtimes WHERE id = ?', (showtime_id,)).fetchone()
            conn.close()
            
            if row:
                return Showtime(
                    id=row['id'], 
                    movie_id=row['movie_id'], 
                    start_time=row['start_time'], 
                    end_time=row['end_time'], 
                    price=row['price'],
                    room_id=row['room_id']
                )
        return None

    def get_all_showtimes(self, movie_id=None):
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if movie_id:
            rows = cursor.execute('SELECT * FROM showtimes WHERE movie_id = ?', (movie_id,)).fetchall()
        else:
            rows = cursor.execute('SELECT * FROM showtimes').fetchall()
        conn.close()
        
        return [Showtime(
            id=r['id'], 
            movie_id=r['movie_id'], 
            start_time=r['start_time'], 
            end_time=r['end_time'], 
            price=r['price'],
            room_id=r['room_id']
        ) for r in rows]

    def update_showtime(self, showtime_id, start_time, end_time, price, room_id=None):
        conn = self._get_connection()
        conn.execute(
            'UPDATE showtimes SET start_time = ?, end_time = ?, price = ?, room_id = ? WHERE id = ?', 
            (start_time, end_time, price, room_id, showtime_id)
        )
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

    def delete_showtimes_by_movie_id(self, movie_id):
        conn = self._get_connection()
        conn.execute('DELETE FROM showtimes WHERE movie_id = ?', (movie_id,))
        conn.commit()
        conn.close()