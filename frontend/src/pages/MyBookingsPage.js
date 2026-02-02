import { getMyBookings } from '../api/apiClient.js';

const MyBookingsPage = {
  render: async () => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) {
        return `<p>Vui lòng <a href="/login">đăng nhập</a> để xem các vé đã đặt.</p>`;
    }

    return `
      <div>
        <h2>Các Vé Đã Đặt Của Bạn</h2>
        <div id="bookings-list-container">
            Đang tải...
        </div>
      </div>
    `;
  },
  afterRender: async () => {
    const container = document.getElementById('bookings-list-container');
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user) return;

    try {
        const bookings = await getMyBookings();
        
        if (!bookings || bookings.length === 0) {
            container.innerHTML = '<p>Bạn chưa có vé nào được đặt.</p>';
            return;
        }

        container.innerHTML = `
            <ul style="list-style: none; padding: 0;">
                ${bookings.map(booking => `
                    <li style="margin-bottom: 15px; padding: 15px; border: 1px solid #ccc; border-radius: 5px;">
                        <p><strong>Mã đặt vé:</strong> #${booking.id}</p>
                        <p><strong>Suất chiếu ID:</strong> ${booking.showtime_id}</p>
                        <p><strong>Chỗ ngồi:</strong> ${booking.seat_number}</p>
                        <p><strong>Giá vé:</strong> ${booking.amount ? booking.amount.toLocaleString() : '0'} VND</p>
                        <p><strong>Trạng thái:</strong> ${booking.status}</p>
                    </li>
                `).join('')}
            </ul>
        `;

    } catch (err) {
        console.error('Failed to fetch bookings:', err);
        container.innerHTML = `<p style="color:red">Không thể tải danh sách vé đã đặt: ${err.message}</p>`;
    }
  }
};

export default MyBookingsPage;
