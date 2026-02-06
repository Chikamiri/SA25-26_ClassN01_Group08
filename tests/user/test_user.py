from tests.base import TestBase
import uuid

class TestUser(TestBase):
    def test_01_TC_USER_01_register_success(self):
        email = f"user_{uuid.uuid4()}@test.com"
        self._request("TC_USER_01", 'POST', f"{self.USER_URL}/auth/register", 
                      {"email": email, "password": "123"}, expected_status=201)

    def test_02_TC_USER_02_register_duplicate(self):
        email, _ = self.create_test_user()
        self._request("TC_USER_02", 'POST', f"{self.USER_URL}/auth/register", 
                      {"email": email, "password": "123"}, expected_status=400)

    def test_03_TC_USER_03_login_success(self):
        email, _ = self.create_test_user()
        resp = self._request("TC_USER_03", 'POST', f"{self.USER_URL}/auth/login", 
                             {"username": email, "password": "123"}, expected_status=200)
        self.assertIn('token', resp.json())

    def test_04_TC_USER_04_login_fail(self):
        email, _ = self.create_test_user()
        self._request("TC_USER_04", 'POST', f"{self.USER_URL}/auth/login", 
                      {"username": email, "password": "wrong_password"}, expected_status=401)