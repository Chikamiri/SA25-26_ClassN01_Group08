from tests.base import TestBase

class TestBooking(TestBase):
    def test_15_TC_BOOKING_01_single(self):
        headers = {"X-User-Email": self.state['user_email']}
        new_showtime = self.create_dedicated_showtime()
        real_seat = self.get_real_available_seat(new_showtime)
        
        payload = {"showtime_id": new_showtime, "seat_number": real_seat}
        resp = self._req('POST', 5002, '/api/bookings', payload, headers, status=201)
        
        data = resp.json()
        if "booking_ids" in data: TestBase.state['booking_id'] = data["booking_ids"][0]
        else: TestBase.state['booking_id'] = data.get("booking_id")

    def test_16_TC_BOOKING_02_multiple(self):
        headers = {"X-User-Email": self.state['user_email']}
        new_showtime = self.create_dedicated_showtime()
        
        seat1 = self.get_real_available_seat(new_showtime)
        seat2 = seat1
        while seat2 == seat1:
            seat2 = self.get_real_available_seat(new_showtime)

        self._req('POST', 5002, '/api/bookings', {"showtime_id": new_showtime, "seat_number": seat1}, headers, status=201)
        self._req('POST', 5002, '/api/bookings', {"showtime_id": new_showtime, "seat_number": seat2}, headers, status=201)

    def test_17_TC_BOOKING_03_no_auth(self):
        seat = self.get_real_available_seat(self.state['showtime_id'])
        payload = {"showtime_id": self.state['showtime_id'], "seat_number": seat}
        self._req('POST', 5002, '/api/bookings', payload, status=401)

    def test_18_TC_BOOKING_04_my_list(self):
        headers = {"X-User-Email": self.state['user_email']}
        self._req('GET', 5002, '/api/bookings/my', headers=headers, status=200)

    def test_19_TC_BOOKING_05_detail(self):
        if not self.state['booking_id']: self.skipTest("No booking ID")
        self._req('GET', 5002, f"/api/bookings/{self.state['booking_id']}", status=200)

    def test_20_TC_BOOKING_06_update_status(self):
        if not self.state['booking_id']: self.skipTest("No booking ID")
        self._req('PUT', 5002, f"/api/bookings/{self.state['booking_id']}/status", {"status": "confirmed"}, status=200)

    def test_21_TC_BOOKING_08_get_seats(self):
        self._req('GET', 5002, f"/api/showtimes/{self.state['showtime_id']}/seats", status=200)

    def test_28_TC_BOOKING_07_cancel(self):
        if self.state['booking_id']:
            self._req('DELETE', 5002, f"/api/bookings/{self.state['booking_id']}", status=200)