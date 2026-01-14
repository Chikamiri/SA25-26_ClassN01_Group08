import unittest
import requests
import subprocess
import time
import os
import sys
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

class TestMovieBookingSystem(unittest.TestCase):
    # Shared state for the test sequence
    movie_id = None
    showtime_id = None
    booking_id = None
    user_email = None
    user_token = None
    admin_token = None

    @classmethod
    def setUpClass(cls):
        print(f"\n{Colors.BOLD}{Colors.HEADER}" + "="*60)
        print("[INFO] INITIALIZING TEST ENVIRONMENT")
        print("="*60 + f"{Colors.RESET}")
        
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
        
        python_executable = sys.executable

        services = [
            ("Movie Service", 'src/movie/app.py', 5001),
            ("Booking Service", 'src/booking/app.py', 5002),
            ("Payment Service", 'src/payment/app.py', 5003),
            ("User Service", 'src/user/app.py', 5004),
        ]
        
        cls.processes = []
        
        for name, script_path, port in services:
            print(f" -> Starting {name} on port {port}...")
            full_path = os.path.join(*script_path.split('/'))
            p = subprocess.Popen(
                [python_executable, full_path],
                env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            cls.processes.append((name, p))
            time.sleep(1)

        time.sleep(5) 

        for name, p in cls.processes:
            if p.poll() is not None:
                print(f"{Colors.RED}[ERROR] {name} failed to start.{Colors.RESET}")
                cls.tearDownClass()
                sys.exit(1)
            
        print(f"{Colors.BOLD}{Colors.HEADER}" + "="*60 + f"{Colors.RESET}\n")

    @classmethod
    def tearDownClass(cls):
        print(f"\n{Colors.BOLD}{Colors.HEADER}" + "="*60)
        print("[INFO] TEARING DOWN SERVICES")
        if hasattr(cls, 'processes'):
            for name, p in cls.processes:
                print(f" -> Stopping {name}...")
                p.terminate()
            for name, p in cls.processes:
                p.wait()
        print("="*60 + f"{Colors.RESET}")

    def _request(self, step_name, method, url, payload=None, headers=None):
        """Helper to execute requests and log logically with color"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}>>> STEP: {step_name}{Colors.RESET}")
        print(f"    {Colors.BLUE}{method} {url}{Colors.RESET}")
        
        if headers:
            print(f"    {Colors.CYAN}Headers: {headers}{Colors.RESET}")

        if payload:
            print(f"    {Colors.CYAN}Payload (JSON):{Colors.RESET}")
            print(f"{Colors.CYAN}{json.dumps(payload, indent=4)}{Colors.RESET}")

        try:
            if method == 'POST':
                resp = requests.post(url, json=payload, headers=headers)
            elif method == 'GET':
                resp = requests.get(url, headers=headers)
            elif method == 'DELETE':
                resp = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            status_color = Colors.GREEN if 200 <= resp.status_code < 300 else Colors.RED
            print(f"    {Colors.BOLD}Response Status: {status_color}{resp.status_code}{Colors.RESET}")
            
            print(f"    {Colors.GREEN}Response Body (JSON):{Colors.RESET}")
            try:
                print(f"{Colors.GREEN}{json.dumps(resp.json(), indent=4)}{Colors.RESET}")
            except:
                print(f"    {Colors.RED}{resp.text}{Colors.RESET}")
            
            return resp
        except requests.exceptions.ConnectionError:
            self.fail(f"{Colors.RED}Could not connect to service at {url}{Colors.RESET}")

    def test_00_a_user_auth_flow(self):
        """Test User Registration and Login"""
        unique_id = str(uuid.uuid4())[:8]
        email = f"test_{unique_id}@example.com"
        password = "securepassword123"
        
        self._request("User Registration", 'POST', "http://127.0.0.1:5004/api/auth/register", 
                      {"email": email, "password": password})

        resp = self._request("User Login", 'POST', "http://127.0.0.1:5004/api/auth/login", 
                             {"username": email, "password": password})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        TestMovieBookingSystem.user_token = data['token']
        TestMovieBookingSystem.user_email = email

    def test_00_b_admin_login(self):
        """Test Admin Login"""
        resp = self._request("Admin Login", 'POST', "http://127.0.0.1:5004/api/auth/login", 
                             {"username": "admin", "password": "111111"})
        self.assertEqual(resp.status_code, 200)
        TestMovieBookingSystem.admin_token = resp.json()['token']

    def test_01_create_movie(self):
        """Test creating a new movie (Admin Action)"""
        url = "http://127.0.0.1:5001/api/movies"
        payload = {
            "title": "Inception",
            "genre": "Sci-Fi",
            "duration": 148,
            "release_date": "2010-07-16"
        }
        resp = self._request("Create Movie", 'POST', url, payload)
        self.assertEqual(resp.status_code, 201)
        TestMovieBookingSystem.movie_id = resp.json()['id']
        
        self._request("Verify Movie Details", 'GET', f"{url}/{TestMovieBookingSystem.movie_id}")

    def test_02_get_movies(self):
        """Test retrieving movies"""
        self._request("Get Movie List", 'GET', "http://127.0.0.1:5001/api/movies")

    def test_03_create_showtime(self):
        """Test creating a showtime (Admin Action)"""
        if not TestMovieBookingSystem.movie_id:
             self.fail("Prerequisite Movie missing")
             
        url = "http://127.0.0.1:5001/api/showtimes"
        payload = {
            "movie_id": TestMovieBookingSystem.movie_id,
            "start_time": "2025-12-01 18:00",
            "end_time": "2025-12-01 20:20",
            "total_seats": 20,
            "price": 75000
        }
        resp = self._request("Create Showtime", 'POST', url, payload)
        self.assertEqual(resp.status_code, 201)
        TestMovieBookingSystem.showtime_id = resp.json()['id']

    def test_04_create_booking(self):
        """Test creating a booking (User Action)"""
        if not TestMovieBookingSystem.showtime_id or not TestMovieBookingSystem.user_email:
            self.fail("Prerequisites missing")

        url = "http://127.0.0.1:5002/api/bookings"
        payload = {"showtime_id": TestMovieBookingSystem.showtime_id, "seat_number": "S1"}
        headers = {"X-User-Email": TestMovieBookingSystem.user_email}
        
        resp = self._request("Create Booking", 'POST', url, payload, headers)
        self.assertEqual(resp.status_code, 201)
        TestMovieBookingSystem.booking_id = resp.json()['booking_id']

    def test_05_process_payment(self):
        """Test processing a payment (User Action)"""
        if not TestMovieBookingSystem.booking_id:
            self.fail("Prerequisite Booking missing")

        url = "http://127.0.0.1:5003/api/payments"
        resp = self._request("Process Payment", 'POST', url, {"booking_id": TestMovieBookingSystem.booking_id})
        self.assertEqual(resp.status_code, 201)

    def test_06_cleanup(self):
        """Test deleting entities (Cleanup / Admin Action)"""
        if TestMovieBookingSystem.booking_id:
            self._request("Delete Booking", 'DELETE', f"http://127.0.0.1:5002/api/bookings/{TestMovieBookingSystem.booking_id}")

        if TestMovieBookingSystem.showtime_id:
            self._request("Delete Showtime", 'DELETE', f"http://127.0.0.1:5001/api/showtimes/{TestMovieBookingSystem.showtime_id}")

        if TestMovieBookingSystem.movie_id:
            self._request("Delete Movie", 'DELETE', f"http://127.0.0.1:5001/api/movies/{TestMovieBookingSystem.movie_id}")

if __name__ == '__main__':
    unittest.main(verbosity=0)