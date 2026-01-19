
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
            Loading...
        </div>
      </div>
    `;
  },
  afterRender: async () => {
    const container = document.getElementById('bookings-list-container');
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user) return;

    try {
        // Giả lập delay và dữ liệu như bản cũ
        await new Promise(resolve => setTimeout(resolve, 500));
        const dummyBookings = [
          { booking_id: 1001, movie: 'Inception', showtime: '2026-01-17 19:00', seat: 'A5', price: 100000, status: 'PAID' },
          { booking_id: 1002, movie: 'The Dark Knight', showtime: '2026-01-17 20:00', seat: 'B10', price: 120000, status: 'PAID' },
        ];
        
        if (dummyBookings.length === 0) {
            container.innerHTML = '<p>Bạn chưa có vé nào được đặt.</p>';
            return;
        }

        container.innerHTML = `
            <ul style="list-style: none; padding: 0;">
                ${dummyBookings.map(booking => `
                    <li style="margin-bottom: 15px; padding: 15px; border: 1px solid #ccc; border-radius: 5px;">
                        <p><strong>Mã đặt vé:</strong> #${booking.booking_id}</p>
                        <p><strong>Phim:</strong> ${booking.movie}</p>
                        <p><strong>Suất chiếu:</strong> ${booking.showtime}</p>
                        <p><strong>Chỗ ngồi:</strong> ${booking.seat}</p>
                        <p><strong>Giá vé:</strong> ${booking.price.toLocaleString()} VND</p>
                        <p><strong>Trạng thái:</strong> ${booking.status}</p>
                    </li>
                `).join('')}
            </ul>
        `;

    } catch (err) {
        container.innerHTML = '<p style="color:red">Không thể tải danh sách vé đã đặt.</p>';
    }
  }
};

export default MyBookingsPage;
