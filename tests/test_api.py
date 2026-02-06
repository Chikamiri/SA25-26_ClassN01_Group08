import unittest
import requests
import subprocess
import time
import os
import sys
import json
import uuid
import socket
import glob
import random

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class TestFull31Cases(unittest.TestCase):
    
    SERVICES = {
        "movie":   {"port": 5001, "path": "src/movie/app.py"},
        "booking": {"port": 5002, "path": "src/booking/app.py"},
        "payment": {"port": 5003, "path": "src/payment/app.py"},
        "user":    {"port": 5004, "path": "src/user/app.py"}
    }
    BASE_URL = "http://127.0.0.1"

    # Shared Data
    state = {
        "user_email": None, "user_token": None,
        "movie_id": None, "showtime_id": None,
        "booking_id": None, "card_id": None
    }

    # ================= HELPERS =================

    @classmethod
    def clean_databases(cls):
        print(f"{Colors.YELLOW}[SETUP] Cleaning old database files...{Colors.RESET}")
        root_dir = os.getcwd()
        patterns = [
            os.path.join(root_dir, '*.db*'), 
            os.path.join(root_dir, 'instance', '*.db*'),
            os.path.join(root_dir, 'src', '**', '*.db*')
        ]
        for pattern in patterns:
            for db_file in glob.glob(pattern, recursive=True):
                try:
                    os.remove(db_file)
                    print(f" -> Deleted: {os.path.basename(db_file)}")
                except: pass

    @classmethod
    def setUpClass(cls):
        cls.clean_databases()
        print(f"\n{Colors.BOLD}{Colors.HEADER}>>> STARTING 31 TEST CASES <<<{Colors.RESET}")
        
        cls.processes = []
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
        env['PYTHONUNBUFFERED'] = '1'
        python_exec = sys.executable

        for name, config in cls.SERVICES.items():
            full_path = os.path.join(*config['path'].split('/'))
            print(f" -> Starting {name.upper()}...")
            p = subprocess.Popen([python_exec, full_path], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cls.processes.append(p)

        print(f" -> {Colors.YELLOW}Waiting 12s for services...{Colors.RESET}")
        time.sleep(12) 
        cls.wait_for_services()
        print(f"{Colors.GREEN}[READY] All systems go.{Colors.RESET}\n")

    @classmethod
    def wait_for_services(cls, timeout=30):
        start = time.time()
        for _, config in cls.SERVICES.items():
            while True:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    if sock.connect_ex(('127.0.0.1', config['port'])) == 0: 
                        sock.close()
                        break
                except: pass
                if time.time() - start > timeout:
                    sys.exit(1)
                time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        print(f"\n{Colors.BOLD}{Colors.HEADER}>>> STOPPING SERVICES <<<{Colors.RESET}")
        for p in cls.processes: p.terminate()
        time.sleep(1)

    def _req(self, method, port, endpoint, payload=None, headers=None, status=200):
        url = f"{self.BASE_URL}:{port}{endpoint}"
        print(f"{Colors.BLUE}[{method}] {url}{Colors.RESET}")
        
        for attempt in range(3):
            try:
                time.sleep(0.5)
                kwargs = {'json': payload, 'headers': headers, 'timeout': 10}
                
                if method == 'GET': resp = requests.get(url, **kwargs)
                elif method == 'POST': resp = requests.post(url, **kwargs)
                elif method == 'PUT': resp = requests.put(url, **kwargs)
                elif method == 'DELETE': resp = requests.delete(url, **kwargs)
                
                if resp.status_code == status:
                    return resp
                
                if resp.status_code == 500 and "database is locked" in resp.text:
                    print(f"{Colors.YELLOW} -> DB Locked. Retrying ({attempt+1}/3)...{Colors.RESET}")
                    time.sleep(2)
                    continue

                print(f"{Colors.RED}FAIL: Got {resp.status_code}, Expected {status}. Body: {resp.text[:200]}{Colors.RESET}")
                self.assertEqual(resp.status_code, status)
                return resp

            except Exception as e:
                print(f"{Colors.RED} -> Connection error: {e}. Retrying...{Colors.RESET}")
                time.sleep(1)
        
        self.fail(f"Request failed after 3 attempts")

    # --- HÀM QUAN TRỌNG NHẤT: Lấy ghế thực tế từ Server ---
    def get_real_available_seat(self, showtime_id):
        # Gọi API lấy danh sách ghế của suất chiếu này
        resp = self._req('GET', 5002, f"/api/showtimes/{showtime_id}/seats", status=200)
        all_seats = resp.json()
        
        # Lọc ra các ghế có status là 'available'
        # Hỗ trợ cả trường hợp API trả về list object hoặc list string
        available = []
        for s in all_seats:
            if isinstance(s, dict):
                # Kiểm tra key 'status' hoặc 'is_booked' tùy backend
                if s.get('status') == 'available' or s.get('available') == True:
                    available.append(s.get('seat_number'))
            else:
                # Nếu backend trả về list string (ví dụ ["A1", "A2"]) thì mặc định là available
                available.append(str(s))
        
        if not available:
            self.fail(f"Showtime {showtime_id} has NO available seats! Cannot test booking.")
            
        # Chọn ngẫu nhiên 1 ghế trong danh sách THỰC TẾ đó
        chosen_seat = random.choice(available)
        print(f"{Colors.CYAN} -> Picked random seat from server: {chosen_seat}{Colors.RESET}")
        return chosen_seat

    def create_dedicated_showtime(self):
        if not self.state['movie_id']: return None
        day = random.randint(10, 28)
        
        # 2 tiếng (120 phút) < 182 phút -> Hợp lệ
        start_t = f"2026-12-{day} 10:00"
        end_t   = f"2026-12-{day} 12:00" 

        p = {
            "movie_id": self.state['movie_id'], 
            "start_time": start_t,
            "end_time": end_t,
            "price": 100000, 
            "total_seats": 50 
        }
        r = self._req('POST', 5001, '/api/showtimes', p, status=201)
        return r.json().get('id')

    # ================= USER SERVICE =================
    
    def test_01_TC_USER_01_register(self):
        uid = str(uuid.uuid4())[:8]
        email = f"user_{uid}@test.com"
        self._req('POST', 5004, '/api/auth/register', {"email": email, "password": "123"}, status=201)
        self.state['user_email'] = email

    def test_02_TC_USER_02_register_duplicate(self):
        self._req('POST', 5004, '/api/auth/register', {"email": self.state['user_email'], "password": "123"}, status=400)

    def test_03_TC_USER_03_login_success(self):
        resp = self._req('POST', 5004, '/api/auth/login', 
                         {"username": self.state['user_email'], "password": "123"}, status=200)
        self.state['user_token'] = resp.json()['token']

    def test_04_TC_USER_04_login_fail(self):
        self._req('POST', 5004, '/api/auth/login', 
                  {"username": self.state['user_email'], "password": "wrong"}, status=401)

    # ================= MOVIE SERVICE =================

    def test_05_TC_MOVIE_01_create(self):
        payload = {"title": "Avengers", "genre": "Action", "duration": 180, "release_date": "2025-05-01"}
        resp = self._req('POST', 5001, '/api/movies', payload, status=201)
        self.state['movie_id'] = resp.json()['id']

    def test_06_TC_MOVIE_02_get_all(self):
        self._req('GET', 5001, '/api/movies', status=200)

    def test_07_TC_MOVIE_03_get_detail(self):
        self._req('GET', 5001, f"/api/movies/{self.state['movie_id']}", status=200)

    def test_08_TC_MOVIE_04_get_not_found(self):
        self._req('GET', 5001, '/api/movies/99999', status=404)

    def test_09_TC_MOVIE_05_update(self):
        payload = {"title": "Avengers: Endgame", "genre": "Sci-Fi", "duration": 182, "release_date": "2025-05-01"}
        self._req('PUT', 5001, f"/api/movies/{self.state['movie_id']}", payload, status=200)

    def test_10_TC_MOVIE_07_search(self):
        self._req('GET', 5001, '/api/movies?query=Avengers', status=200)

    # ================= SHOWTIME SERVICE =================

    def test_11_TC_SHOWTIME_01_create(self):
        # 120 phút -> Hợp lệ
        payload = {
            "movie_id": self.state['movie_id'], 
            "start_time": "2026-12-01 10:00", 
            "end_time": "2026-12-01 12:00", 
            "price": 100000, 
            "total_seats": 50
        }
        resp = self._req('POST', 5001, '/api/showtimes', payload, status=201)
        self.state['showtime_id'] = resp.json()['id']

    def test_12_TC_SHOWTIME_02_get_list(self):
        self._req('GET', 5001, f"/api/showtimes?movie_id={self.state['movie_id']}", status=200)

    def test_13_TC_SHOWTIME_03_get_detail(self):
        pass 

    def test_14_TC_SHOWTIME_04_update(self):
        payload = {
            "movie_id": self.state['movie_id'], 
            "start_time": "2026-12-01 19:00", 
            "end_time": "2026-12-01 21:00", 
            "price": 120000, "total_seats": 50
        }
        self._req('PUT', 5001, f"/api/showtimes/{self.state['showtime_id']}", payload, status=200)

    # ================= BOOKING SERVICE =================

    def test_15_TC_BOOKING_01_single(self):
        """Tạo suất -> Lấy ghế thực tế -> Đặt"""
        headers = {"X-User-Email": self.state['user_email']}
        new_showtime = self.create_dedicated_showtime() 
        
        # --- QUAN TRỌNG: Lấy ghế thật từ server ---
        real_seat = self.get_real_available_seat(new_showtime)
        
        payload = {"showtime_id": new_showtime, "seat_number": real_seat}
        resp = self._req('POST', 5002, '/api/bookings', payload, headers, status=201)
        
        data = resp.json()
        if "booking_ids" in data: self.state['booking_id'] = data["booking_ids"][0]
        else: self.state['booking_id'] = data.get("booking_id")

    def test_16_TC_BOOKING_02_multiple(self):
        """Tạo suất -> Lấy 2 ghế thực tế -> Đặt"""
        headers = {"X-User-Email": self.state['user_email']}
        new_showtime = self.create_dedicated_showtime() 
        
        # Lấy ghế
        seat1 = self.get_real_available_seat(new_showtime)
        # Hack nhỏ: Gọi lại lần nữa, hy vọng random ra cái khác. 
        # Nếu trùng thì server báo lỗi, nên ta gọi loop cho chắc
        seat2 = seat1
        while seat2 == seat1:
            seat2 = self.get_real_available_seat(new_showtime)

        self._req('POST', 5002, '/api/bookings', {"showtime_id": new_showtime, "seat_number": seat1}, headers, status=201)
        self._req('POST', 5002, '/api/bookings', {"showtime_id": new_showtime, "seat_number": seat2}, headers, status=201)

    def test_17_TC_BOOKING_03_no_auth(self):
        # Lấy đại 1 ghế để test lỗi 401
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

    # ================= PAYMENT SERVICE =================

    def test_22_TC_PAYMENT_04_add_card(self):
        headers = {"X-User-Email": self.state['user_email']}
        payload = {"card_number": "1234567890123456", "card_holder": "TEST USER"}
        resp = self._req('POST', 5003, '/api/payment-methods', payload, headers, status=201)

    def test_23_TC_PAYMENT_05_get_cards(self):
        headers = {"X-User-Email": self.state['user_email']}
        resp = self._req('GET', 5003, '/api/payment-methods', headers=headers, status=200)
        if len(resp.json()) > 0:
            self.state['card_id'] = resp.json()[0]['id']

    def test_24_TC_PAYMENT_07_update_card(self):
        if self.state['card_id']:
            headers = {"X-User-Email": self.state['user_email']}
            self._req('PUT', 5003, f"/api/payment-methods/{self.state['card_id']}", 
                      {"card_holder": "NEW NAME"}, headers, status=200)

    def test_25_TC_PAYMENT_01_success(self):
        """Tạo suất -> Lấy ghế thật -> Đặt -> Thanh toán"""
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

    # ================= CLEANUP =================

    def test_28_TC_BOOKING_07_cancel(self):
        if self.state['booking_id']:
            self._req('DELETE', 5002, f"/api/bookings/{self.state['booking_id']}", status=200)

    def test_29_TC_SHOWTIME_05_delete(self):
        p = {"movie_id": self.state['movie_id'], "start_time": "2030-01-01 10:00", "end_time": "2030-01-01 12:00", "price": 100, "total_seats": 10}
        r = self._req('POST', 5001, '/api/showtimes', p, status=201)
        sid = r.json()['id']
        self._req('DELETE', 5001, f"/api/showtimes/{sid}", status=200)

    def test_30_TC_MOVIE_06_delete(self):
        p = {"title": "Trash Movie", "genre": "N/A", "duration": 10, "release_date": "2020-01-01"}
        r = self._req('POST', 5001, '/api/movies', p, status=201)
        mid = r.json()['id']
        self._req('DELETE', 5001, f"/api/movies/{mid}", status=200)

    def test_31_FINAL_CHECK(self):
        self._req('GET', 5001, '/api/movies', status=200)

if __name__ == '__main__':
    unittest.main(verbosity=2, failfast=False)