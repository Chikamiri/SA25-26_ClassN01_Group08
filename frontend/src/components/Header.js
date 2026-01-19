
const Header = {
  render: () => {
    const user = JSON.parse(localStorage.getItem('user'));
    return `
      <nav style="padding: 10px; background-color: #f0f0f0; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <a href="/" class="nav-link" style="margin-right: 15px; text-decoration: none; color: #333;">Trang Chủ</a>
          <a href="/movies" class="nav-link" style="margin-right: 15px; text-decoration: none; color: #333;">Phim</a>
          ${user && user.role === 'customer' ? `
            <a href="/my-bookings" class="nav-link" style="margin-right: 15px; text-decoration: none; color: #333;">Vé Của Tôi</a>
          ` : ''}
          ${user && user.role === 'admin' ? `
            <a href="/admin/dashboard" class="nav-link" style="margin-right: 15px; text-decoration: none; color: #333;">Admin</a>
          ` : ''}
        </div>
        <div>
          ${!user ? `
            <a href="/login" class="nav-link" style="margin-right: 15px; text-decoration: none; color: #333;">Đăng Nhập</a>
            <a href="/admin/login" class="nav-link" style="text-decoration: none; color: #333;">Đăng Nhập Admin</a>
          ` : `
            <div style="display: flex; align-items: center;">
              <span style="margin-right: 15px; color: #333;">Xin chào, ${user.email} (${user.role})</span>
              <button id="logout-btn" style="padding: 5px 10px; cursor: pointer;">Đăng xuất</button>
            </div>
          `}
        </div>
      </nav>
    `;
  },
  afterRender: () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('user');
        alert('Bạn đã đăng xuất.');
        window.location.href = '/'; // Reload trang để reset state nhanh nhất cho Vanilla JS đơn giản
      });
    }
  }
};

export default Header;
