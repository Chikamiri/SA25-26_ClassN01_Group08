import sys
import os
from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from booking.business_logic.booking_service import BookingService

app = Flask(__name__)
booking_service = BookingService()

@app.route('/api/bookings/seats/<showtime_id>', methods=['GET'])
def get_seats(showtime_id):
    try:
        seats = booking_service.get_available_seats(showtime_id)
        return jsonify(seats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/bookings', methods=['POST'])
def book_ticket():
    data = request.json
    try:
        result = booking_service.book_ticket(
            showtime_id=data['showtime_id'],
            seat_number=data['seat_number'],
            user_name=data['user_name']
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)