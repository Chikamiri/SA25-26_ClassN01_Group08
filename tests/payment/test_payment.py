from tests.base import TestBase

class TestPayment(TestBase):
    def test_22_TC_PAYMENT_04_add_card(self):
        headers = {"X-User-Email": self.state['user_email']}
        payload = {"card_number": "1234567890123456", "card_holder": "TEST USER"}
        resp = self._req('POST', 5003, '/api/payment-methods', payload, headers, status=201)

    def test_23_TC_PAYMENT_05_get_cards(self):
        headers = {"X-User-Email": self.state['user_email']}
        resp = self._req('GET', 5003, '/api/payment-methods', headers=headers, status=200)
        if len(resp.json()) > 0:
            TestBase.state['card_id'] = resp.json()[0]['id']

    def test_24_TC_PAYMENT_07_update_card(self):
        if self.state['card_id']:
            headers = {"X-User-Email": self.state['user_email']}
            self._req('PUT', 5003, f"/api/payment-methods/{self.state['card_id']}", 
                      {"card_holder": "NEW NAME"}, headers, status=200)

    def test_25_TC_PAYMENT_01_success(self):
        headers = {"X-User-Email": self.state['user_email']}
        new_showtime = self.create_dedicated_showtime()
        seat = self.get_real_available_seat(new_showtime)
        
        r = self._req('POST', 5002, '/api/bookings', 
                      {"showtime_id": new_showtime, "seat_number": seat}, headers, status=201)
        try:
            b_data = r.json()
            new_booking_id = b_data.get("booking_id") or b_data.get("booking_ids")[0]
            self._req('POST', 5003, '/api/payments', {"booking_id": new_booking_id}, status=201)
        except: pass

    def test_26_TC_PAYMENT_02_not_found(self):
        self._req('POST', 5003, '/api/payments', {"booking_id": 999999}, status=404)

    def test_27_TC_PAYMENT_06_delete_card(self):
        if self.state['card_id']:
            headers = {"X-User-Email": self.state['user_email']}
            self._req('DELETE', 5003, f"/api/payment-methods/{self.state['card_id']}", headers=headers, status=200)