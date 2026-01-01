from booking.persistence.booking_repository import BookingRepository

class BookingService:
    def __init__(self):
        self.repo = BookingRepository()

    def get_available_seats(self, showtime_id):
        seats = self.repo.get_seats_by_showtime(showtime_id)
        return [seat.to_dict() for seat in seats if seat.status == 'available']

    def book_ticket(self, showtime_id, seat_number, user_name):
        seat = self.repo.find_seat(showtime_id, seat_number)
        
        if not seat:
            raise ValueError("Invalid seat number")
        if seat.status != 'available':
            raise ValueError(f"seat {seat_number} alread taken")

        success = self.repo.update_seat_status(seat.id, "booked")
        if success:
            return {
                "message": "Ticket Purchase successful",
                "ticket": {
                    "seat": seat_number,
                    "customer": user_name,
                    "showtime_id": showtime_id
                }
            }
        else:
            raise Exception("Lỗi hệ thống")