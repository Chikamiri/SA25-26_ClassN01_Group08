import { getMovies, createMovie, updateMovie, deleteMovie } from '../api/apiClient.js';
import AdminSidebar from '../components/AdminSidebar.js';

const AdminMoviesPage = {
  render: async () => {
    return `
      <div class="admin-layout">
        ${AdminSidebar.render('movies')}
        <div class="admin-content">
            <div class="container-fluid">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2 class="fw-bold mb-0">Quản lý Phim</h2>
                    <button id="add-movie-btn" class="btn btn-primary shadow-sm">
                        <i class="bi bi-plus-lg"></i> Thêm Phim Mới
                    </button>
                </div>

                <div class="card shadow-sm border-0">
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th class="ps-4">Tên Phim</th>
                                        <th>Thể Loại</th>
                                        <th>Thời Lượng</th>
                                        <th>Ngày Phát Hành</th>
                                        <th class="text-end pe-4">Hành Động</th>
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
                                <h5 class="modal-title fw-bold" id="modal-title">Thêm Phim</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body p-4">
                                <form id="movie-form">
                                    <input type="hidden" id="movie-id">
                                    <div class="mb-3">
                                        <label class="form-label text-muted small fw-bold text-uppercase">Tên phim</label>
                                        <input type="text" id="movie-title" class="form-control" required>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label text-muted small fw-bold text-uppercase">Thể loại</label>
                                        <input type="text" id="movie-genre" class="form-control" required>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label text-muted small fw-bold text-uppercase">Thời lượng (phút)</label>
                                            <input type="number" id="movie-duration" class="form-control" required min="1">
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label text-muted small fw-bold text-uppercase">Ngày phát hành</label>
                                            <input type="date" id="movie-release-date" class="form-control" required>
                                        </div>
                                    </div>
                                    <div class="text-end mt-4">
                                        <button type="button" class="btn btn-light me-2" data-bs-dismiss="modal">Hủy</button>
                                        <button type="submit" class="btn btn-primary px-4">Lưu</button>
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

    const renderList = (movies) => {
        moviesData = movies;
        if (movies.length === 0) {
            list.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-5">Chưa có phim nào.</td></tr>';
            return;
        }
        list.innerHTML = movies.map(movie => `
          <tr>
            <td class="ps-4 fw-bold text-primary">${movie.title}</td>
            <td><span class="badge bg-light text-dark border">${movie.genre}</span></td>
            <td>${movie.duration} phút</td>
            <td>${new Date(movie.release_date).toLocaleDateString()}</td>
            <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-primary me-2 edit-btn" data-id="${movie.id}">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${movie.id}">
                    <i class="bi bi-trash"></i>
                </button>
            </td>
          </tr>
        `).join('');

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
            const movies = await getMovies();
            renderList(movies);
        } catch (err) {
            list.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">Lỗi tải dữ liệu: ${err.message}</td></tr>`;
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
            modalTitle.innerText = 'Sửa Phim';
            movieModal.show();
        }
    };

    addBtn.addEventListener('click', () => {
        form.reset();
        idInput.value = '';
        modalTitle.innerText = 'Thêm Phim';
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
            alert('Thời lượng phải lớn hơn 0');
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
            alert('Lỗi: ' + err.message);
        }
    });

    const handleDelete = async (id) => {
        if (confirm('Bạn có chắc chắn muốn xóa phim này?')) {
            try {
                await deleteMovie(id);
                fetchMovies();
            } catch (err) {
                alert('Lỗi: ' + err.message);
            }
        }
    };

    await fetchMovies();
  }
};

export default AdminMoviesPage;