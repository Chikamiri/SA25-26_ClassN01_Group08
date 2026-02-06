from tests.base import TestBase
import requests

class TestPayment(TestBase):
    def setUp(self):
        self.email, self.token = self.create_test_user()
        self.headers = {"X-User-Email": self.email}
        
        m = requests.post(f"{self.MOVIE_URL}/movies", 
                          json={"title": "Pay Movie", "genre": "T", "duration": 120, "release_date": "2026-01-01"}, timeout=30).json()
        
        s_payload = {
            "movie_id": m['id'], 
            "start_time": "2026-10-01 10:00", 
            "end_time": "2026-10-01 12:00",
            "price": 100000, 
            "total_seats": 50
        }
        s = requests.post(f"{self.MOVIE_URL}/showtimes", json=s_payload, timeout=30).json()
        
        resp_b = requests.post(f"{self.BOOKING_URL}/bookings", 
                          json={"showtime_id": s['id'], "seat_number": "P1"}, 
                          headers=self.headers, timeout=30)
        
        if resp_b.status_code != 201:
            raise Exception(f"Setup failed: Could not create booking. Status: {resp_b.status_code}, Body: {resp_b.text}")

        b = resp_b.json()
        self.booking_id = b['booking_id']
        self.movie_id = m['id']
        self.showtime_id = s['id']
        self.card_id = None

    def test_01_TC_PAYMENT_01_process_success(self):
        self._request("TC_PAYMENT_01", 'POST', f"{self.PAYMENT_URL}/payments", 
                      {"booking_id": self.booking_id}, expected_status=201)

    def test_02_TC_PAYMENT_02_not_found(self):
        self._request("TC_PAYMENT_02", 'POST', f"{self.PAYMENT_URL}/payments", 
                      {"booking_id": "999999"}, expected_status=404)

    def test_03_manage_payment_methods(self):
        payload = {"card_number": "1234567890123456", "card_holder": "TEST USER"}
        self._request("TC_PAYMENT_04", 'POST', f"{self.PAYMENT_URL}/payment-methods", 
                             payload, self.headers, expected_status=201)
        
        list_resp = self._request("TC_PAYMENT_05", 'GET', f"{self.PAYMENT_URL}/payment-methods", headers=self.headers)
        cards = list_resp.json()
        if cards:
            card_id = cards[0].get('id')
            self._request("TC_PAYMENT_07", 'PUT', f"{self.PAYMENT_URL}/payment-methods/{card_id}", 
                          {"card_holder": "UPDATED NAME"}, self.headers)
            self._request("TC_PAYMENT_06", 'DELETE', f"{self.PAYMENT_URL}/payment-methods/{card_id}", headers=self.headers)

    def tearDown(self):
        if hasattr(self, 'booking_id'): requests.delete(f"{self.BOOKING_URL}/bookings/{self.booking_id}", timeout=30)
        if hasattr(self, 'showtime_id'): requests.delete(f"{self.MOVIE_URL}/showtimes/{self.showtime_id}", timeout=30)
        if hasattr(self, 'movie_id'): requests.delete(f"{self.MOVIE_URL}/movies/{self.movie_id}", timeout=30)