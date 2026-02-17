import { getMovieById, getShowtimes, getRooms } from '../api/apiClient.js';

const MovieDetailsPage = {
  render: async () => {
    return `
      <div class="container py-4">
        <nav aria-label="breadcrumb" class="mb-4">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="/movies">Movies</a></li>
            <li class="breadcrumb-item active" aria-current="page">Details</li>
          </ol>
        </nav>
        <div id="movie-detail-container">
          <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </div>
    `;
  },
  afterRender: async () => {
    const container = document.getElementById('movie-detail-container');
    const pathParts = window.location.pathname.split('/');
    const id = pathParts[2];

    if (!id) {
        container.innerHTML = '<div class="alert alert-warning">Movie ID not found.</div>';
        return;
    }

    try {
        const [movie, showtimes, allRooms] = await Promise.all([
            getMovieById(id),
            getShowtimes(id),
            getRooms()
        ]);

        if (!movie) {
             container.innerHTML = '<div class="alert alert-danger">Movie not found.</div>';
             return;
        }

        const roomMap = {};
        allRooms.forEach(r => roomMap[r.id] = r.name);

        // --- Logic: Group Showtimes by Date ---
        const groupedShowtimes = {};
        showtimes.forEach(st => {
            // st.start_time is "YYYY-MM-DD HH:MM"
            const [dateStr, timeStr] = st.start_time.split(' ');
            if (!groupedShowtimes[dateStr]) {
                groupedShowtimes[dateStr] = [];
            }
            groupedShowtimes[dateStr].push({ ...st, time: timeStr });
        });

        // Sort dates
        const dates = Object.keys(groupedShowtimes).sort();
        
        // Helper to format date label
        const getDayLabel = (dateStr) => {
            const date = new Date(dateStr);
            const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            return {
                day: days[date.getDay()],
                date: `${date.getDate()}/${date.getMonth() + 1}`
            };
        };

        // Render Structure
        container.innerHTML = `
            <div class="row g-5">
              <div class="col-md-3">
                <div class="card border-0 shadow-sm sticky-top" style="top: 2rem; z-index: 1;">
                  <div class="card-body bg-dark text-white rounded p-5 text-center d-flex align-items-center justify-content-center" style="min-height: 400px;">
                    <div>
                        <h1 class="display-1">🎬</h1>
                        <p class="mb-0 text-muted">Poster</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-md-9">
                <h1 class="fw-bold mb-2">${movie.title}</h1>
                <div class="mb-4">
                  <span class="badge bg-primary me-2">${movie.genre}</span>
                  <span class="badge bg-secondary me-2">${movie.duration} minutes</span>
                  <span class="text-muted small">Release Date: ${new Date(movie.release_date).toLocaleDateString()}</span>
                </div>
                
                <p class="lead text-muted mb-5">${movie.description || 'No description available for this movie.'}</p>
                
                <h4 class="fw-bold mb-4">Showtimes</h4>
                
                <div id="schedule-container">
                    <!-- Date Scroller -->
                    <div class="mb-2">
                        <label class="form-label small text-muted mb-0">Select Date</label>
                    </div>
                    <div class="d-flex align-items-stretch gap-2 mb-4">
                        <button id="prev-dates-btn" class="btn btn-outline-secondary btn-sm px-2" title="Previous dates">
                            <i class="bi bi-chevron-left"></i>
                        </button>
                        
                        <div class="date-scroller flex-grow-1" id="date-scroller">
                            <!-- Date items will be injected here -->
                        </div>

                        <button id="next-dates-btn" class="btn btn-outline-secondary btn-sm px-2" title="Next dates">
                            <i class="bi bi-chevron-right"></i>
                        </button>
                    </div>

                    <!-- Times Grid -->
                    <div id="showtimes-grid"></div>
                </div>
              </div>
            </div>
        `;

        // --- Logic for Date Scroller & Grid ---
        const scroller = document.getElementById('date-scroller');
        const prevBtn = document.getElementById('prev-dates-btn');
        const nextBtn = document.getElementById('next-dates-btn');
        const timesGrid = document.getElementById('showtimes-grid');

        if (dates.length === 0) {
            timesGrid.innerHTML = '<div class="alert alert-info">No showtimes available.</div>';
            return;
        }

        let currentPage = 0;
        const datesPerPage = 8;
        const totalPages = Math.ceil(dates.length / datesPerPage);

        const renderTimes = (dateStr) => {
            const shows = groupedShowtimes[dateStr];
            if (!shows) {
                timesGrid.innerHTML = '<div class="alert alert-warning">No shows found for this date.</div>';
                return;
            }
            shows.sort((a,b) => a.time.localeCompare(b.time));

            timesGrid.innerHTML = `
                <div class="row g-3">
                    ${shows.map(st => {
                        const roomName = roomMap[st.room_id] || 'Room';
                        return `
                        <div class="col-6 col-sm-4 col-md-3 col-lg-2">
                            <a href="/book/${st.id}" class="btn btn-outline-primary w-100 h-100 d-flex flex-column justify-content-center align-items-center p-2">
                                <span class="fw-bold mb-1">${st.time}</span>
                                <div class="small text-muted" style="font-size: 0.7rem;">
                                    <div class="border-bottom pb-1 mb-1">${roomName}</div>
                                    <div>${st.price.toLocaleString()} VND</div>
                                </div>
                            </a>
                        </div>
                        `;
                    }).join('')}
                </div>
            `;
        };

        const renderDatePage = (activeDate) => {
            const start = currentPage * datesPerPage;
            const end = start + datesPerPage;
            const pageDates = dates.slice(start, end);

            // Update Buttons
            prevBtn.disabled = currentPage === 0;
            nextBtn.disabled = currentPage >= totalPages - 1;

            scroller.innerHTML = pageDates.map(dStr => {
                const { day, date } = getDayLabel(dStr);
                const isActive = dStr === activeDate ? 'active' : '';
                return `
                    <div class="date-scroller-item ${isActive}" data-date="${dStr}">
                        <span class="date-scroller-day">${day}</span>
                        <span class="date-scroller-date">${date}</span>
                    </div>
                `;
            }).join('');

            // Add Events
            scroller.querySelectorAll('.date-scroller-item').forEach(el => {
                el.addEventListener('click', () => {
                    const newDate = el.dataset.date;
                    renderDatePage(newDate); // Re-render to update active class
                    renderTimes(newDate);
                });
            });
        };

        // Navigation Events
        prevBtn.addEventListener('click', () => {
            if (currentPage > 0) {
                currentPage--;
                // Keep current selection active visualization if it's on the new page
                // But for simplicity, we just re-render the page. 
                // The currently selected date is not tracked globally in this scope 
                // except by looking at the 'active' class, but that's DOM based.
                // Let's assume we don't change the selection when paging unless clicked.
                // We need to pass the currently active date to keep it highlighted.
                const activeEl = scroller.querySelector('.active');
                const currentActiveDate = activeEl ? activeEl.dataset.date : dates[0];
                renderDatePage(currentActiveDate);
            }
        });

        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages - 1) {
                currentPage++;
                const activeEl = scroller.querySelector('.active');
                const currentActiveDate = activeEl ? activeEl.dataset.date : dates[0];
                renderDatePage(currentActiveDate);
            }
        });

        // Initial Render
        // Default to first date
        renderDatePage(dates[0]);
        renderTimes(dates[0]);

    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
    }
  }
};

export default MovieDetailsPage;
