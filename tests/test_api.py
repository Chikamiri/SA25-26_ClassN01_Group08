import unittest
import requests
import subprocess
import time
import os
import sys
import json

class TestMovieBookingSystem(unittest.TestCase):
    movie_id = None
    showtime_id = None

    @classmethod
    def setUpClass(cls):
        print("\n" + "="*50)
        print("[INFO] Setting up test environment...")
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
        
        # Ensure we are using the venv python
        python_executable = sys.executable

        print("[INFO] Starting Movie Service on port 5001...")
        cls.movie_proc = subprocess.Popen(
            [python_executable, os.path.join('src', 'movie', 'app.py')],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        print("[INFO] Starting Booking Service on port 5002...")
        cls.booking_proc = subprocess.Popen(
            [python_executable, os.path.join('src', 'booking', 'app.py')],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        print("[INFO] Waiting for services to initialize...")
        time.sleep(5) # Increased wait time

        if cls.movie_proc.poll() is not None:
            print("[ERROR] Movie Service failed to start.")
            print(cls.movie_proc.stderr.read().decode())
            sys.exit(1)
            
        if cls.booking_proc.poll() is not None:
            print("[ERROR] Booking Service failed to start.")
            print(cls.booking_proc.stderr.read().decode())
            sys.exit(1)
            
        print("[INFO] Services started successfully.\n")
        print("="*50 + "\n")

    @classmethod
    def tearDownClass(cls):
        print("\n" + "="*50)
        print("[INFO] Tearing down services...")
        cls.movie_proc.terminate()
        cls.booking_proc.terminate()
        cls.movie_proc.wait()
        cls.booking_proc.wait()
        print("[INFO] Services stopped.")
        print("="*50)

    def test_01_create_movie(self):
        """Test creating a new movie"""
        print("\n[RUN] test_01_create_movie")
        url = "http://127.0.0.1:5001/api/movies"
        payload = {
            "title": "Inception",
            "genre": "Sci-Fi",
            "duration": 148,
            "release_date": "2010-07-16"
        }
        try:
            response = requests.post(url, json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Data: {json.dumps(response.json(), indent=2)}")
            self.assertEqual(response.status_code, 201)
            self.assertIn('id', response.json())
            TestMovieBookingSystem.movie_id = response.json()['id']
            
            # Verify details
            get_url = f"{url}/{TestMovieBookingSystem.movie_id}"
            get_resp = requests.get(get_url)
            self.assertEqual(get_resp.status_code, 200)
            self.assertEqual(get_resp.json()['title'], "Inception")
            
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to Movie Service at port 5001")

    def test_02_get_movies(self):
        """Test retrieving movies"""
        print("\n[RUN] test_02_get_movies")
        url = "http://127.0.0.1:5001/api/movies"
        try:
            response = requests.get(url)
            print(f"Response Status: {response.status_code}")
            print(f"Response Data: {json.dumps(response.json(), indent=2)}")
            self.assertEqual(response.status_code, 200)
            self.assertTrue(isinstance(response.json(), list))
        except requests.exceptions.ConnectionError:
             self.fail("Could not connect to Movie Service at port 5001")

    def test_03_create_showtime(self):
        """Test creating a showtime (Prerequisite for booking)"""
        print("\n[RUN] test_03_create_showtime")
        if not TestMovieBookingSystem.movie_id:
             self.fail("Skipping showtime creation because movie creation failed.")
             
        url = "http://127.0.0.1:5001/api/showtimes"
        payload = {
            "movie_id": TestMovieBookingSystem.movie_id,
            "start_time": "2025-12-01 18:00",
            "end_time": "2025-12-01 20:20",
            "total_seats": 20,
            "price": 75000
        }
        try:
            response = requests.post(url, json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Data: {json.dumps(response.json(), indent=2)}")
            self.assertEqual(response.status_code, 201)
            self.assertIn('id', response.json())
            TestMovieBookingSystem.showtime_id = response.json()['id']
        except requests.exceptions.ConnectionError:
             self.fail("Could not connect to Movie Service at port 5001")

    def test_04_create_booking(self):
        """Test creating a booking"""
        print("\n[RUN] test_04_create_booking")
        if not TestMovieBookingSystem.showtime_id:
            self.fail("Skipping booking test because showtime creation failed.")

        url = "http://127.0.0.1:5002/api/bookings"
        payload = {
            "showtime_id": TestMovieBookingSystem.showtime_id,
            "seat_number": "S1"
        }
        headers = {
            "X-User-Email": "testuser@example.com"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(f"Response Status: {response.status_code}")
            print(f"Response Data: {json.dumps(response.json(), indent=2)}")
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json()['message'], "Booking successful")
        except requests.exceptions.ConnectionError:
             self.fail("Could not connect to Booking Service at port 5002")

if __name__ == '__main__':
    unittest.main(verbosity=1)
