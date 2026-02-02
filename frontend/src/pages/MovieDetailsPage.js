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

        const showtimesHTML = showtimes.length > 0 
            ? `<div class="list-group">
                ${showtimes.map(st => `
                    <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center p-3 border-0 shadow-sm mb-2 rounded">
                        <div>
                            <div class="fw-bold text-primary">${st.start_time} - ${st.end_time}</div>
                            <small class="text-muted">Giá vé: ${st.price ? st.price.toLocaleString() : 'N/A'} VND</small>
                        </div>
                        <a href="/book/${st.id}" class="btn btn-success btn-sm px-4">
                            Đặt vé
                        </a>
                    </div>
                `).join('')}
               </div>`
            : '<div class="p-3 bg-light rounded text-muted">Hiện không có suất chiếu nào cho phim này.</div>';

        container.innerHTML = `
            <div class="row g-4">
              <div class="col-md-4">
                <div class="card border-0 shadow-sm">
                  <div class="card-body bg-dark text-white rounded p-5 text-center">
                    <h1 class="display-1">🎬</h1>
                    <p class="mb-0">Poster Phim</p>
                  </div>
                </div>
              </div>
              <div class="col-md-8">
                <h1 class="fw-bold mb-2">${movie.title}</h1>
                <div class="mb-3">
                  <span class="badge bg-primary me-2">${movie.genre}</span>
                  <span class="badge bg-secondary">${movie.duration} phút</span>
                </div>
                <p class="text-muted mb-4">${movie.description || 'Không có mô tả chi tiết cho bộ phim này.'}</p>
                
                <h4 class="fw-bold mb-3">Lịch Chiếu</h4>
                ${showtimesHTML}
              </div>
            </div>
        `;

    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">Lỗi: ${err.message}</div>`;
    }
  }
};

export default MovieDetailsPage;
