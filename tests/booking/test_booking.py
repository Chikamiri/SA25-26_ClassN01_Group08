from tests.base import TestBase
import requests

class TestBooking(TestBase):
    def setUp(self):
        self.email, self.token = self.create_test_user()
        self.headers = {"X-User-Email": self.email}
        
        m_resp = requests.post(f"{self.MOVIE_URL}/movies", 
                               json={"title": "Booking Movie", "genre": "Test", "duration": 100, "release_date": "2026-01-01"}, timeout=5)
        self.movie_id = m_resp.json().get('id')

        s_payload = {
            "movie_id": self.movie_id, 
            "start_time": "2026-10-10 10:00", 
            "end_time": "2026-10-10 12:00", 
            "price": 50000, 
            "total_seats": 50
        }
        s_resp = requests.post(f"{self.MOVIE_URL}/showtimes", json=s_payload, timeout=5)
        self.showtime_id = s_resp.json().get('id')
        self.booking_id = None

    def test_01_TC_BOOKING_01_book_single(self):
        payload = {"showtime_id": self.showtime_id, "seat_number": "A1"}
        resp = self._request("TC_BOOKING_01", 'POST', f"{self.BOOKING_URL}/bookings", 
                      payload, self.headers, expected_status=201)
        self.booking_id = resp.json().get('booking_id')

    def test_02_TC_BOOKING_02_book_multiple(self):
        payload = {"showtime_id": self.showtime_id, "seat_number": "A2"}
        self._request("TC_BOOKING_02 (1)", 'POST', f"{self.BOOKING_URL}/bookings", payload, self.headers, expected_status=201)
        
        payload2 = {"showtime_id": self.showtime_id, "seat_number": "A3"}
        self._request("TC_BOOKING_02 (2)", 'POST', f"{self.BOOKING_URL}/bookings", payload2, self.headers, expected_status=201)

    def test_03_TC_BOOKING_03_no_auth(self):
        payload = {"showtime_id": self.showtime_id, "seat_number": "A4"}
        self._request("TC_BOOKING_03", 'POST', f"{self.BOOKING_URL}/bookings", payload, expected_status=401)

    def test_04_TC_BOOKING_08_get_seats(self):
        self._request("TC_BOOKING_08", 'GET', f"{self.BOOKING_URL}/showtimes/{self.showtime_id}/seats")

    def test_05_TC_BOOKING_FULL_FLOW(self):
        payload = {"showtime_id": self.showtime_id, "seat_number": "B1"}
        resp = self._request("Create for Flow", 'POST', f"{self.BOOKING_URL}/bookings", payload, self.headers, expected_status=201)
        b_id = resp.json().get('booking_id')

        self._request("TC_BOOKING_05 (Detail)", 'GET', f"{self.BOOKING_URL}/bookings/{b_id}")
        self._request("TC_BOOKING_04 (My List)", 'GET', f"{self.BOOKING_URL}/bookings", headers=self.headers)
        self._request("TC_BOOKING_06 (Update Status)", 'PUT', f"{self.BOOKING_URL}/bookings/{b_id}/status", {"status": "confirmed"})
        self._request("TC_BOOKING_07 (Cancel)", 'DELETE', f"{self.BOOKING_URL}/bookings/{b_id}")

    def tearDown(self):
        if self.showtime_id: requests.delete(f"{self.MOVIE_URL}/showtimes/{self.showtime_id}", timeout=5)
        if self.movie_id: requests.delete(f"{self.MOVIE_URL}/movies/{self.movie_id}", timeout=5)