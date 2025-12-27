from booking.models.booking_models import Booking

booking_db = {}
next_id = 1

class BookingRepository:

    def save(self, user_name, showtime_id, seat_number, price):
        global next_id
        booking_id = str(next_id)
        new_booking = Booking(booking_id, user_name, showtime_id, seat_number, price)
        booking_db[booking_id] = new_booking
        next_id += 1
        return new_booking

    def find_by_id(self, booking_id):
        return booking_db.get(booking_id)

    def find_all(self):
        return list(booking_db.values())