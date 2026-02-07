import { getMovies } from '../api/apiClient.js';

const MoviesPage = {
  render: async () => {
    return `
      <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="fw-bold">Movie List</h2>
          <div class="col-md-4">
            <input
              type="text"
              id="search-input"
              class="form-control"
              placeholder="🔍 Search movies..."
            />
          </div>
        </div>
        <div id="movies-list" class="row g-4">
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
    const moviesList = document.getElementById('movies-list');
    const searchInput = document.getElementById('search-input');

    const fetchAndRenderMovies = async (query = '') => {
      try {
        const movies = await getMovies(query);
        
        if (movies.length === 0) {
            moviesList.innerHTML = '<div class="col-12 text-center text-muted"><p>No matching movies found.</p></div>';
            return;
        }

        moviesList.innerHTML = movies.map(movie => `
          <div class="col-md-4 col-sm-6">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body">
                <h5 class="card-title fw-bold">${movie.title}</h5>
                <h6 class="card-subtitle mb-2 text-muted small">${movie.genre}</h6>
                <p class="card-text small text-secondary">
                  <strong>Duration:</strong> ${movie.duration} minutes<br>
                  <strong>Release Date:</strong> ${new Date(movie.release_date).toLocaleDateString()}
                </p>
                <div class="d-grid mt-3">
                  <a href="/movies/${movie.id}" class="btn btn-outline-primary btn-sm">View Details</a>
                </div>
              </div>
            </div>
          </div>
        `).join('');

      } catch (err) {
        moviesList.innerHTML = `<div class="col-12"><div class="alert alert-danger">Error: ${err.message}</div></div>`;
      }
    };

    // Initial fetch
    await fetchAndRenderMovies();

    // Debounce helper
    const debounce = (func, delay) => {
      let timeout;
      return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
      };
    };

    const debouncedSearch = debounce((query) => {
      fetchAndRenderMovies(query);
    }, 500);

    // Search event
    searchInput.addEventListener('input', (e) => {
      debouncedSearch(e.target.value);
    });
  }
};

export default MoviesPage;
