import sqlite3
import os

class BookingRepository:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'booking.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                showtime_id INTEGER NOT NULL,
                seat_number TEXT NOT NULL,
                email TEXT NOT NULL, 
                status TEXT DEFAULT 'booked'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                showtime_id INTEGER NOT NULL,
                seat_number TEXT NOT NULL,
                status TEXT DEFAULT 'available',
                UNIQUE(showtime_id, seat_number)
            )
        ''')
        
        conn.commit()
        conn.close()

    def check_seat_availability(self, showtime_id, seat_number):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT status FROM seats WHERE showtime_id = ? AND seat_number = ?', (showtime_id, seat_number))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def create_booking(self, showtime_id, seat_number, email):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE seats SET status = "booked" WHERE showtime_id = ? AND seat_number = ?', 
            (showtime_id, seat_number)
        )
        
        cursor.execute(
            'INSERT INTO bookings (showtime_id, seat_number, email) VALUES (?, ?, ?)',
            (showtime_id, seat_number, email)
        )
        booking_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return booking_id

    def get_booking_by_id(self, booking_id):
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    def get_all_bookings(self):
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bookings')
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_booking(self, booking_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT showtime_id, seat_number FROM bookings WHERE id = ?', (booking_id,))
        row = cursor.fetchone()
        
        if row:
            showtime_id, seat_number = row
            cursor.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
            cursor.execute(
                'UPDATE seats SET status = "available" WHERE showtime_id = ? AND seat_number = ?', 
                (showtime_id, seat_number)
            )
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False

    def create_seats(self, showtime_id, total_seats):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            for i in range(1, total_seats + 1):
                seat_number = f"S{i}"
                cursor.execute(
                    'INSERT OR IGNORE INTO seats (showtime_id, seat_number) VALUES (?, ?)',
                    (showtime_id, seat_number)
                )
            conn.commit()
        except Exception as e:
            print(f"Error creating seats: {e}")
        finally:
            conn.close()

    def get_seats_by_showtime(self, showtime_id):
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM seats WHERE showtime_id = ?', (showtime_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_customers_by_showtime(self, showtime_id):
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT email, seat_number FROM bookings WHERE showtime_id = ?', (showtime_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]