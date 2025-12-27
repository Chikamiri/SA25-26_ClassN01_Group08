from booking.persistence.booking_repository import BookingRepository

class BookingService:

    def __init__(self):
        self.repo = BookingRepository()

    def create_booking(self, user_name, showtime_id, seat_number, price):
        if not user_name or not showtime_id or not seat_number:
            raise ValueError("Dữ liệu không hợp lệ: Thiếu thông tin người dùng hoặc ghế.")
        if price < 0:
            raise ValueError("Giá vé không được nhỏ hơn 0.")
        return self.repo.save(user_name, showtime_id, seat_number, price)

    def get_booking_details(self, booking_id):
        booking = self.repo.find_by_id(booking_id)
        if not booking:
            raise ValueError(f"Không tìm thấy đơn đặt vé với ID {booking_id}")
        return booking
        
    def get_all_bookings(self):
        return self.repo.find_all()