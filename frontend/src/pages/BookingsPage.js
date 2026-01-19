import { bookTicket } from '../api/apiClient.js';

const BookingsPage = {
  render: () => {
    const user = JSON.parse(localStorage.getItem('user'));
    // Lấy showtimeId từ URL
    const pathParts = window.location.pathname.split('/');
    const showtimeId = pathParts[2];

    if (!user) {
        return `<p>Bạn cần <a href="/login">đăng nhập</a> để đặt vé.</p>`;
    }

    return `
      <div>
        <h2>Đặt Vé</h2>
        <p>Suất chiếu ID: ${showtimeId}</p>
        <p>Người dùng: ${user.email} (${user.role})</p>

        <div id="booking-form-container">
          <div style="margin-top: 20px;">
            <label>Nhập số ghế bạn muốn đặt:</label><br />
            <input
              type="text"
              id="seat-number"
              placeholder="Ví dụ: A1, B5, 23"
              style="padding: 8px; margin-right: 10px;"
            />
            <button id="confirm-booking-btn" style="padding: 10px 15px;">
              Xác nhận Đặt vé
            </button>
          </div>
          <p id="booking-error" style="color: red; margin-top: 15px;"></p>
        </div>
        
        <div id="booking-success" style="display: none; margin-top: 20px; padding: 15px; border: 1px solid #28a745; border-radius: 5px; background-color: #d4edda; color: #155724;">
           <!-- Kết quả đặt vé sẽ hiện ở đây -->
        </div>

        <p style="margin-top: 20px;">
            <a href="/movies" style="text-decoration: none; color: #6c757d; margin-right: 10px;">&larr; Quay lại danh sách phim</a>
        </p>
      </div>
    `;
  },
  afterRender: () => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) return;

    const pathParts = window.location.pathname.split('/');
    const showtimeId = pathParts[2];
    
    const confirmBtn = document.getElementById('confirm-booking-btn');
    const seatInput = document.getElementById('seat-number');
    const errorMsg = document.getElementById('booking-error');
    const successDiv = document.getElementById('booking-success');
    const formContainer = document.getElementById('booking-form-container');

    confirmBtn.addEventListener('click', async () => {
        const seatNumber = seatInput.value.trim();
        if (!seatNumber) {
            alert('Vui lòng nhập số ghế.');
            return;
        }

        confirmBtn.disabled = true;
        confirmBtn.innerText = 'Đang xử lý...';
        errorMsg.innerText = '';

        try {
            const bookingData = {
                showtime_id: parseInt(showtimeId),
                seat_number: seatNumber
            };

            const response = await bookTicket(bookingData);

            // Ẩn form, hiện success
            formContainer.style.display = 'none';
            successDiv.style.display = 'block';
            successDiv.innerHTML = `
                <h3>Đặt vé thành công!</h3>
                <p><strong>Mã đặt vé:</strong> #${response.booking_id}</p>
                <p><strong>Phim:</strong> ${response.movie}</p>
                <p><strong>Chỗ ngồi:</strong> ${seatNumber}</p>
                <p><strong>Giá vé:</strong> ${response.price ? response.price.toLocaleString() : 'N/A'} VND</p>
                <button id="view-my-bookings" style="margin-top: 10px; padding: 8px 12px;">
                    Xem các vé đã đặt
                </button>
            `;

            document.getElementById('view-my-bookings').addEventListener('click', () => {
                window.location.href = '/my-bookings';
            });

        } catch (err) {
            console.error('Booking failed:', err);
            errorMsg.innerText = err.message || 'Đã xảy ra lỗi khi đặt vé.';
            confirmBtn.disabled = false;
            confirmBtn.innerText = 'Xác nhận Đặt vé';
        }
    });
  }
};

export default BookingsPage;
