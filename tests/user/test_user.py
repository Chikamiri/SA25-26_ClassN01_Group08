from tests.base import TestBase
import uuid

class TestUser(TestBase):
    def test_01_TC_USER_01_register(self):
        uid = str(uuid.uuid4())[:8]
        email = f"user_{uid}@test.com"
        self._req('POST', 5004, '/api/auth/register', {"email": email, "password": "123"}, status=201)
        TestBase.state['user_email'] = email

    def test_02_TC_USER_02_register_duplicate(self):
        self._req('POST', 5004, '/api/auth/register', {"email": self.state['user_email'], "password": "123"}, status=400)

    def test_03_TC_USER_03_login_success(self):
        resp = self._req('POST', 5004, '/api/auth/login', 
                         {"username": self.state['user_email'], "password": "123"}, status=200)
        TestBase.state['user_token'] = resp.json()['token']

    def test_04_TC_USER_04_login_fail(self):
        self._req('POST', 5004, '/api/auth/login', 
                  {"username": self.state['user_email'], "password": "wrong"}, status=401)