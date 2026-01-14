import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from movie.persistence.movie_repository import MovieRepository
from movie.models.movie_model import Movie, Showtime

class TestMovieRepository(unittest.TestCase):

    # Patch sqlite3.connect as it's directly used by _get_connection
    @patch('movie.persistence.movie_repository.sqlite3.connect')
    # Patch _init_db to prevent it from creating tables with potential side effects.
    # _init_db calls _get_connection, which will be intercepted by the patch below.
    # Patching it directly ensures no actual table creation logic runs.
    @patch('movie.persistence.movie_repository.MovieRepository._init_db')
    def setUp(self, mock_init_db, mock_connect):
        """
        Set up mocks for sqlite3.connect, Connection, and Cursor objects.
        This method runs before each test method.
        """
        self.mock_connect = mock_connect
        
        # Create mock connection and cursor objects
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        
        # Configure the mocks:
        # 1. When sqlite3.connect() is called, return self.mock_conn
        self.mock_connect.return_value = self.mock_conn
        
        # 2. When self.mock_conn.cursor() is called, return self.mock_cursor
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        # 3. Mock methods on the connection object that are used:
        self.mock_conn.commit = MagicMock()
        self.mock_conn.close = MagicMock()
        # Mock conn.execute used in update methods
        self.mock_conn.execute = MagicMock()

        # 4. Mock methods and attributes on the cursor object that are used:
        self.mock_cursor.execute = MagicMock() # Explicitly mock cursor.execute
        self.mock_cursor.fetchone = MagicMock()
        self.mock_cursor.fetchall = MagicMock()
        # For rowcount, MagicMock handles attribute access; values will be set per test.

        # Instantiate the repository. 
        # _init_db is patched, and sqlite3.connect is mocked, so no real DB access happens.
        self.repo = MovieRepository()

        # Reset all mocks before each test to ensure isolation
        # This is crucial to avoid state leakage between tests.
        self.mock_connect.reset_mock()
        self.mock_conn.reset_mock()
        self.mock_cursor.reset_mock()
        
        # Re-apply the return_value for the connection and cursor mocks after resetting
        self.mock_connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        # Also re-mock execute methods on cursor and conn as they might be called during init
        self.mock_cursor.execute = MagicMock()
        self.mock_conn.execute = MagicMock()


    def test_add_movie_with_id(self):
        """Test adding a movie with a provided ID."""
        movie_id = 1
        self.repo.add_movie(movie_id, "Test Movie", "Action", 120, "2024-01-01")
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with(
            'INSERT INTO movies (id, title, genre, duration, release_date) VALUES (?, ?, ?, ?, ?)',
            (movie_id, "Test Movie", "Action", 120, "2024-01-01")
        )
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()

    def test_add_movie_without_id(self):
        """Test adding a movie without providing an ID (auto-generated)."""
        self.mock_cursor.lastrowid = 1 # Mock for auto-generated ID
        
        new_id = self.repo.add_movie(None, "Another Movie", "Comedy", 90, "2024-02-01")
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with(
            'INSERT INTO movies (title, genre, duration, release_date) VALUES (?, ?, ?, ?)',
            ("Another Movie", "Comedy", 90, "2024-02-01")
        )
        self.assertEqual(new_id, 1)
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()

    def test_get_movie_found(self):
        """Test retrieving an existing movie."""
        self.mock_cursor.fetchone.return_value = (1, "Test Movie", "Action", 120, "2024-01-01")
        
        movie = self.repo.get_movie(1)
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with('SELECT * FROM movies WHERE id = ?', (1,))
        self.assertIsNotNone(movie)
        self.assertEqual(movie.id, 1)
        self.assertEqual(movie.title, "Test Movie")
        self.mock_conn.close.assert_called_once()

    def test_get_movie_not_found(self):
        """Test retrieving a non-existent movie."""
        self.mock_cursor.fetchone.return_value = None
        
        movie = self.repo.get_movie(99)
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with('SELECT * FROM movies WHERE id = ?', (99,))
        self.assertIsNone(movie)
        self.mock_conn.close.assert_called_once()

    def test_get_all_movies(self):
        """Test retrieving all movies."""
        self.mock_cursor.fetchall.return_value = [
            (1, "Movie 1", "Action", 100, "2024-01-01"),
            (2, "Movie 2", "Comedy", 90, "2024-01-02")
        ]
        
        movies = self.repo.get_all_movies()
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with('SELECT * FROM movies')
        self.assertEqual(len(movies), 2)
        self.assertEqual(movies[0].title, "Movie 1")
        self.mock_conn.close.assert_called_once()

    def test_search_movies(self):
        """Test searching for movies by title."""
        self.mock_cursor.fetchall.return_value = [
            (1, "Inception", "Sci-Fi", 148, "2010-07-16")
        ]
        
        movies = self.repo.search_movies("Inception")
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with("SELECT * FROM movies WHERE title LIKE ?", ('%Inception%',))
        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0].title, "Inception")
        self.mock_conn.close.assert_called_once()

    def test_update_movie(self):
        """Test updating an existing movie."""
        self.repo.update_movie(1, "Updated Title", "Drama", 130, "2024-03-01")
        
        self.mock_connect.assert_called_once()
        self.mock_conn.execute.assert_called_once_with(
            'UPDATE movies SET title = ?, genre = ?, duration = ?, release_date = ? WHERE id = ?',
            ("Updated Title", "Drama", 130, "2024-03-01", 1)
        )
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()

    def test_delete_movie_no_showtimes(self):
        """Test deleting a movie when it has no associated showtimes."""
        self.mock_cursor.fetchone.return_value = (0,) # Simulate no showtimes
        self.mock_cursor.rowcount = 1 # Simulate one row deleted from movies table

        result = self.repo.delete_movie(1)

        self.assertTrue(result)
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called() # cursor should be called twice for SELECT COUNT and DELETE
        self.mock_cursor.execute.assert_any_call('SELECT COUNT(*) FROM showtimes WHERE movie_id = ?', (1,))
        self.mock_cursor.execute.assert_any_call('DELETE FROM movies WHERE id = ?', (1,))
        self.assertEqual(self.mock_cursor.execute.call_count, 2)
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()

    def test_delete_movie_with_showtimes(self):
        """Test attempting to delete a movie that has associated showtimes."""
        self.mock_cursor.fetchone.return_value = (5,) # Simulate showtimes exist

        result = self.repo.delete_movie(1)

        self.assertFalse(result)
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        # Verify only the SELECT COUNT call was made, not the DELETE
        self.mock_cursor.execute.assert_any_call('SELECT COUNT(*) FROM showtimes WHERE movie_id = ?', (1,))
        self.assertEqual(self.mock_cursor.execute.call_count, 1) # Ensure only one execute call happened
        self.mock_conn.commit.assert_not_called()
        self.mock_conn.close.assert_called_once()

    def test_add_showtime_with_id(self):
        """Test adding a showtime with a provided ID."""
        showtime_id = 1
        self.repo.add_showtime(showtime_id, 1, "10:00", "12:00")
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with(
            'INSERT INTO showtimes (id, movie_id, start_time, end_time) VALUES (?, ?, ?, ?)',
            (showtime_id, 1, "10:00", "12:00")
        )
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()

    def test_add_showtime_without_id(self):
        """Test adding a showtime without providing an ID."""
        self.mock_cursor.lastrowid = 1 # Mock for auto-generated ID
        
        new_id = self.repo.add_showtime(None, 1, "13:00", "15:00")
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with(
            'INSERT INTO showtimes (movie_id, start_time, end_time) VALUES (?, ?, ?)',
            (1, "13:00", "15:00")
        )
        self.assertEqual(new_id, 1)
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()

    def test_get_showtime_found(self):
        """Test retrieving an existing showtime."""
        self.mock_cursor.fetchone.return_value = (1, 1, "10:00", "12:00")
        
        showtime = self.repo.get_showtime(1)
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with('SELECT * FROM showtimes WHERE id = ?', (1,))
        self.assertIsNotNone(showtime)
        self.assertEqual(showtime.id, 1)
        self.assertEqual(showtime.movie_id, 1)
        self.mock_conn.close.assert_called_once()

    def test_get_showtime_not_found(self):
        """Test retrieving a non-existent showtime."""
        self.mock_cursor.fetchone.return_value = None
        
        showtime = self.repo.get_showtime(99)
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with('SELECT * FROM showtimes WHERE id = ?', (99,))
        self.assertIsNone(showtime)
        self.mock_conn.close.assert_called_once()

    def test_get_all_showtimes(self):
        """Test retrieving all showtimes."""
        self.mock_cursor.fetchall.return_value = [
            (1, 1, "10:00", "12:00"),
            (2, 1, "13:00", "15:00")
        ]
        
        showtimes = self.repo.get_all_showtimes()
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with('SELECT * FROM showtimes')
        self.assertEqual(len(showtimes), 2)
        self.assertEqual(showtimes[0].movie_id, 1)
        self.mock_conn.close.assert_called_once()

    def test_get_all_showtimes_by_movie_id(self):
        """Test retrieving showtimes for a specific movie."""
        self.mock_cursor.fetchall.return_value = [
            (1, 1, "10:00", "12:00")
        ]
        
        showtimes = self.repo.get_all_showtimes(movie_id=1)
        
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with('SELECT * FROM showtimes WHERE movie_id = ?', (1,))
        self.assertEqual(len(showtimes), 1)
        self.assertEqual(showtimes[0].movie_id, 1)
        self.mock_conn.close.assert_called_once()

    def test_update_showtime(self):
        """Test updating an existing showtime."""
        self.repo.update_showtime(1, "11:00", "13:00")
        
        self.mock_connect.assert_called_once()
        self.mock_conn.execute.assert_called_once_with(
            'UPDATE showtimes SET start_time = ?, end_time = ? WHERE id = ?',
            ("11:00", "13:00", 1)
        )
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()

    def test_delete_showtime(self):
        """Test deleting an existing showtime."""
        self.mock_cursor.rowcount = 1 # Simulate one row deleted

        result = self.repo.delete_showtime(1)

        self.assertTrue(result)
        self.mock_connect.assert_called_once()
        self.mock_conn.cursor.assert_called_once()
        self.mock_cursor.execute.assert_called_once_with('DELETE FROM showtimes WHERE id = ?', (1,))
        self.mock_conn.commit.assert_called_once()
        self.mock_conn.close.assert_called_once()
