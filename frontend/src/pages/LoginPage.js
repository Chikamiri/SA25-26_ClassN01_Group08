import { loginUser } from '../api/apiClient.js';

const LoginPage = {
  render: () => {
    return `
      <div class="row justify-content-center mt-5">
        <div class="col-md-5 col-lg-4">
          <div class="card shadow-sm border-0">
            <div class="card-body p-4">
              <h2 class="text-center fw-bold mb-4">Đăng Nhập</h2>
              <form id="login-form">
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input type="email" id="email" class="form-control" placeholder="user@example.com" required>
                </div>
                <div class="mb-4">
                  <label class="form-label">Mật khẩu</label>
                  <input type="password" id="password" class="form-control" placeholder="••••••••" required>
                </div>
                <div class="d-grid">
                  <button type="submit" id="login-btn" class="btn btn-primary py-2 fw-bold">Đăng nhập</button>
                </div>
              </form>
              <div id="error-msg" class="text-danger mt-3 text-center small"></div>
              <div class="mt-4 p-3 bg-light rounded small">
                <p class="mb-0 text-muted"><strong>Tài khoản thử nghiệm:</strong><br>user@example.com / password123</p>
              </div>
              <div class="mt-3 text-center">
                <p class="text-muted small">Chưa có tài khoản? <a href="/register" class="text-decoration-none">Đăng ký ngay</a></p>
              </div>
            </div>
          </div>
        </div>
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
        window.location.href = '/'; 
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
