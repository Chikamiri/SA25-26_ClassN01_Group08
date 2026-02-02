
const AdminDashboardPage = {
  render: () => {
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user || user.role !== 'admin') {
        return `
          <div class="container py-5 text-center">
            <div class="alert alert-danger d-inline-block">
              <h4 class="alert-heading">Truy cập bị từ chối!</h4>
              <p>Bạn không có quyền truy cập trang này.</p>
              <hr>
              <a href="/admin/login" class="btn btn-outline-danger btn-sm">Đăng nhập Admin</a>
            </div>
          </div>
        `;
    }

    return `
      <div class="container py-4">
        <h2 class="fw-bold mb-4">Bảng Điều Khiển Quản Trị</h2>
        
        <div class="row g-4">
          <div class="col-md-12">
            <div class="card bg-primary text-white shadow-sm mb-4">
              <div class="card-body p-4">
                <h4 class="card-title">Xin chào, ${user.email}!</h4>
                <p class="card-text">Hệ thống quản lý rạp chiếu phim đang hoạt động.</p>
              </div>
            </div>
          </div>
          
          <div class="col-md-6">
            <div class="card h-100 shadow-sm">
              <div class="card-header bg-white fw-bold py-3">Quản lý nội dung</div>
              <div class="list-group list-group-flush">
                <a href="/admin/movies/manage" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center">
                  <div>
                    <strong>Quản lý Phim</strong>
                    <div class="small text-muted">Thêm, sửa, xóa phim</div>
                  </div>
                  <span class="fs-4">🎬</span>
                </a>
                <a href="/admin/showtimes/manage" class="list-group-item list-group-item-action py-3 d-flex justify-content-between align-items-center">
                  <div>
                    <strong>Quản lý Lịch chiếu</strong>
                    <div class="small text-muted">Xếp lịch chiếu cho các phim</div>
                  </div>
                  <span class="fs-4">📅</span>
                </a>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card h-100 shadow-sm">
              <div class="card-header bg-white fw-bold py-3">Thống kê nhanh</div>
              <div class="card-body">
                 <p class="text-muted text-center py-5">Chức năng thống kê đang được phát triển...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  },
  afterRender: () => {}
};

export default AdminDashboardPage;
