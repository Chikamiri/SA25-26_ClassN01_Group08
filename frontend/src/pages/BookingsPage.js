import { bookTicket, getShowtimeSeats, processPayment } from '../api/apiClient.js';

const BookingsPage = {
  render: async () => {
    const user = JSON.parse(localStorage.getItem('user'));
    const pathParts = window.location.pathname.split('/');
    const showtimeId = pathParts[2];

    if (!user) {
        return `
          <div class="container py-5 text-center">
            <div class="alert alert-warning d-inline-block">
              Bạn cần <a href="/login" class="alert-link">đăng nhập</a> để đặt vé.
            </div>
          </div>
        `;
    }

    return `
      <div class="container py-4">
        <h2 class="fw-bold mb-4 text-center">Đặt Vé & Chọn Chỗ</h2>
        
        <div id="booking-container" class="card shadow-sm border-0">
            <div class="card-body p-4">
                <div class="bg-secondary text-white text-center py-2 mb-5 rounded shadow-sm mx-auto" style="max-width: 80%; letter-spacing: 5px;">
                  <small>MÀN HÌNH</small>
                </div>
                
                <div id="seat-map" class="d-flex flex-wrap justify-content-center gap-2 mb-5" style="max-width: 600px; margin: 0 auto;">
                    <div class="spinner-border text-primary" role="status"></div>
                </div>

                <div class="border-top pt-4">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <p class="mb-0 text-muted small text-uppercase">Ghế đã chọn</p>
                        <h4 id="selected-seat-display" class="fw-bold text-primary mb-0">Chưa chọn</h4>
                      </div>
                      <button id="confirm-booking-btn" class="btn btn-primary btn-lg px-5 fw-bold" disabled>
                          Tiếp tục đặt vé
                      </button>
                    </div>
                </div>
                <div id="booking-error" class="text-danger mt-3 text-center small"></div>
            </div>
        </div>
        
        <div id="payment-step" style="display: none;">
           <div class="card shadow border-primary border-2">
             <div class="card-body p-5 text-center">
               <h3 class="fw-bold mb-3 text-primary">Thanh Toán</h3>
               <div id="payment-info" class="lead mb-4"></div>
               <button id="pay-now-btn" class="btn btn-success btn-lg px-5 fw-bold shadow">
                  Xác nhận Thanh toán
               </button>
             </div>
           </div>
        </div>

        <div id="booking-success" style="display: none;" class="alert alert-success p-5 text-center shadow-sm">
        </div>

        <div class="mt-4 text-center">
            <a href="/movies" class="text-decoration-none text-muted small">&larr; Quay lại danh sách phim</a>
        </div>
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
            seatMap.innerHTML = seats.map(seat => {
                const isAvailable = seat.status === 'available';
                return `
                    <div class="seat-item ${isAvailable ? 'available' : 'booked'}" 
                         data-seat="${seat.seat_number}" 
                         style="width: 45px; height: 45px; line-height: 45px; border-radius: 6px; text-align: center; cursor: ${isAvailable ? 'pointer' : 'not-allowed'}; background: ${isAvailable ? '#f8f9fa' : '#e9ecef'}; border: 2px solid ${isAvailable ? '#dee2e6' : '#dee2e6'}; color: ${isAvailable ? '#212529' : '#adb5bd'}; font-weight: bold; font-size: 0.8rem; transition: all 0.2s;">
                        ${seat.seat_number}
                    </div>
                `;
            }).join('');

            document.querySelectorAll('.seat-item.available').forEach(el => {
                el.addEventListener('click', () => {
                    document.querySelectorAll('.seat-item.available').forEach(s => {
                      s.style.background = '#f8f9fa';
                      s.style.borderColor = '#dee2e6';
                      s.style.color = '#212529';
                      s.style.transform = 'scale(1)';
                    });
                    el.style.background = '#0d6efd';
                    el.style.borderColor = '#0d6efd';
                    el.style.color = 'white';
                    el.style.transform = 'scale(1.1)';
                    
                    selectedSeat = el.dataset.seat;
                    selectedDisplay.innerText = selectedSeat;
                    confirmBtn.disabled = false;
                });
            });
        } catch (err) {
            seatMap.innerHTML = `<div class="alert alert-danger">Lỗi tải sơ đồ ghế: ${err.message}</div>`;
        }
    };

    confirmBtn.addEventListener('click', async () => {
        if (!selectedSeat) return;

        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Đang xử lý...';
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
                Ghế: <span class="badge bg-primary">${selectedSeat}</span><br>
                Số tiền: <span class="fw-bold text-success">${response.price.toLocaleString()} VND</span>
            `;

        } catch (err) {
            errorMsg.innerText = err.message || 'Đã xảy ra lỗi khi đặt vé.';
            confirmBtn.disabled = false;
            confirmBtn.innerText = 'Tiếp tục đặt vé';
        }
    });

    payNowBtn.addEventListener('click', async () => {
        payNowBtn.disabled = true;
        payNowBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Đang thanh toán...';
        
        try {
            await processPayment({ booking_id: currentBookingId });
            
            paymentStep.style.display = 'none';
            successDiv.style.display = 'block';
            successDiv.innerHTML = `
                <div class="display-1 mb-4">✅</div>
                <h3 class="fw-bold">Thanh toán thành công!</h3>
                <p class="lead mb-4">Vé của bạn đã được xác nhận. Mã đặt vé: <strong>#${currentBookingId}</strong></p>
                <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
                  <a href="/my-bookings" class="btn btn-primary btn-lg px-4">Xem Vé Của Tôi</a>
                  <a href="/movies" class="btn btn-outline-secondary btn-lg px-4">Quay lại trang phim</a>
                </div>
            `;
        } catch (err) {
            alert('Lỗi thanh toán: ' + err.message);
            payNowBtn.disabled = false;
            payNowBtn.innerText = 'Xác nhận Thanh toán';
        }
    });

    await fetchSeats();
  }
};

export default BookingsPage;
