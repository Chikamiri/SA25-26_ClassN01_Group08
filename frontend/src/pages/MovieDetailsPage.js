import { getMovieById, getShowtimes } from '../api/apiClient.js';

const MovieDetailsPage = {
  render: async () => {
    return `
      <div class="container py-4">
        <nav aria-label="breadcrumb" class="mb-4">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="/movies">Phim</a></li>
            <li class="breadcrumb-item active" aria-current="page">Chi tiết</li>
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
        container.innerHTML = '<div class="alert alert-warning">Không tìm thấy ID phim.</div>';
        return;
    }

    try {
        const [movie, showtimes] = await Promise.all([
            getMovieById(id),
            getShowtimes(id)
        ]);

        if (!movie) {
             container.innerHTML = '<div class="alert alert-danger">Phim không tìm thấy.</div>';
             return;
        }

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
            const days = ['CN', 'Th 2', 'Th 3', 'Th 4', 'Th 5', 'Th 6', 'Th 7'];
            return {
                day: days[date.getDay()],
                date: `${date.getDate()}/${date.getMonth() + 1}`
            };
        };

        // Render function for Schedule
        const renderSchedule = () => {
             if (dates.length === 0) {
                 return '<div class="p-4 bg-light rounded text-center text-muted">Hiện không có suất chiếu nào.</div>';
             }

             // Tabs HTML
             const tabsHtml = dates.map((dateStr, index) => {
                 const label = getDayLabel(dateStr);
                 const isActive = index === 0 ? 'active' : '';
                 return `
                    <div class="date-tab ${isActive}" data-date="${dateStr}">
                        <span class="day-name">${label.day}</span>
                        <span class="date-val">${label.date}</span>
                    </div>
                 `;
             }).join('');

             // Grids HTML (All hidden except first)
             const gridsHtml = dates.map((dateStr, index) => {
                 const isHidden = index === 0 ? '' : 'display: none;';
                 const shows = groupedShowtimes[dateStr].sort((a,b) => a.time.localeCompare(b.time));
                 
                 return `
                    <div class="schedule-grid row g-3" id="grid-${dateStr}" style="${isHidden}">
                        ${shows.map(st => `
                            <div class="col-6 col-sm-4 col-md-3">
                                <a href="/book/${st.id}" class="time-card">
                                    <span class="time">${st.time}</span>
                                    <small class="text-muted d-block">${st.price.toLocaleString()}đ</small>
                                </a>
                            </div>
                        `).join('')}
                    </div>
                 `;
             }).join('');

             return `
                <div class="mb-4">
                    <div class="date-ribbon mb-4" id="date-ribbon">
                        ${tabsHtml}
                    </div>
                    ${gridsHtml}
                </div>
             `;
        };

        container.innerHTML = `
            <div class="row g-5">
              <div class="col-md-4">
                <div class="card border-0 shadow-sm sticky-top" style="top: 2rem; z-index: 1;">
                  <div class="card-body bg-dark text-white rounded p-5 text-center d-flex align-items-center justify-content-center" style="min-height: 400px;">
                    <div>
                        <h1 class="display-1">🎬</h1>
                        <p class="mb-0 text-muted">Poster</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-md-8">
                <h1 class="fw-bold mb-2">${movie.title}</h1>
                <div class="mb-4">
                  <span class="badge bg-primary me-2">${movie.genre}</span>
                  <span class="badge bg-secondary me-2">${movie.duration} phút</span>
                  <span class="text-muted small">Khởi chiếu: ${new Date(movie.release_date).toLocaleDateString()}</span>
                </div>
                
                <p class="lead text-muted mb-5">${movie.description || 'Chưa có mô tả cho bộ phim này.'}</p>
                
                <h4 class="fw-bold mb-4">Lịch Chiếu</h4>
                ${renderSchedule()}
              </div>
            </div>
        `;

        // Event Listeners for Tabs
        const tabs = document.querySelectorAll('.date-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Remove active class from all
                tabs.forEach(t => t.classList.remove('active'));
                // Add active to clicked
                tab.classList.add('active');
                
                // Hide all grids
                document.querySelectorAll('.schedule-grid').forEach(g => g.style.display = 'none');
                
                // Show selected grid
                const targetId = `grid-${tab.dataset.date}`;
                document.getElementById(targetId).style.display = 'flex';
            });
        });

    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">Lỗi: ${err.message}</div>`;
    }
  }
};

export default MovieDetailsPage;
