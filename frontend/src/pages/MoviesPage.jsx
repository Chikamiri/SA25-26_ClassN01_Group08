// src/pages/MoviesPage.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getMovies } from '../api/apiClient'; // Import hàm lấy phim

function MoviesPage() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Sử dụng useCallback để tránh tạo lại hàm fetchMovies không cần thiết
  const fetchMovies = useCallback(async (query = '') => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMovies(query);
      setMovies(data);
    } catch (err) {
      setError(err.message || 'Không thể tải danh sách phim.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []); // [] đảm bảo hàm này chỉ được tạo một lần

  useEffect(() => {
    fetchMovies(searchTerm); // Gọi API khi component mount hoặc searchTerm thay đổi
  }, [fetchMovies, searchTerm]);

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  // Không cần handleSearch riêng nữa vì useEffect sẽ tự động chạy khi searchTerm thay đổi
  // Nếu muốn tìm kiếm thủ công khi nhấn nút, có thể giữ lại, nhưng auto-search thì không cần.

  if (loading) return <p>Đang tải danh sách phim...</p>;
  if (error) return <p>Lỗi: {error}</p>;
  if (movies.length === 0 && !loading && !error) return <p>Không tìm thấy phim nào.</p>;

  return (
    <div>
      <h2>Danh Sách Phim</h2>
      <div style={{ marginBottom: '20px' }}>
        <input
          type="text"
          placeholder="Tìm kiếm phim theo tiêu đề..."
          value={searchTerm}
          onChange={handleSearchChange}
          style={{ marginRight: '10px', padding: '8px' }}
        />
        {/* Nút tìm kiếm không còn cần thiết nếu tìm kiếm tự động theo onChange */}
        {/* <button onClick={() => fetchMovies(searchTerm)} style={{ padding: '8px 12px' }}>Tìm kiếm</button> */}
      </div>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {movies.map(movie => (
          <li key={movie.id} style={{ marginBottom: '15px', padding: '10px', border: '1px solid #eee', borderRadius: '5px' }}>
            <h3>
              <Link to={`/movies/${movie.id}`} style={{ textDecoration: 'none', color: '#007bff' }}>
                {movie.title}
              </Link>
            </h3>
            <p>Thể loại: {movie.genre}</p>
            <p>Thời lượng: {movie.duration} phút</p>
            <p>Ngày phát hành: {movie.release_date}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default MoviesPage;