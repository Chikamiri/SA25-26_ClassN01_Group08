// src/pages/AdminDashboardPage.jsx
import React from 'react';
import { Link } from 'react-router-dom';

function AdminDashboardPage() {
  // TODO: Lấy thông tin admin nếu cần thiết
  const user = JSON.parse(localStorage.getItem('user'));

  return (
    <div>
      <h2>Bảng Điều Khiển Quản Trị</h2>
      {user && user.role === 'admin' ? (
        <div>
          <p>Chào mừng, Quản trị viên {user.email}!</p>
          <div style={{ marginTop: '30px' }}>
            <h4>Quản lý</h4>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li style={{ marginBottom: '10px' }}>
                <Link to="/admin/movies/manage" style={{ textDecoration: 'none', color: '#007bff' }}>Quản lý Phim</Link>
              </li>
              <li style={{ marginBottom: '10px' }}>
                <Link to="/admin/showtimes/manage" style={{ textDecoration: 'none', color: '#007bff' }}>Quản lý Lịch chiếu</Link>
              </li>
              {/* Thêm các mục quản lý khác nếu cần */}
            </ul>
          </div>
        </div>
      ) : (
        <p>Bạn không có quyền truy cập trang này.</p>
      )}
    </div>
  );
}

export default AdminDashboardPage;