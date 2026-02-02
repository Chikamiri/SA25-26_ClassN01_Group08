const HomePage = {
  render: () => {
    const user = JSON.parse(localStorage.getItem('user'));

    return `
      <div class="container text-center py-5 mt-5 bg-light rounded-3 border shadow-sm">
        <h1 class="display-4 fw-bold">Chào mừng đến với MovieBook</h1>
        <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
          <a href="/movies" class="btn btn-primary btn-lg px-4 gap-3">Xem Phim Ngay</a>
          ${!user ? `
            <a href="/login" class="btn btn-outline-secondary btn-lg px-4">Đăng Nhập</a>
          ` : `
            ${user.role === 'admin' ? `
              <a href="/admin/dashboard" class="btn btn-outline-warning btn-lg px-4 text-dark">Vào Trang Quản Trị</a>
            ` : `
              <a href="/my-bookings" class="btn btn-outline-success btn-lg px-4">Vé Của Tôi</a>
            `}
          `}
        </div>
      </div>
    `;
  },
  afterRender: () => { }
};

export default HomePage;
