
const AdminDashboardPage = {
  render: () => {
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user || user.role !== 'admin') {
        return `<p>Bạn không có quyền truy cập trang này. <a href="/login">Đăng nhập</a></p>`;
    }

    return `
      <div>
        <h2>Bảng Điều Khiển Quản Trị</h2>
        <div>
          <p>Chào mừng, Quản trị viên ${user.email}!</p>
          <div style="margin-top: 30px;">
            <h4>Quản lý</h4>
            <ul style="list-style: none; padding: 0;">
              <li style="margin-bottom: 10px;">
                <a href="/admin/movies/manage" style="text-decoration: none; color: #007bff;">Quản lý Phim</a>
              </li>
              <li style="margin-bottom: 10px;">
                <a href="/admin/showtimes/manage" style="text-decoration: none; color: #007bff;">Quản lý Lịch chiếu</a>
              </li>
              <!-- Thêm các mục quản lý khác nếu cần -->
            </ul>
          </div>
        </div>
      </div>
    `;
  },
  afterRender: () => {}
};

export default AdminDashboardPage;
