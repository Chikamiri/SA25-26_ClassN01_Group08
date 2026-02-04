import { registerUser } from '../api/apiClient.js';

const RegisterPage = {
  render: () => {
    return `
      <div class="row justify-content-center mt-5">
        <div class="col-md-5 col-lg-4">
          <div class="card shadow-sm border-0">
            <div class="card-body p-4">
              <h2 class="text-center fw-bold mb-4">Đăng Ký</h2>
              <form id="register-form">
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input type="email" id="reg-email" class="form-control" placeholder="user@example.com" required>
                </div>
                <div class="mb-3">
                  <label class="form-label">Mật khẩu</label>
                  <input type="password" id="reg-password" class="form-control" placeholder="••••••••" required minlength="6">
                </div>
                <div class="mb-4">
                  <label class="form-label">Xác nhận mật khẩu</label>
                  <input type="password" id="reg-confirm-password" class="form-control" placeholder="••••••••" required>
                </div>
                <div class="d-grid">
                  <button type="submit" id="register-btn" class="btn btn-success py-2 fw-bold">Đăng Ký</button>
                </div>
              </form>
              <div id="reg-error-msg" class="text-danger mt-3 text-center small"></div>
              <div class="mt-4 text-center">
                <p class="text-muted small">Đã có tài khoản? <a href="/login" class="text-decoration-none">Đăng nhập ngay</a></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  },
  afterRender: () => {
    const form = document.getElementById('register-form');
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('reg-email').value;
      const password = document.getElementById('reg-password').value;
      const confirmPassword = document.getElementById('reg-confirm-password').value;
      const errorMsg = document.getElementById('reg-error-msg');
      const btn = document.getElementById('register-btn');

      if (password !== confirmPassword) {
          errorMsg.innerText = 'Mật khẩu xác nhận không khớp.';
          return;
      }

      btn.disabled = true;
      btn.innerText = 'Đang xử lý...';
      errorMsg.innerText = '';

      try {
        await registerUser({ email, password });
        alert('Đăng ký thành công! Vui lòng đăng nhập.');
        window.location.href = '/login';
      } catch (err) {
        console.error('Registration failed:', err);
        errorMsg.innerText = err.message || 'Đăng ký thất bại. Vui lòng thử lại.';
      } finally {
        btn.disabled = false;
        btn.innerText = 'Đăng Ký';
      }
    });
  }
};

export default RegisterPage;
