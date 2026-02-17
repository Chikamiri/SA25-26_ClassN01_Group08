from tests.base import TestBase

class TestMovie(TestBase):
    def test_05_TC_MOVIE_01_create(self):
        payload = {"title": "Avengers", "genre": "Action", "duration": 180, "release_date": "2025-05-01"}
        resp = self._req('POST', 5001, '/api/movies', payload, status=201)
        TestBase.state['movie_id'] = resp.json()['id']

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

    def test_11_TC_SHOWTIME_01_create(self):
        payload = {
            "movie_id": self.state['movie_id'], "start_time": "2026-12-01 10:00", 
            "end_time": "2026-12-01 12:00", "price": 100000, "total_seats": 50
        }
        resp = self._req('POST', 5001, '/api/showtimes', payload, status=201)
        TestBase.state['showtime_id'] = resp.json()['id']

    def test_12_TC_SHOWTIME_02_get_list(self):
        self._req('GET', 5001, f"/api/showtimes?movie_id={self.state['movie_id']}", status=200)

    def test_13_TC_SHOWTIME_03_get_detail(self):
        pass 

    def test_14_TC_SHOWTIME_04_update(self):
        payload = {
            "movie_id": self.state['movie_id'], "start_time": "2026-12-01 19:00", 
            "end_time": "2026-12-01 21:00", "price": 120000, "total_seats": 50
        }
        self._req('PUT', 5001, f"/api/showtimes/{self.state['showtime_id']}", payload, status=200)
    
    def test_29_TC_SHOWTIME_05_delete(self):
        p = {"movie_id": self.state['movie_id'], "start_time": "2030-01-01 10:00", "end_time": "2030-01-01 12:00", "price": 100, "total_seats": 50}
        r = self._req('POST', 5001, '/api/showtimes', p, status=201)
        sid = r.json()['id']
        self._req('DELETE', 5001, f"/api/showtimes/{sid}", status=200)

    def test_30_TC_MOVIE_06_delete(self):
        p = {"title": "Trash Movie", "genre": "N/A", "duration": 10, "release_date": "2020-01-01"}
        r = self._req('POST', 5001, '/api/movies', p, status=201)
        mid = r.json()['id']
        self._req('DELETE', 5001, f"/api/movies/{mid}", status=200)