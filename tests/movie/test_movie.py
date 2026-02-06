from tests.base import TestBase

class TestMovieAndShowtime(TestBase):
    movie_id = None
    showtime_id = None

    def setUp(self):
        self.admin_token = self.get_admin_token()

    def test_01_TC_MOVIE_01_create_movie(self):
        payload = {"title": "Full Test Movie", "genre": "Action", "duration": 120, "release_date": "2026-01-01"}
        resp = self._request("TC_MOVIE_01", 'POST', f"{self.MOVIE_URL}/movies", payload, expected_status=201)
        TestMovieAndShowtime.movie_id = resp.json().get('id')

    def test_02_TC_MOVIE_02_get_all_movies(self):
        self._request("TC_MOVIE_02", 'GET', f"{self.MOVIE_URL}/movies")

    def test_03_TC_MOVIE_03_get_movie_detail(self):
        if not TestMovieAndShowtime.movie_id: self.skipTest("No movie created")
        self._request("TC_MOVIE_03", 'GET', f"{self.MOVIE_URL}/movies/{TestMovieAndShowtime.movie_id}")

    def test_04_TC_MOVIE_04_get_non_existent(self):
        self._request("TC_MOVIE_04", 'GET', f"{self.MOVIE_URL}/movies/999999", expected_status=404)

    def test_05_TC_MOVIE_05_update_movie(self):
        if not TestMovieAndShowtime.movie_id: self.skipTest("No movie created")
        payload = {"title": "Updated Title", "genre": "Drama", "duration": 130, "release_date": "2026-01-01"}
        self._request("TC_MOVIE_05", 'PUT', f"{self.MOVIE_URL}/movies/{TestMovieAndShowtime.movie_id}", payload)

    def test_06_TC_MOVIE_07_search_movies(self):
        self._request("TC_MOVIE_07", 'GET', f"{self.MOVIE_URL}/movies?query=Updated")

    def test_07_TC_SHOWTIME_01_create_showtime(self):
        if not TestMovieAndShowtime.movie_id: self.skipTest("No movie created")
        payload = {
            "movie_id": TestMovieAndShowtime.movie_id,
            "start_time": "2026-12-01 18:00", 
            "end_time": "2026-12-01 20:00",
            "total_seats": 20, 
            "price": 75000
        }
        resp = self._request("TC_SHOWTIME_01", 'POST', f"{self.MOVIE_URL}/showtimes", payload, expected_status=201)
        TestMovieAndShowtime.showtime_id = resp.json().get('id')

    def test_08_TC_SHOWTIME_02_get_showtimes(self):
        self._request("TC_SHOWTIME_02", 'GET', f"{self.MOVIE_URL}/showtimes?movie_id={TestMovieAndShowtime.movie_id}")

    def test_09_TC_SHOWTIME_04_update_showtime(self):
        if not TestMovieAndShowtime.showtime_id: self.skipTest("No showtime created")
        payload = {
            "start_time": "2026-12-01 19:00", 
            "end_time": "2026-12-01 21:00",
            "price": 80000
        }
        self._request("TC_SHOWTIME_04", 'PUT', f"{self.MOVIE_URL}/showtimes/{TestMovieAndShowtime.showtime_id}", payload)

    def test_10_TC_SHOWTIME_05_delete_showtime(self):
        if not TestMovieAndShowtime.showtime_id: self.skipTest("No showtime created")
        self._request("TC_SHOWTIME_05", 'DELETE', f"{self.MOVIE_URL}/showtimes/{TestMovieAndShowtime.showtime_id}")

    def test_11_TC_MOVIE_06_delete_movie(self):
        if not TestMovieAndShowtime.movie_id: self.skipTest("No movie created")
        self._request("TC_MOVIE_06", 'DELETE', f"{self.MOVIE_URL}/movies/{TestMovieAndShowtime.movie_id}")