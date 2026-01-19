import { getMovies } from '../api/apiClient.js';

const MoviesPage = {
  render: async () => {
    return `
      <div>
        <h2>Danh Sách Phim</h2>
        <div style="margin-bottom: 20px;">
          <input
            type="text"
            id="search-input"
            placeholder="Tìm kiếm phim theo tiêu đề..."
            style="margin-right: 10px; padding: 8px; width: 300px;"
          />
        </div>
        <ul id="movies-list" style="list-style: none; padding: 0;">
          Loading movies...
        </ul>
      </div>
    `;
  },
  afterRender: async () => {
    const moviesList = document.getElementById('movies-list');
    const searchInput = document.getElementById('search-input');

    const fetchAndRenderMovies = async (query = '') => {
      try {
        moviesList.innerHTML = 'Loading...';
        const movies = await getMovies(query);
        
        if (movies.length === 0) {
            moviesList.innerHTML = '<p>Không tìm thấy phim nào.</p>';
            return;
        }

        moviesList.innerHTML = movies.map(movie => `
          <li style="margin-bottom: 15px; padding: 10px; border: 1px solid #eee; border-radius: 5px;">
            <h3>
              <a href="/movies/${movie.id}" style="text-decoration: none; color: #007bff;">
                ${movie.title}
              </a>
            </h3>
            <p>Thể loại: ${movie.genre}</p>
            <p>Thời lượng: ${movie.duration} phút</p>
            <p>Ngày phát hành: ${movie.release_date}</p>
          </li>
        `).join('');

      } catch (err) {
        moviesList.innerHTML = `<p style="color:red">Lỗi: ${err.message}</p>`;
      }
    };

    // Initial fetch
    await fetchAndRenderMovies();

    // Search event
    searchInput.addEventListener('input', (e) => {
        fetchAndRenderMovies(e.target.value);
    });
  }
};

export default MoviesPage;
