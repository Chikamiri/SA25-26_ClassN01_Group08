import { getMyBookings, deleteBooking } from '../api/apiClient.js';

const MyBookingsPage = {
  render: async () => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        return `
          <div class="container py-5 text-center">
            <div class="alert alert-warning d-inline-block">
              Vui lòng <a href="/login" class="alert-link">đăng nhập</a> để xem các vé đã đặt.
            </div>
          </div>
        `;
    }

    return `
      <div class="container py-4">
        <h2 class="fw-bold mb-4">Các Vé Đã Đặt</h2>
        <div id="bookings-list-container">
            <div class="text-center py-5">
              <div class="spinner-border text-primary" role="status"></div>
            </div>
        </div>
      </div>
    `;
  },
  afterRender: async () => {
    const container = document.getElementById('bookings-list-container');
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user) return;

    const loadBookings = async () => {
        try {
            const bookings = await getMyBookings();
            
            if (!bookings || bookings.length === 0) {
                container.innerHTML = `
                  <div class="card border-0 shadow-sm text-center p-5">
                    <p class="text-muted mb-0">Bạn chưa có vé nào được đặt. <a href="/movies">Khám phá phim ngay!</a></p>
                  </div>
                `;
                return;
            }

            container.innerHTML = `
                <div class="table-responsive bg-white rounded shadow-sm">
                  <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                      <tr>
                        <th class="ps-4">Mã Đặt Vé</th>
                        <th>Suất Chiếu</th>
                        <th>Chỗ Ngồi</th>
                        <th>Giá Vé</th>
                        <th>Trạng Thái</th>
                        <th class="text-end pe-4">Hành Động</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${bookings.map(booking => {
                        const isPending = booking.status === 'PENDING_PAYMENT';
                        return `
                        <tr>
                          <td class="ps-4 fw-bold text-secondary">#${booking.id}</td>
                          <td>ID: ${booking.showtime_id}</td>
                          <td><span class="badge bg-light text-dark border">${booking.seat_number}</span></td>
                          <td>${booking.amount ? booking.amount.toLocaleString() : '0'} VND</td>
                          <td>
                            <span class="badge ${booking.status === 'confirmed' ? 'bg-success' : 'bg-warning text-dark'}">
                              ${booking.status === 'confirmed' ? 'Đã Thanh Toán' : 'Chờ Thanh Toán'}
                            </span>
                          </td>
                          <td class="text-end pe-4">
                             ${isPending ? `
                                <a href="/payment?booking_ids=${booking.id}&amount=${booking.amount}" class="btn btn-sm btn-primary me-2">
                                    Thanh Toán
                                </a>
                             ` : ''}
                             <button class="btn btn-sm btn-outline-danger cancel-btn" data-id="${booking.id}">
                                Hủy Vé
                             </button>
                          </td>
                        </tr>
                      `}).join('')}
                    </tbody>
                  </table>
                </div>
            `;

            // Attach Event Listeners
            document.querySelectorAll('.cancel-btn').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = e.target.dataset.id;
                    if (confirm(`Bạn có chắc chắn muốn hủy vé #${id}?`)) {
                        try {
                            await deleteBooking(id);
                            alert('Đã hủy vé thành công.');
                            loadBookings(); // Reload list
                        } catch (err) {
                            alert('Lỗi khi hủy vé: ' + err.message);
                        }
                    }
                });
            });

        } catch (err) {
            console.error('Failed to fetch bookings:', err);
            container.innerHTML = `<div class="alert alert-danger">Không thể tải danh sách vé đã đặt: ${err.message}</div>`;
        }
    };

    await loadBookings();
  }
};

export default MyBookingsPage;
