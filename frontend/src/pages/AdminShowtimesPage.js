import { getShowtimes, getMovies, createShowtime, updateShowtime, deleteShowtime } from '../api/apiClient.js';

const AdminShowtimesPage = {
  render: async () => {
    return `
      <div class="container py-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="fw-bold">Quản lý Lịch Chiếu</h2>
            <button id="add-showtime-btn" class="btn btn-success">
                <i class="bi bi-plus-circle"></i> + Thêm Lịch Chiếu
            </button>
        </div>

        <div class="card shadow-sm border-0">
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th class="ps-4">Phim</th>
                                <th>Bắt Đầu</th>
                                <th>Kết Thúc</th>
                                <th>Giá Vé (VND)</th>
                                <th class="text-end pe-4">Hành Động</th>
                            </tr>
                        </thead>
                        <tbody id="admin-showtimes-list">
                             <tr><td colspan="5" class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="mt-4">
            <a href="/admin/dashboard" class="text-decoration-none text-muted">&larr; Quay lại Dashboard</a>
        </div>

         <!-- Bootstrap Modal -->
        <div class="modal fade" id="showtimeModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="modal-title">Thêm Lịch Chiếu</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="showtime-form">
                            <input type="hidden" id="showtime-id">
                            <div class="mb-3">
                                <label class="form-label">Phim</label>
                                <select id="showtime-movie" class="form-select" required>
                                    <option value="">-- Chọn phim --</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Thời gian bắt đầu</label>
                                <input type="datetime-local" id="showtime-start" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Thời gian kết thúc</label>
                                <input type="datetime-local" id="showtime-end" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Giá vé</label>
                                <input type="number" id="showtime-price" class="form-control" required min="0">
                            </div>
                            <div class="text-end">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Hủy</button>
                                <button type="submit" class="btn btn-primary">Lưu</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
      </div>
    `;
  },
  afterRender: async () => {
    const list = document.getElementById('admin-showtimes-list');
    const addBtn = document.getElementById('add-showtime-btn');
    const form = document.getElementById('showtime-form');
    const modalTitle = document.getElementById('modal-title');
    
    // Initialize Bootstrap Modal
    const showtimeModal = new bootstrap.Modal(document.getElementById('showtimeModal'));

    // Inputs
    const idInput = document.getElementById('showtime-id');
    const movieSelect = document.getElementById('showtime-movie');
    const startInput = document.getElementById('showtime-start');
    const endInput = document.getElementById('showtime-end');
    const priceInput = document.getElementById('showtime-price');

    let showtimesData = [];
    let moviesData = [];

    const toLocalISO = (dateStr) => {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        const offset = date.getTimezoneOffset() * 60000;
        const localISOTime = (new Date(date - offset)).toISOString().slice(0, 16);
        return localISOTime;
    };

    const renderList = (showtimes) => {
        showtimesData = showtimes;
        if (showtimes.length === 0) {
            list.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">Chưa có lịch chiếu nào.</td></tr>';
            return;
        }

        list.innerHTML = showtimes.map(st => {
            const movie = moviesData.find(m => m.id === st.movie_id);
            const movieTitle = movie ? movie.title : `<span class="text-muted">Movie ID ${st.movie_id} (Đã xóa)</span>`;
            return `
              <tr>
                <td class="ps-4 fw-bold text-primary">${movieTitle}</td>
                <td>${new Date(st.start_time).toLocaleString()}</td>
                <td>${new Date(st.end_time).toLocaleString()}</td>
                <td>${st.price ? st.price.toLocaleString() : '0'}</td>
                <td class="text-end pe-4">
                    <button class="btn btn-sm btn-outline-primary me-2 edit-btn" data-id="${st.id}">Sửa</button>
                    <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${st.id}">Xóa</button>
                </td>
              </tr>
            `;
        }).join('');

        // Attach events
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => openEditModal(e.target.dataset.id));
        });
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => handleDelete(e.target.dataset.id));
        });
    };

    const loadData = async () => {
        try {
            const [movies, showtimes] = await Promise.all([getMovies(), getShowtimes()]);
            moviesData = movies;
            
            // Populate Movie Select
            movieSelect.innerHTML = '<option value="">-- Chọn phim --</option>' + 
                movies.map(m => `<option value="${m.id}">${m.title}</option>`).join('');

            renderList(showtimes);
        } catch (err) {
            list.innerHTML = `<tr><td colspan="5" class="text-center text-danger py-4">Lỗi tải dữ liệu: ${err.message}</td></tr>`;
        }
    };

    const openEditModal = (id) => {
        const showtime = showtimesData.find(s => s.id == id);
        if (showtime) {
            idInput.value = showtime.id;
            movieSelect.value = showtime.movie_id;
            startInput.value = toLocalISO(showtime.start_time);
            endInput.value = toLocalISO(showtime.end_time);
            priceInput.value = showtime.price;
            
            modalTitle.innerText = 'Sửa Lịch Chiếu';
            showtimeModal.show();
        }
    };

    addBtn.addEventListener('click', () => {
        form.reset();
        idInput.value = '';
        modalTitle.innerText = 'Thêm Lịch Chiếu';
        showtimeModal.show();
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = idInput.value;
        const data = {
            movie_id: parseInt(movieSelect.value),
            start_time: startInput.value,
            end_time: endInput.value,
            price: parseFloat(priceInput.value)
        };

        if (new Date(data.start_time) >= new Date(data.end_time)) {
            alert('Thời gian kết thúc phải sau thời gian bắt đầu.');
            return;
        }

        try {
            if (id) {
                await updateShowtime(id, data);
            } else {
                await createShowtime(data);
            }
            showtimeModal.hide();
            loadData();
        } catch (err) {
            alert('Lỗi: ' + err.message);
        }
    });

    const handleDelete = async (id) => {
        if (confirm('Bạn có chắc chắn muốn xóa lịch chiếu này?')) {
            try {
                await deleteShowtime(id);
                loadData();
            } catch (err) {
                alert('Lỗi: ' + err.message);
            }
        }
    };

    await loadData();
  }
};

export default AdminShowtimesPage;