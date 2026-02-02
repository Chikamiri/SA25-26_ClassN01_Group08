import { loginUser } from '../api/apiClient.js';

const AdminLoginPage = {
  render: () => {
    return `
      <div class="row justify-content-center mt-5">
        <div class="col-md-5 col-lg-4">
          <div class="card shadow border-0">
            <div class="card-header bg-danger text-white text-center py-3">
              <h4 class="mb-0 fw-bold">Admin Login</h4>
            </div>
            <div class="card-body p-4">
              <p class="text-muted text-center mb-4">Khu vực dành riêng cho quản trị viên.</p>
              <form id="admin-login-form">
                <div class="mb-3">
                  <label class="form-label">Username / Email</label>
                  <input type="text" id="admin-email" class="form-control" placeholder="admin" required>
                </div>
                <div class="mb-4">
                  <label class="form-label">Mật khẩu</label>
                  <input type="password" id="admin-password" class="form-control" placeholder="••••••••" required>
                </div>
                <div class="d-grid">
                  <button type="submit" id="admin-login-btn" class="btn btn-danger py-2 fw-bold">Đăng nhập Admin</button>
                </div>
              </form>
              <div id="admin-error-msg" class="text-danger mt-3 text-center small"></div>
              <div class="mt-4 p-3 bg-light rounded small border">
                <p class="mb-0 text-muted"><strong>Tài khoản mặc định:</strong><br>admin / 111111</p>
              </div>
            </div>
          </div>
        </div>
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
        const response = await loginUser({ username: email, password });
        
        if (response.role === 'admin') {
            localStorage.setItem('user', JSON.stringify(response));
            window.location.href = '/admin/dashboard';
        } else {
             errorMsg.innerText = 'Tài khoản này không có quyền quản trị.';
             // logout if accidentally logged in as user
             localStorage.removeItem('user');
        }

      } catch (err) {
        console.error('Admin login failed:', err);
        errorMsg.innerText = err.message || 'Thông tin đăng nhập không hợp lệ.';
      } finally {
        loginBtn.disabled = false;
        loginBtn.innerText = 'Đăng nhập Admin';
      }
    });
  }
};

export default AdminLoginPage;
