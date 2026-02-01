import { getMovies, createMovie, updateMovie, deleteMovie } from '../api/apiClient.js';

const AdminMoviesPage = {
  render: async () => {
    return `
      <div>
        <h2>Quản lý Phim</h2>
        <div style="margin-bottom: 20px;">
            <button id="add-movie-btn" style="padding: 10px 15px; background-color: #28a745; color: white; border: none; cursor: pointer;">+ Thêm Phim Mới</button>
        </div>
        <ul id="admin-movies-list" style="list-style: none; padding: 0;">
          Loading movies...
        </ul>
        <p style="margin-top: 20px;">
            <a href="/admin/dashboard" style="text-decoration: none; color: #6c757d;">&larr; Quay lại Dashboard</a>
        </p>

        <!-- Modal -->
        <div id="movie-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center;">
            <div style="background: white; padding: 20px; border-radius: 5px; width: 400px; position: relative;">
                <h3 id="modal-title">Thêm Phim</h3>
                <form id="movie-form">
                    <input type="hidden" id="movie-id">
                    <div style="margin-bottom: 10px;">
                        <label>Tên phim:</label>
                        <input type="text" id="movie-title" style="width: 100%; padding: 5px;" required>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Thể loại:</label>
                        <input type="text" id="movie-genre" style="width: 100%; padding: 5px;" required>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Thời lượng (phút):</label>
                        <input type="number" id="movie-duration" style="width: 100%; padding: 5px;" required min="1">
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Ngày phát hành:</label>
                        <input type="date" id="movie-release-date" style="width: 100%; padding: 5px;" required>
                    </div>
                    <div style="text-align: right;">
                        <button type="button" id="cancel-btn" style="margin-right: 10px; padding: 5px 10px; cursor: pointer;">Hủy</button>
                        <button type="submit" style="padding: 5px 10px; background-color: #007bff; color: white; border: none; cursor: pointer;">Lưu</button>
                    </div>
                </form>
            </div>
        </div>
      </div>
    `;
  },
  afterRender: async () => {
    const list = document.getElementById('admin-movies-list');
    const addBtn = document.getElementById('add-movie-btn');
    const modal = document.getElementById('movie-modal');
    const form = document.getElementById('movie-form');
    const cancelBtn = document.getElementById('cancel-btn');
    const modalTitle = document.getElementById('modal-title');

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
            list.innerHTML = '<p>Không có phim nào.</p>';
            return;
        }
        list.innerHTML = movies.map(movie => `
          <li style="margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>${movie.title}</strong> (${movie.duration} phút)<br>
                <small>${movie.genre} | ${movie.release_date}</small>
            </div>
            <div>
                <button class="edit-btn" data-id="${movie.id}" style="margin-right: 5px; cursor: pointer;">Sửa</button>
                <button class="delete-btn" data-id="${movie.id}" style="color: red; cursor: pointer;">Xóa</button>
            </div>
          </li>
        `).join('');

        // Attach events
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => openEditModal(e.target.dataset.id));
        });
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => handleDelete(e.target.dataset.id));
        });
    };

    const fetchMovies = async () => {
        try {
            const movies = await getMovies();
            renderList(movies);
        } catch (err) {
            list.innerHTML = `<p style="color:red">Lỗi tải dữ liệu: ${err.message}</p>`;
        }
    };

    const openModal = () => {
        modal.style.display = 'flex';
    };

    const closeModal = () => {
        modal.style.display = 'none';
        form.reset();
        idInput.value = '';
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
            openModal();
        }
    };

    addBtn.addEventListener('click', () => {
        modalTitle.innerText = 'Thêm Phim';
        openModal();
    });

    cancelBtn.addEventListener('click', closeModal);

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
                alert('Cập nhật thành công!');
            } else {
                await createMovie(data);
                alert('Thêm mới thành công!');
            }
            closeModal();
            fetchMovies();
        } catch (err) {
            alert('Lỗi: ' + err.message);
        }
    });

    const handleDelete = async (id) => {
        if (confirm('Bạn có chắc chắn muốn xóa phim này?')) {
            try {
                await deleteMovie(id);
                alert('Xóa thành công!');
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