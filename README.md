# Lab 3 instruction
install extension postman

Open your Terminal and navigate to the folder containing app.py (e.g., src/movie).

Run the following command to start the server:
python app.py

Then the server will start at: http://127.0.0.1:5000

open the postman extension and send a request to test booking a new ticket (Make sure to select JSON format) with the following example:
URL: http://127.0.0.1:5000/api/bookings

Method: POST

Body (JSON):

{
    "user_name": "Test User",
    "showtime_id": "ST001",
    "seat_number": "J10",
    "price": 100000
}

check the details of the booked ticket 

URL: http://127.0.0.1:5000/api/bookings/1
Method: GET