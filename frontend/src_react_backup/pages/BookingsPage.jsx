// src/pages/BookingsPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { bookTicket } from '../api/apiClient'; // Import hàm đặt vé

function BookingsPage() {
  const { showtimeId } = useParams(); // Lấy showtimeId từ URL
  const navigate = useNavigate();
  const [seatNumber, setSeatNumber] = useState('');
  const [bookingDetails, setBookingDetails] = useState(null); // Thông tin chi tiết sau khi đặt vé
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Lấy thông tin người dùng từ localStorage (giả lập)
  const user = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    // Nếu chưa đăng nhập, chuyển hướng về trang đăng nhập
    if (!user) {
      alert('Bạn cần đăng nhập để đặt vé.');
      navigate('/login');
    }
  }, [user, navigate]); // Chạy lại khi user hoặc navigate thay đổi

  const handleBookTicket = async () => {
    // Kiểm tra lại lần nữa, mặc dù đã có redirect ở useEffect
    if (!user) {
      alert('Bạn cần đăng nhập để đặt vé.');
      navigate('/login');
      return;
    }
    if (!seatNumber) {
      alert('Vui lòng nhập số ghế.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const bookingData = {
        showtime_id: parseInt(showtimeId),
        seat_number: seatNumber,
        // Email của người dùng sẽ được thêm vào header bởi hàm request trong apiClient.js
      };

      const response = await bookTicket(bookingData);
      
      // response từ API Gateway sẽ có cấu trúc như: { message, booking_id, price, movie }
      setBookingDetails(response);
      alert('Đặt vé thành công!');
      // Tùy chọn: chuyển hướng hoặc hiển thị chi tiết đặt vé
      // navigate('/my-bookings'); // Có thể chuyển hướng đến trang vé của tôi

    } catch (err) {
      console.error('Booking failed:', err);
      setError(err.message || 'Đã xảy ra lỗi khi đặt vé.');
      alert(`Đặt vé thất bại: ${err.message || 'Đã xảy ra lỗi.'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Đặt Vé</h2>
      <p>Suất chiếu ID: {showtimeId}</p>
      {user && (
        <p>Người dùng: {user.email} ({user.role})</p>
      )}

      {!bookingDetails ? (
        <div>
          <div style={{ marginTop: '20px' }}>
            <label>Nhập số ghế bạn muốn đặt:</label><br />
            <input
              type="text"
              value={seatNumber}
              onChange={(e) => setSeatNumber(e.target.value.trim())}
              placeholder="Ví dụ: A1, B5, 23"
              style={{ padding: '8px', marginRight: '10px' }}
              disabled={loading || !user}
            />
            <button onClick={handleBookTicket} disabled={loading || !seatNumber || !user} style={{ padding: '10px 15px' }}>
              {loading ? 'Đang xử lý...' : 'Xác nhận Đặt vé'}
            </button>
          </div>
          {error && <p style={{ color: 'red', marginTop: '15px' }}>{error}</p>}
        </div>
      ) : (
        <div style={{ marginTop: '20px', padding: '15px', border: '1px solid #28a745', borderRadius: '5px', backgroundColor: '#d4edda', color: '#155724' }}>
          <h3>Đặt vé thành công!</h3>
          <p><strong>Mã đặt vé:</strong> #{bookingDetails.booking_id}</p>
          <p><strong>Phim:</strong> {bookingDetails.movie}</p>
          <p><strong>Chỗ ngồi:</strong> {seatNumber}</p>
          <p><strong>Giá vé:</strong> {bookingDetails.price ? bookingDetails.price.toLocaleString() : 'N/A'} VND</p>
          <button onClick={() => navigate('/my-bookings')} style={{ marginTop: '10px', padding: '8px 12px' }}>
            Xem các vé đã đặt
          </button>
        </div>
      )}
       <p style={{ marginTop: '20px' }}>
        <Link to="/movies" style={{ textDecoration: 'none', color: '#6c757d', marginRight: '10px' }}>&larr; Quay lại danh sách phim</Link>
      </p>
    </div>
  );
}

export default BookingsPage;