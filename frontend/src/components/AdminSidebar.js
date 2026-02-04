const AdminSidebar = {
  render: (activePage = 'dashboard') => {
    return `
      <div class="admin-sidebar">
        <div class="sidebar-header">
          <i class="bi bi-film"></i> Admin Panel
        </div>
        <nav class="nav flex-column mt-3">
          <a class="nav-link ${activePage === 'dashboard' ? 'active' : ''}" href="/admin/dashboard">
            <i class="bi bi-speedometer2"></i> Dashboard
          </a>
          <a class="nav-link ${activePage === 'movies' ? 'active' : ''}" href="/admin/movies/manage">
            <i class="bi bi-camera-reels"></i> Quản lý Phim
          </a>
          <a class="nav-link ${activePage === 'showtimes' ? 'active' : ''}" href="/admin/showtimes/manage">
            <i class="bi bi-calendar-week"></i> Quản lý Lịch chiếu
          </a>
          <a class="nav-link text-muted" href="#" onclick="alert('Tính năng đang phát triển')">
            <i class="bi bi-ticket-detailed"></i> Quản lý Đặt vé
          </a>
          <a class="nav-link text-muted" href="#" onclick="alert('Tính năng đang phát triển')">
             <i class="bi bi-people"></i> Quản lý Users
          </a>
        </nav>
        
        <div class="user-info">
          <div class="d-grid">
            <button id="admin-logout-btn" class="btn btn-outline-light btn-sm">
              <i class="bi bi-box-arrow-left"></i> Đăng xuất
            </button>
          </div>
        </div>
      </div>
    `;
  },
  afterRender: () => {
    const logoutBtn = document.getElementById('admin-logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            if(confirm('Bạn có chắc chắn muốn đăng xuất?')) {
                localStorage.removeItem('user');
                window.location.href = '/';
            }
        });
    }
  }
};

export default AdminSidebar;
