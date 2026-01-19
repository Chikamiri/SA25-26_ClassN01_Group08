// src/pages/AdminLoginPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../api/apiClient'; // Sử dụng cùng hàm loginUser

function AdminLoginPage({ onLogin }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await loginUser({ email, password });
      
      // Chỉ cho phép admin truy cập dashboard
      if (response.role === 'admin') {
        onLogin(response);
        navigate('/admin/dashboard'); // Chuyển hướng đến bảng điều khiển admin
        alert('Đăng nhập Admin thành công!');
      } else {
        // Nếu đăng nhập thành công nhưng không phải là admin
        setError('Bạn không có quyền truy cập trang quản trị.');
        alert('Bạn không có quyền truy cập trang này.');
      }

    } catch (err) {
      console.error('Admin login failed:', err);
      setError(err.message || 'Thông tin đăng nhập Admin không hợp lệ.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>Đăng Nhập Tài Khoản Quản Trị</h2>
      <p>Chỉ dành cho quản trị viên.</p>
      <div>
        <label>Email:</label><br />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="admin@example.com"
          disabled={isLoading}
        />
      </div>
      <div style={{ marginTop: '10px' }}>
        <label>Mật khẩu:</label><br />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="admin123"
          disabled={isLoading}
        />
      </div>
      <button onClick={handleLogin} disabled={isLoading} style={{ marginTop: '20px', padding: '10px 15px' }}>
        {isLoading ? 'Đang xử lý...' : 'Đăng nhập Admin'}
      </button>
      {error && <p style={{ color: 'red', marginTop: '15px' }}>{error}</p>}
       <p style={{ marginTop: '10px' }}>Tài khoản thử nghiệm: admin@example.com / admin123</p>
    </div>
  );
}

export default AdminLoginPage;