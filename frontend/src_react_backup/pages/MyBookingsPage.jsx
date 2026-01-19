// src/pages/MyBookingsPage.jsx
import React, { useState, useEffect } from 'react';

function MyBookingsPage() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Giả lập thông tin người dùng đã đăng nhập
  const user = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    const fetchMyBookings = async () => {
      if (!user) {
        setError('Bạn cần đăng nhập để xem các vé đã đặt.');
        setLoading(false);
        return;
      }

      try {
        // TODO: Gọi API Gateway '/api/bookings' (hoặc một endpoint lấy bookings của user hiện tại)
        // Giả lập dữ liệu vé
        await new Promise(resolve => setTimeout(resolve, 500));
        const dummyBookings = [
          { booking_id: 1001, movie: 'Inception', showtime: '2026-01-17 19:00', seat: 'A5', price: 100000, status: 'PAID' },
          { booking_id: 1002, movie: 'The Dark Knight', showtime: '2026-01-17 20:00', seat: 'B10', price: 120000, status: 'PAID' },
        ];
        setBookings(dummyBookings);
      } catch (err) {
        setError('Không thể tải danh sách vé đã đặt.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchMyBookings();
  }, [user]); // Fetch lại nếu user thay đổi

  if (loading) return <p>Đang tải danh sách vé của bạn...</p>;
  if (error) return <p>Lỗi: {error}</p>;
  if (!user) return <p>Vui lòng <a href="/login">đăng nhập</a> để xem các vé đã đặt.</p>;

  return (
    <div>
      <h2>Các Vé Đã Đặt Của Bạn</h2>
      {bookings.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {bookings.map(booking => (
            <li key={booking.booking_id} style={{ marginBottom: '15px', padding: '15px', border: '1px solid #ccc', borderRadius: '5px' }}>
              <p><strong>Mã đặt vé:</strong> #{booking.booking_id}</p>
              <p><strong>Phim:</strong> {booking.movie}</p>
              <p><strong>Suất chiếu:</strong> {booking.showtime}</p>
              <p><strong>Chỗ ngồi:</strong> {booking.seat}</p>
              <p><strong>Giá vé:</strong> {booking.price.toLocaleString()} VND</p>
              <p><strong>Trạng thái:</strong> {booking.status}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>Bạn chưa có vé nào được đặt.</p>
      )}
    </div>
  );
}

export default MyBookingsPage;