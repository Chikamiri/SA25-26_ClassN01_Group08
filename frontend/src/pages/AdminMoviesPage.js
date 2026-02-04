import { getMovies, createMovie, updateMovie, deleteMovie, getAllBookings, getShowtimes } from '../api/apiClient.js';
import AdminSidebar from '../components/AdminSidebar.js';

const AdminMoviesPage = {
  render: async () => {
    return `
      <div class="admin-layout">
        ${AdminSidebar.render('movies')}
        <div class="admin-content">
            <div class="container-fluid">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2 class="fw-bold mb-0">Manage Movies</h2>
                    <button id="add-movie-btn" class="btn btn-primary shadow-sm">
                        <i class="bi bi-plus-lg"></i> Add New Movie
                    </button>
                </div>

                <div class="card shadow-sm border-0">
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th class="ps-4">Movie Title</th>
                                        <th>Genre</th>
                                        <th>Duration</th>
                                        <th>Release Date</th>
                                        <th>Total Revenue (VND)</th>
                                        <th class="text-end pe-4">Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="admin-movies-list">
                                    <tr><td colspan="5" class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                 <!-- Bootstrap Modal -->
                <div class="modal fade" id="movieModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header bg-light">
                                <h5 class="modal-title fw-bold" id="modal-title">Add Movie</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body p-4">
                                <form id="movie-form">
                                    <input type="hidden" id="movie-id">
                                    <div class="mb-3">
                                        <label class="form-label text-muted small fw-bold text-uppercase">Movie title</label>
                                        <input type="text" id="movie-title" class="form-control" required>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label text-muted small fw-bold text-uppercase">Genre</label>
                                        <input type="text" id="movie-genre" class="form-control" required>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label text-muted small fw-bold text-uppercase">Duration (minutes)</label>
                                            <input type="number" id="movie-duration" class="form-control" required min="1">
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label text-muted small fw-bold text-uppercase">Release date</label>
                                            <input type="date" id="movie-release-date" class="form-control" required>
                                        </div>
                                    </div>
                                    <div class="text-end mt-4">
                                        <button type="button" class="btn btn-light me-2" data-bs-dismiss="modal">Cancel</button>
                                        <button type="submit" class="btn btn-primary px-4">Save</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    `;
  },
  afterRender: async () => {
    AdminSidebar.afterRender();

    const list = document.getElementById('admin-movies-list');
    const addBtn = document.getElementById('add-movie-btn');
    const form = document.getElementById('movie-form');
    const modalTitle = document.getElementById('modal-title');
    
    // Initialize Bootstrap Modal
    const movieModal = new bootstrap.Modal(document.getElementById('movieModal'));

    // Inputs
    const idInput = document.getElementById('movie-id');
    const titleInput = document.getElementById('movie-title');
    const genreInput = document.getElementById('movie-genre');
    const durationInput = document.getElementById('movie-duration');
    const releaseDateInput = document.getElementById('movie-release-date');

    let moviesData = [];
    let bookingsData = [];
    let showtimesData = [];

    const renderList = (movies) => {
        moviesData = movies;
        if (movies.length === 0) {
            list.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-5">No movies yet.</td></tr>';
            return;
        }
        list.innerHTML = movies.map(movie => {
            // Find showtimes for this movie
            const movieShowtimes = showtimesData.filter(st => st.movie_id === movie.id);
            const showtimeIds = movieShowtimes.map(st => st.id);
            
            // Sum revenue of bookings for these showtimes
            const revenue = bookingsData
                .filter(b => showtimeIds.includes(b.showtime_id))
                .reduce((sum, b) => sum + (b.amount || 0), 0);

            return `
              <tr>
                <td class="ps-4 fw-bold text-primary">${movie.title}</td>
                <td><span class="badge bg-light text-dark border">${movie.genre}</span></td>
                <td>${movie.duration} minutes</td>
                <td>${new Date(movie.release_date).toLocaleDateString()}</td>
                <td class="fw-bold text-success">${revenue.toLocaleString()}</td>
                <td class="text-end pe-4">
                    <button class="btn btn-sm btn-outline-primary me-2 edit-btn" data-id="${movie.id}">
                        <i class="bi bi-pencil"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${movie.id}">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </td>
              </tr>
            `;
        }).join('');

        // Attach events
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => openEditModal(e.currentTarget.dataset.id));
        });
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => handleDelete(e.currentTarget.dataset.id));
        });
    };

    const fetchMovies = async () => {
        try {
            const [movies, bookings, showtimes] = await Promise.all([
                getMovies(),
                getAllBookings(),
                getShowtimes()
            ]);
            bookingsData = bookings;
            showtimesData = showtimes;
            renderList(movies);
        } catch (err) {
            list.innerHTML = `<tr><td colspan="6" class="text-center text-danger py-4">Error loading data: ${err.message}</td></tr>`;
        }
    };

    const openEditModal = (id) => {
        const movie = moviesData.find(m => m.id == id);
        if (movie) {
            idInput.value = movie.id;
            titleInput.value = movie.title;
            genreInput.value = movie.genre;
            durationInput.value = movie.duration;
            releaseDateInput.value = movie.release_date;
            modalTitle.innerText = 'Edit Movie';
            movieModal.show();
        }
    };

    addBtn.addEventListener('click', () => {
        form.reset();
        idInput.value = '';
        modalTitle.innerText = 'Add Movie';
        movieModal.show();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = idInput.value;
        const data = {
            title: titleInput.value,
            genre: genreInput.value,
            duration: parseInt(durationInput.value),
            release_date: releaseDateInput.value
        };

        if (data.duration <= 0) {
            alert('Duration must be greater than 0');
            return;
        }

        try {
            if (id) {
                await updateMovie(id, data);
            } else {
                await createMovie(data);
            }
            movieModal.hide();
            fetchMovies();
        } catch (err) {
            alert('Error: ' + err.message);
        }
    });

    const handleDelete = async (id) => {
        if (confirm('Are you sure you want to delete this movie?')) {
            try {
                await deleteMovie(id);
                fetchMovies();
            } catch (err) {
                alert('Error: ' + err.message);
            }
        }
    };

    await fetchMovies();
  }
};

export default AdminMoviesPage;