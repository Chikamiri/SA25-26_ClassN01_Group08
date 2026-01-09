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
        seats = booking_service.get_seats(showtime_id)
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
            customer_name=data['customer_name']
        )
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
def get_all_bookings():
    return jsonify(booking_service.get_all_bookings()), 200

@app.route('/api/bookings/<booking_id>', methods=['GET'])
def get_booking_detail(booking_id):
    try:
        result = booking_service.get_booking_details(booking_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    try:
        result = booking_service.delete_booking(booking_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/bookings/showtime/<showtime_id>/customers', methods=['GET'])
def get_customers_by_showtime(showtime_id):
    try:
        customers = booking_service.get_affected_customers(showtime_id)
        return jsonify(customers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/internal/seats', methods=['POST'])
def create_seats_internal():
    data = request.json
    try:
        booking_service.create_seats(
            showtime_id=data['showtime_id'],
            total_seats=data['total_seats']
        )
        return jsonify({"message": "Seats created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    print("Booking Service running on port 5002...")
    app.run(debug=True, port=5002)