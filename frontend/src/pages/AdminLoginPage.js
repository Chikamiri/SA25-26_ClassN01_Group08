import { loginUser } from '../api/apiClient.js';

const AdminLoginPage = {
  render: () => {
    return `
      <div>
        <h2>Đăng Nhập Tài Khoản Quản Trị</h2>
        <p>Chỉ dành cho quản trị viên.</p>
        <form id="admin-login-form">
          <div>
            <label>Email:</label><br />
            <input type="email" id="admin-email" placeholder="admin@example.com" required style="padding: 5px;">
          </div>
          <div style="margin-top: 10px;">
            <label>Mật khẩu:</label><br />
            <input type="password" id="admin-password" placeholder="admin123" required style="padding: 5px;">
          </div>
          <button type="submit" id="admin-login-btn" style="margin-top: 20px; padding: 10px 15px;">Đăng nhập Admin</button>
        </form>
        <p id="admin-error-msg" style="color: red; margin-top: 15px;"></p>
        <p style="margin-top: 10px;">Tài khoản thử nghiệm: admin@example.com / admin123</p>
      </div>
    `;
  },
  afterRender: () => {
    const form = document.getElementById('admin-login-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('admin-email').value;
      const password = document.getElementById('admin-password').value;
      const errorMsg = document.getElementById('admin-error-msg');
      const loginBtn = document.getElementById('admin-login-btn');

      loginBtn.disabled = true;
      loginBtn.innerText = 'Đang xử lý...';
      errorMsg.innerText = '';

      try {
        const response = await loginUser({ email, password });
        
        if (response.role === 'admin') {
            localStorage.setItem('user', JSON.stringify(response));
            alert('Đăng nhập Admin thành công!');
            window.location.href = '/admin/dashboard';
        } else {
             errorMsg.innerText = 'Bạn không có quyền truy cập trang quản trị.';
             alert('Bạn không có quyền truy cập trang này.');
        }

      } catch (err) {
        console.error('Admin login failed:', err);
        errorMsg.innerText = err.message || 'Thông tin đăng nhập Admin không hợp lệ.';
      } finally {
        loginBtn.disabled = false;
        loginBtn.innerText = 'Đăng nhập Admin';
      }
    });
  }
};

export default AdminLoginPage;
