from flask import Flask, request, jsonify
from booking.business_logic.booking_service import BookingService

app = Flask(__name__)
booking_service = BookingService()

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    try:
        booking = booking_service.create_booking(
            user_name=data.get('user_name'),
            showtime_id=data.get('showtime_id'),
            seat_number=data.get('seat_number'),
            price=data.get('price')
        )
        return jsonify(booking.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    try:
        booking = booking_service.get_booking_details(booking_id)
        return jsonify(booking.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(port=5002, debug=True)