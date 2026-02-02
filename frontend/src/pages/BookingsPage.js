import { bookTicket, getShowtimeSeats, processPayment } from '../api/apiClient.js';

const BookingsPage = {
  render: async () => {
    const user = JSON.parse(localStorage.getItem('user'));
    const pathParts = window.location.pathname.split('/');
    const showtimeId = pathParts[2];

    if (!user) {
        return `<p>Bạn cần <a href="/login">đăng nhập</a> để đặt vé.</p>`;
    }

    return `
      <div>
        <h2>Đặt Vé & Chọn Chỗ</h2>
        <p>Suất chiếu ID: ${showtimeId}</p>
        
        <div id="booking-container">
            <div style="margin: 20px 0; padding: 10px; background: #eee; text-align: center; font-weight: bold;">
                MÀN HÌNH
            </div>
            
            <div id="seat-map" style="display: grid; grid-template-columns: repeat(10, 1fr); gap: 10px; max-width: 500px; margin: 0 auto;">
                Loading seats...
            </div>

            <div style="margin-top: 30px; border-top: 1px solid #ccc; padding-top: 20px;">
                <p>Ghế đã chọn: <span id="selected-seat-display" style="font-weight: bold; color: #007bff;">Chưa chọn</span></p>
                <button id="confirm-booking-btn" disabled style="padding: 10px 15px; cursor: not-allowed;">
                    Xác nhận Đặt vé
                </button>
            </div>
            <p id="booking-error" style="color: red; margin-top: 15px;"></p>
        </div>
        
        <div id="payment-step" style="display: none; margin-top: 20px; padding: 20px; border: 2px solid #007bff; border-radius: 8px;">
           <h3>Thanh Toán</h3>
           <p id="payment-info"></p>
           <button id="pay-now-btn" style="padding: 12px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">
              Thanh toán ngay (Giả lập)
           </button>
        </div>

        <div id="booking-success" style="display: none; margin-top: 20px; padding: 15px; border: 1px solid #28a745; border-radius: 5px; background-color: #d4edda; color: #155724;">
        </div>

        <p style="margin-top: 20px;">
            <a href="/movies" style="text-decoration: none; color: #6c757d; margin-right: 10px;">&larr; Quay lại danh sách phim</a>
        </p>
      </div>
    `;
  },
  afterRender: async () => {
    const user = JSON.parse(localStorage.getItem('user'));
    if (!user) return;

    const pathParts = window.location.pathname.split('/');
    const showtimeId = pathParts[2];
    
    const seatMap = document.getElementById('seat-map');
    const selectedDisplay = document.getElementById('selected-seat-display');
    const confirmBtn = document.getElementById('confirm-booking-btn');
    const errorMsg = document.getElementById('booking-error');
    const bookingContainer = document.getElementById('booking-container');
    const paymentStep = document.getElementById('payment-step');
    const paymentInfo = document.getElementById('payment-info');
    const payNowBtn = document.getElementById('pay-now-btn');
    const successDiv = document.getElementById('booking-success');

    let selectedSeat = null;
    let currentBookingId = null;

    const fetchSeats = async () => {
        try {
            const seats = await getShowtimeSeats(showtimeId);
            seatMap.innerHTML = seats.map(seat => `
                <div class="seat ${seat.status}" 
                     data-seat="${seat.seat_number}" 
                     style="padding: 10px; border: 1px solid #ccc; text-align: center; cursor: ${seat.status === 'available' ? 'pointer' : 'not-allowed'}; background: ${seat.status === 'available' ? 'white' : '#ddd'}; color: ${seat.status === 'available' ? 'black' : '#888'};">
                    ${seat.seat_number}
                </div>
            `).join('');

            document.querySelectorAll('.seat.available').forEach(el => {
                el.addEventListener('click', () => {
                    document.querySelectorAll('.seat').forEach(s => s.style.borderColor = '#ccc');
                    el.style.borderColor = '#007bff';
                    el.style.boxShadow = '0 0 5px rgba(0,123,255,0.5)';
                    selectedSeat = el.dataset.seat;
                    selectedDisplay.innerText = selectedSeat;
                    confirmBtn.disabled = false;
                    confirmBtn.style.cursor = 'pointer';
                    confirmBtn.style.background = '#007bff';
                    confirmBtn.style.color = 'white';
                });
            });
        } catch (err) {
            seatMap.innerHTML = `<p style="color:red">Lỗi tải sơ đồ ghế: ${err.message}</p>`;
        }
    };

    confirmBtn.addEventListener('click', async () => {
        if (!selectedSeat) return;

        confirmBtn.disabled = true;
        confirmBtn.innerText = 'Đang đặt chỗ...';
        errorMsg.innerText = '';

        try {
            const response = await bookTicket({
                showtime_id: parseInt(showtimeId),
                seat_number: selectedSeat
            });

            currentBookingId = response.booking_id;
            bookingContainer.style.display = 'none';
            paymentStep.style.display = 'block';
            paymentInfo.innerHTML = `
                Bạn đang đặt ghế <strong>${selectedSeat}</strong> cho suất chiếu #${showtimeId}.<br>
                Số tiền cần thanh toán: <strong>${response.price.toLocaleString()} VND</strong>
            `;

        } catch (err) {
            errorMsg.innerText = err.message || 'Đã xảy ra lỗi khi đặt vé.';
            confirmBtn.disabled = false;
            confirmBtn.innerText = 'Xác nhận Đặt vé';
        }
    });

    payNowBtn.addEventListener('click', async () => {
        payNowBtn.disabled = true;
        payNowBtn.innerText = 'Đang thanh toán...';
        
        try {
            await processPayment({ booking_id: currentBookingId });
            
            paymentStep.style.display = 'none';
            successDiv.style.display = 'block';
            successDiv.innerHTML = `
                <h3>Thanh toán thành công!</h3>
                <p>Vé của bạn đã được xác nhận. Mã đặt vé: #${currentBookingId}</p>
                <button id="view-my-bookings" style="margin-top: 10px; padding: 8px 12px;">
                    Xem các vé đã đặt
                </button>
            `;
            document.getElementById('view-my-bookings').addEventListener('click', () => {
                window.location.href = '/my-bookings';
            });
        } catch (err) {
            alert('Lỗi thanh toán: ' + err.message);
            payNowBtn.disabled = false;
            payNowBtn.innerText = 'Thanh toán ngay (Giả lập)';
        }
    });

    await fetchSeats();
  }
};

export default BookingsPage;
