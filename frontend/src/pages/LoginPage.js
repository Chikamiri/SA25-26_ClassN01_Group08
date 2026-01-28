import { loginUser } from '../api/apiClient.js';

const LoginPage = {
  render: () => {
    return `
      <div>
        <h2>Đăng Nhập Hệ Thống</h2>
        <p>Vui lòng đăng nhập để tiếp tục.</p>
        <form id="login-form">
          <div>
            <label>Email:</label><br />
            <input type="email" id="email" placeholder="user@example.com" required style="padding: 5px;">
          </div>
          <div style="margin-top: 10px;">
            <label>Mật khẩu:</label><br />
            <input type="password" id="password" placeholder="password123" required style="padding: 5px;">
          </div>
          <button type="submit" id="login-btn" style="margin-top: 20px; padding: 10px 15px;">Đăng nhập</button>
        </form>
        <p id="error-msg" style="color: red; margin-top: 15px;"></p>
        <p style="margin-top: 10px;">Tài khoản thử nghiệm: user@example.com / password123</p>
      </div>
    `;
  },
  afterRender: () => {
    const form = document.getElementById('login-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      const errorMsg = document.getElementById('error-msg');
      const loginBtn = document.getElementById('login-btn');

      loginBtn.disabled = true;
      loginBtn.innerText = 'Đang xử lý...';
      errorMsg.innerText = '';

      try {
        const response = await loginUser({ username: email, password });
        localStorage.setItem('user', JSON.stringify(response));
        alert('Đăng nhập thành công!');
        window.location.href = '/'; // Redirect về trang chủ
      } catch (err) {
        console.error('Login failed:', err);
        errorMsg.innerText = err.message || 'Đã xảy ra lỗi khi đăng nhập. Vui lòng thử lại.';
      } finally {
        loginBtn.disabled = false;
        loginBtn.innerText = 'Đăng nhập';
      }
    });
  }
};

export default LoginPage;
