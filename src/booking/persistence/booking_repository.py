import sqlite3
import os
from booking.models.booking_models import Seat

class BookingRepository:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, '..', 'db', 'booking.db')

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS seats (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            showtime_id INTEGER NOT NULL,
                            seat_number TEXT NOT NULL,
                            status TEXT DEFAULT 'available')""")

    def create_seats(self, showtime_id, total_seats):
        seats_data = [(showtime_id, f"Seat-{i+1}", "available") for i in range(total_seats)]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany("INSERT INTO seats (showtime_id, seat_number, status) VALUES (?, ?, ?)", seats_data)
            conn.commit()

    def get_seats_by_showtime(self, showtime_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM seats WHERE showtime_id = ?", (showtime_id,))
            rows = cursor.fetchall()
            return [Seat(row[0], row[1], row[2], row[3]) for row in rows]

    def find_seat(self, showtime_id, seat_number):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM seats WHERE showtime_id = ? AND seat_number = ?", (showtime_id, seat_number))
            row = cursor.fetchone()
            return Seat(row[0], row[1], row[2], row[3]) if row else None

    def update_seat_status(self, seat_id, new_status):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE seats SET status = ? WHERE id = ?", (new_status, seat_id))
            conn.commit()
            return cursor.rowcount > 0