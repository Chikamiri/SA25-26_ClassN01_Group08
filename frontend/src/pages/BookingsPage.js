import { bookTicket, getShowtimeSeats, processPayment, getShowtimeDetail, getShowtimes, getRoomById } from '../api/apiClient.js';

const BookingsPage = {
  render: async () => {
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user) {
        return `
          <div class="container py-5 text-center">
            <div class="alert alert-warning d-inline-block">
              You need to <a href="/login" class="alert-link">login</a> to book tickets.
            </div>
          </div>
        `;
    }

    return `
      <div class="container py-4">
        <div class="row g-4">
            
            <!-- Sidebar -->
            <div class="col-lg-3 order-lg-2">
                
                <!-- Booking Summary Card -->
                <div class="card shadow-sm border-0 mb-3 sticky-top" style="top: 2rem; z-index: 20;">
                    <div class="card-header bg-primary text-white border-bottom-0 py-3">
                        <h5 class="fw-bold text-uppercase mb-0 text-center"><i class="bi bi-ticket-perforated"></i> Book Ticket</h5>
                        <div id="room-name-display" class="text-center small text-white-50 mt-1"></div>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <small class="text-muted d-block">Selected seats:</small>
                            <div id="selected-seat-display" class="fw-bold text-break text-primary">None selected</div>
                        </div>
                        <div class="mb-4">
                            <small class="text-muted d-block">Subtotal:</small>
                            <h4 id="total-price-display" class="fw-bold text-success mb-0">0 VND</h4>
                        </div>
                        <div class="d-grid">
                            <button id="confirm-booking-btn" class="btn btn-primary fw-bold py-2" disabled>
                                Book Now
                            </button>
                        </div>
                        <div id="booking-error" class="text-danger mt-2 text-center small"></div>
                    </div>
                </div>

                <!-- Schedule Picker -->
                <div class="card shadow-sm border-0">
                    <div class="card-header bg-white border-bottom-0 pt-3">
                        <h6 class="fw-bold text-uppercase mb-0 text-center text-muted">Other Showtimes</h6>
                    </div>
                    <div class="card-body p-2" id="schedule-picker-container">
                         <div class="text-center py-3"><div class="spinner-border spinner-border-sm text-secondary" role="status"></div></div>
                    </div>
                </div>
            </div>

            <!-- Main Content: Seat Selection -->
            <div class="col-lg-9 order-lg-1">
                <div id="booking-container" class="card shadow-sm border-0 bg-white">
                    <div class="card-body p-4">
                        <div class="text-center mb-4">
                            <h2 class="fw-bold">Seat Map</h2>
                            <p class="text-muted small">Screen at the front - Please select seats</p>
                        </div>

                        <!-- Cinema Screen -->
                        <div class="cinema-screen shadow-sm">SCREEN</div>
                        
                        <!-- Seat Map (Scrollable for IMAX) -->
                        <div class="table-responsive mb-5" style="overflow-x: auto;">
                            <div id="seat-map" class="d-flex flex-column align-items-center" style="min-width: max-content; margin: 0 auto; padding-bottom: 20px;">
                                <div class="spinner-border text-primary" role="status"></div>
                            </div>
                        </div>

                        <!-- Legend -->
                        <div class="d-flex justify-content-center gap-4 mb-3 text-muted small flex-wrap">
                            <div class="d-flex align-items-center">
                                <span class="seat-legend-item" style="background-color: #fff;"></span> Available
                            </div>
                            <div class="d-flex align-items-center">
                                <span class="seat-legend-item" style="background-color: var(--primary-color); border-color: var(--primary-color);"></span> Selected
                            </div>
                            <div class="d-flex align-items-center">
                                <span class="seat-legend-item booked"></span> Booked
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4 text-center">
                    <a href="/movies" class="text-decoration-none text-muted small">&larr; Back to movie list</a>
                </div>
            </div>
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
    const totalPriceDisplay = document.getElementById('total-price-display');
    const confirmBtn = document.getElementById('confirm-booking-btn');
    const errorMsg = document.getElementById('booking-error');
    const bookingContainer = document.getElementById('booking-container');
    const schedulePickerContainer = document.getElementById('schedule-picker-container');
    const roomNameDisplay = document.getElementById('room-name-display');

    let selectedSeats = [];
    let currentBookingIds = [];
    let ticketPrice = 50000; // Default fallback
    let allSeatsData = []; // Store seat data for price calc

    // --- Schedule Picker & Price Fetch Logic ---
    const initPageData = async () => {
        try {
            const currentShowtime = await getShowtimeDetail(showtimeId);
            
            if (currentShowtime) {
                ticketPrice = currentShowtime.price || 50000;
                
                // Fetch Room Name
                if (currentShowtime.room_id) {
                    try {
                        const room = await getRoomById(currentShowtime.room_id);
                        if (room && room.name) {
                            roomNameDisplay.innerText = room.name;
                        }
                    } catch (err) {
                        console.log("Could not fetch room details");
                    }
                }

                // Load Schedule Picker if movie_id exists
                if (currentShowtime.movie_id) {
                     loadSchedulePicker(currentShowtime.movie_id, currentShowtime.start_time);
                }
            } else {
                 schedulePickerContainer.innerHTML = '<p class="text-center text-muted small">Could not load information.</p>';
            }
        } catch (e) {
            console.error("Error loading page data:", e);
        }
    };

    const loadSchedulePicker = async (movieId, currentStartTime) => {
        try {
            const allShowtimes = await getShowtimes(movieId);
            const groupedShowtimes = {};
            
            allShowtimes.forEach(st => {
                const [dateStr, timeStr] = st.start_time.split(' ');
                if (!groupedShowtimes[dateStr]) groupedShowtimes[dateStr] = [];
                groupedShowtimes[dateStr].push({ ...st, time: timeStr });
            });
            const dates = Object.keys(groupedShowtimes).sort();

            const getDayLabel = (dateStr) => {
                const date = new Date(dateStr);
                const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
                return `${days[date.getDay()]}, ${date.getDate()}/${date.getMonth() + 1}`;
            };

            const html = dates.map(dateStr => {
                const label = getDayLabel(dateStr);
                const shows = groupedShowtimes[dateStr].sort((a,b) => a.time.localeCompare(b.time));
                
                return `
                   <div class="mb-3">
                       <div class="d-flex align-items-center mb-2">
                            <span class="badge bg-light text-dark border me-2"><i class="bi bi-calendar"></i></span>
                            <span class="fw-bold small text-secondary">${label}</span>
                       </div>
                       <div class="d-flex flex-wrap gap-2">
                           ${shows.map(st => {
                               const isCurrent = st.id == showtimeId;
                               const btnClass = isCurrent 
                                ? 'btn-primary text-white' 
                                : 'btn-outline-secondary';
                               const href = isCurrent ? '#' : `/book/${st.id}`;
                               return `
                                   <a href="${href}" class="btn btn-sm ${btnClass} flex-grow-1" style="font-size: 0.85rem;">
                                       ${st.time}
                                   </a>
                               `;
                           }).join('')}
                       </div>
                   </div>
                   <hr class="text-muted opacity-25">
                `;
            }).join('');
            
            schedulePickerContainer.innerHTML = html || '<p class="text-center text-muted small">No other showtimes</p>';
        } catch (e) {
            console.error(e);
        }
    };

    initPageData();

    // --- Visual Update Logic ---

    const updateVisualSelection = () => {
        // Update Seat Styles
        document.querySelectorAll('.seat-item.available').forEach(el => {
            if (selectedSeats.includes(el.dataset.seat)) {
                el.classList.add('selected');
            } else {
                el.classList.remove('selected');
            }
        });
        
        // Update Sidebar Info
        if (selectedSeats.length > 0) {
            selectedDisplay.innerText = selectedSeats.join(', ');
            
            // Calculate Total
            let total = 0;
            selectedSeats.forEach(seatNum => {
                const seatObj = allSeatsData.find(s => s.seat_number === seatNum);
                const surcharge = seatObj ? (seatObj.price_surcharge || 0) : 0;
                total += (ticketPrice + surcharge);
            });
            
            totalPriceDisplay.innerText = total.toLocaleString() + ' VND';
            confirmBtn.disabled = false;
        } else {
            selectedDisplay.innerText = 'None selected';
            totalPriceDisplay.innerText = '0 VND';
            confirmBtn.disabled = true;
        }
    };

    const fetchSeats = async () => {
        try {
            const seats = await getShowtimeSeats(showtimeId);
            allSeatsData = seats; // Store for price calc
            
            // Group seats by row letter
            const rows = {};
            seats.forEach(seat => {
              const rowLetter = seat.seat_number.match(/[A-Z]+/)[0];
              if (!rows[rowLetter]) rows[rowLetter] = [];
              rows[rowLetter].push(seat);
            });

            seatMap.innerHTML = Object.keys(rows).sort().map(rowLetter => `
                <div class="seat-row">
                  <div class="seat-row-label">${rowLetter}</div>
                  ${rows[rowLetter].sort((a, b) => {
                    // Sort I1-2 before I3-4 etc.
                    const numA = parseInt(a.seat_number.match(/\d+/)[0]);
                    const numB = parseInt(b.seat_number.match(/\d+/)[0]);
                    return numA - numB;
                  }).map(seat => {
                      const isAvailable = seat.status === 'available';
                      const match = seat.seat_number.match(/\d+(-?\d+)?/);
                      const displayNum = match ? match[0] : '';
                      const startNum = parseInt(displayNum.split('-')[0]);
                      
                      // Determine Layout Classes
                      let typeClass = '';
                      if (seat.seat_type === 'VIP') typeClass = 'vip';
                      if (seat.seat_type === 'COUPLE') typeClass = 'couple';
                      
                      let aisleClass = '';
                      // Apply aisle to seats 3 and 8 in standard rows
                      if (rowLetter !== 'I' && (startNum === 3 || startNum === 8)) {
                          aisleClass = 'seat-aisle-right';
                      }

                      return `
                          <div class="seat-item ${isAvailable ? 'available' : 'booked'} ${typeClass} ${aisleClass}" 
                               data-seat="${seat.seat_number}" 
                               title="${seat.seat_number} (${seat.seat_type})">
                              ${displayNum}
                          </div>
                      `;
                  }).join('')}
                  <div class="seat-row-label">${rowLetter}</div>
                </div>
            `).join('');

            // Add Legend Items for new types
            const legendContainer = document.querySelector('.d-flex.justify-content-center.gap-4.mb-3');
            if (legendContainer && !legendContainer.querySelector('.vip')) {
                 legendContainer.innerHTML += `
                    <div class="d-flex align-items-center">
                        <span class="seat-legend-item vip"></span> VIP (+20k)
                    </div>
                    <div class="d-flex align-items-center">
                        <span class="seat-legend-item couple"></span> Couple (+50k)
                    </div>
                 `;
            }

            document.querySelectorAll('.seat-item.available').forEach(el => {
                el.addEventListener('click', () => {
                    const seat = el.dataset.seat;
                    if (selectedSeats.includes(seat)) {
                        selectedSeats = selectedSeats.filter(s => s !== seat);
                    } else {
                        selectedSeats.push(seat);
                    }
                    updateVisualSelection();
                });
            });
        } catch (err) {
            seatMap.innerHTML = `<div class="alert alert-danger">Error loading seat map: ${err.message}</div>`;
        }
    };

    confirmBtn.addEventListener('click', async () => {
        if (selectedSeats.length === 0) return;

        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing...';
        errorMsg.innerText = '';

        try {
            const response = await bookTicket({
                showtime_id: parseInt(showtimeId),
                seat_numbers: selectedSeats
            });

            // The backend now returns { booking_ids: [...], total_price: ... }
            // Or { booking_id: ... } if fallback. 
            // We implemented booking_ids.
            
            if (response.booking_ids) {
                currentBookingIds = response.booking_ids;
            } else if (response.booking_id) {
                currentBookingIds = [response.booking_id];
            }

            const totalPrice = response.total_price || response.price;

            // Redirect to Payment Page
            window.location.href = `/payment?booking_ids=${currentBookingIds.join(',')}&amount=${totalPrice}`;

        } catch (err) {
            errorMsg.innerText = err.message || 'An error occurred while booking.';
            confirmBtn.disabled = false;
            confirmBtn.innerText = 'Continue booking';
        }
    });

    await fetchSeats();
  }
};

export default BookingsPage;
