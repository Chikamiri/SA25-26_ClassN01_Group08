class Booking:
    def __init__(self, booking_id, user_name, showtime_id, seat_number, price):
        self.id = booking_id
        self.user_name = user_name
        self.showtime_id = showtime_id
        self.seat_number = seat_number
        self.price = price  

    def to_dict(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "showtime_id": self.showtime_id,
            "seat_number": self.seat_number,
            "price": self.price
        }