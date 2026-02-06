import unittest
import requests
import json
import uuid

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class TestBase(unittest.TestCase):
    USER_URL = "http://127.0.0.1:5004/api"
    MOVIE_URL = "http://127.0.0.1:5001/api"
    BOOKING_URL = "http://127.0.0.1:5002/api"
    PAYMENT_URL = "http://127.0.0.1:5003/api"

    def _request(self, step_name, method, url, payload=None, headers=None, expected_status=200):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}>>> STEP: {step_name}{Colors.RESET}")
        print(f"    {Colors.BLUE}{method} {url}{Colors.RESET}")
        
        if headers: print(f"    {Colors.CYAN}Headers: {headers}{Colors.RESET}")
        if payload: print(f"    {Colors.CYAN}Payload: {json.dumps(payload)}{Colors.RESET}")

        try:
            if method == 'POST': resp = requests.post(url, json=payload, headers=headers, timeout=30)
            elif method == 'GET': resp = requests.get(url, headers=headers, timeout=30)
            elif method == 'PUT': resp = requests.put(url, json=payload, headers=headers, timeout=30)
            elif method == 'DELETE': resp = requests.delete(url, headers=headers, timeout=30)
            else: raise ValueError(f"Unsupported method: {method}")
            
            if resp.status_code != expected_status:
                print(f"    {Colors.RED}!!! FAILURE !!!{Colors.RESET}")
                print(f"    {Colors.RED}Status: {resp.status_code} (Expected: {expected_status}){Colors.RESET}")
                print(f"    {Colors.RED}Response Body: {resp.text}{Colors.RESET}")
                self.assertEqual(resp.status_code, expected_status, f"API failed with {resp.status_code}: {resp.text}")
            else:
                print(f"    {Colors.BOLD}Status: {Colors.GREEN}{resp.status_code}{Colors.RESET}")

            return resp
        except requests.exceptions.ConnectionError:
            self.fail(f"{Colors.RED}Could not connect to service at {url}{Colors.RESET}")
        except requests.exceptions.ReadTimeout:
            self.fail(f"{Colors.RED}Request timed out (Server took too long){Colors.RESET}")

    def create_test_user(self):
        unique_id = str(uuid.uuid4())[:8]
        email = f"auto_{unique_id}@test.com"
        password = "123"
        requests.post(f"{self.USER_URL}/auth/register", json={"email": email, "password": password}, timeout=30)
        resp = requests.post(f"{self.USER_URL}/auth/login", json={"username": email, "password": password}, timeout=30)
        return email, resp.json().get('token')
    
    def get_admin_token(self):
        resp = requests.post(f"{self.USER_URL}/auth/login", json={"username": "admin", "password": "111111"}, timeout=30)
        return resp.json().get('token')