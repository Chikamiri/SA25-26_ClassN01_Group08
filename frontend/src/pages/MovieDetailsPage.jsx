// src/pages/MovieDetailsPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getMovieById, getShowtimes } from '../api/apiClient'; // Import các hàm API mới

function MovieDetailsPage() {
  const { id } = useParams(); // Lấy movie_id từ URL
  const navigate = useNavigate();
  const [movie, setMovie] = useState(null);
  const [showtimes, setShowtimes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      setLoading(true);
      setError(null);
      try {
        // Lấy thông tin phim
        const movieData = await getMovieById(id);
        setMovie(movieData);

        // Lấy danh sách suất chiếu cho phim này
        const showtimeData = await getShowtimes(id);
        setShowtimes(showtimeData);

      } catch (err) {
        setError(err.message || 'Không thể tải thông tin phim hoặc suất chiếu.');
        console.error('Error fetching movie details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [id]); // Fetch lại khi id của phim thay đổi

  if (loading) return <p>Đang tải chi tiết phim...</p>;
  if (error) return <p>Lỗi: {error}</p>;
  if (!movie) return <p>Phim không tìm thấy.</p>;

  return (
    <div>
      <h2>{movie.title}</h2>
      <p><strong>Thể loại:</strong> {movie.genre}</p>
      <p><strong>Thời lượng:</strong> {movie.duration} phút</p>
      <p><strong>Ngày phát hành:</strong> {movie.release_date}</p>
      <p><strong>Mô tả:</strong> {movie.description || 'Không có mô tả.'}</p>

      <h3 style={{ marginTop: '30px' }}>Các Suất Chiếu</h3>
      {showtimes.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {showtimes.map(st => (
            <li key={st.id} style={{ marginBottom: '10px', padding: '10px', border: '1px solid #ddd', borderRadius: '5px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <p><strong>Thời gian:</strong> {st.start_time} - {st.end_time}</p>
                <p><strong>Giá vé:</strong> {st.price ? st.price.toLocaleString() : 'N/A'} VND</p>
              </div>
              <Link to={`/book/${st.id}`} style={{ padding: '8px 12px', backgroundColor: '#28a745', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>
                Đặt vé
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p>Hiện không có suất chiếu nào cho phim này.</p>
      )}

      <div style={{ marginTop: '30px' }}>
        <Link to="/movies" style={{ textDecoration: 'none', color: '#6c757d', marginRight: '10px' }}>&larr; Quay lại danh sách phim</Link>
      </div>
    </div>
  );
}

export default MovieDetailsPage;