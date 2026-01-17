// src/pages/LoginPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loginUser } from '../api/apiClient'; // Import hàm đăng nhập

function LoginPage({ onLogin }) {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    setIsLoading(true);
    setError(''); // Xóa lỗi cũ

    try {
      const response = await loginUser({ email, password });
      
      // Nếu đăng nhập thành công, response sẽ chứa token, role, email
      onLogin(response);
      navigate('/'); // Chuyển hướng về trang chủ
      alert('Đăng nhập thành công!');

    } catch (err) {
      // Lỗi có thể đến từ API (ví dụ: thông tin sai) hoặc lỗi mạng
      console.error('Login failed:', err);
      setError(err.message || 'Đã xảy ra lỗi khi đăng nhập. Vui lòng thử lại.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h2>Đăng Nhập Hệ Thống</h2>
      <p>Vui lòng đăng nhập để tiếp tục.</p>
      <div>
        <label>Email:</label><br />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="user@example.com"
          disabled={isLoading}
        />
      </div>
      <div style={{ marginTop: '10px' }}>
        <label>Mật khẩu:</label><br />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password123"
          disabled={isLoading}
        />
      </div>
      <button onClick={handleLogin} disabled={isLoading} style={{ marginTop: '20px', padding: '10px 15px' }}>
        {isLoading ? 'Đang xử lý...' : 'Đăng nhập'}
      </button>
      {error && <p style={{ color: 'red', marginTop: '15px' }}>{error}</p>}
      <p style={{ marginTop: '10px' }}>Tài khoản thử nghiệm: user@example.com / password123</p>
    </div>
  );
}

export default LoginPage;