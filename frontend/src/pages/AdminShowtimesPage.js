import { getShowtimes, getMovies, createShowtime, updateShowtime, deleteShowtime } from '../api/apiClient.js';

const AdminShowtimesPage = {
  render: async () => {
    return `
      <div>
        <h2>Quản lý Lịch Chiếu</h2>
        <div style="margin-bottom: 20px;">
            <button id="add-showtime-btn" style="padding: 10px 15px; background-color: #28a745; color: white; border: none; cursor: pointer;">+ Thêm Lịch Chiếu</button>
        </div>
        <ul id="admin-showtimes-list" style="list-style: none; padding: 0;">
          Loading showtimes...
        </ul>
        <p style="margin-top: 20px;">
            <a href="/admin/dashboard" style="text-decoration: none; color: #6c757d;">&larr; Quay lại Dashboard</a>
        </p>

         <!-- Modal -->
        <div id="showtime-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); justify-content: center; align-items: center;">
            <div style="background: white; padding: 20px; border-radius: 5px; width: 400px; position: relative;">
                <h3 id="modal-title">Thêm Lịch Chiếu</h3>
                <form id="showtime-form">
                    <input type="hidden" id="showtime-id">
                    <div style="margin-bottom: 10px;">
                        <label>Phim:</label>
                        <select id="showtime-movie" style="width: 100%; padding: 5px;" required>
                            <option value="">-- Chọn phim --</option>
                        </select>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Thời gian bắt đầu:</label>
                        <input type="datetime-local" id="showtime-start" style="width: 100%; padding: 5px;" required>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Thời gian kết thúc:</label>
                        <input type="datetime-local" id="showtime-end" style="width: 100%; padding: 5px;" required>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Giá vé:</label>
                        <input type="number" id="showtime-price" style="width: 100%; padding: 5px;" required min="0">
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
    const list = document.getElementById('admin-showtimes-list');
    const addBtn = document.getElementById('add-showtime-btn');
    const modal = document.getElementById('showtime-modal');
    const form = document.getElementById('showtime-form');
    const cancelBtn = document.getElementById('cancel-btn');
    const modalTitle = document.getElementById('modal-title');

    // Inputs
    const idInput = document.getElementById('showtime-id');
    const movieSelect = document.getElementById('showtime-movie');
    const startInput = document.getElementById('showtime-start');
    const endInput = document.getElementById('showtime-end');
    const priceInput = document.getElementById('showtime-price');

    let showtimesData = [];
    let moviesData = [];

    // Helper to format date for datetime-local input (YYYY-MM-DDTHH:mm)
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
            list.innerHTML = '<p>Không có lịch chiếu nào.</p>';
            return;
        }

        list.innerHTML = showtimes.map(st => {
            const movie = moviesData.find(m => m.id === st.movie_id);
            const movieTitle = movie ? movie.title : `Movie ID ${st.movie_id}`;
            return `
              <li style="margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>${movieTitle}</strong><br/>
                    Start: ${st.start_time}<br/>
                    End: ${st.end_time}<br/>
                    Price: ${st.price}
                </div>
                <div>
                    <button class="edit-btn" data-id="${st.id}" style="margin-right: 5px; cursor: pointer;">Sửa</button>
                    <button class="delete-btn" data-id="${st.id}" style="color: red; cursor: pointer;">Xóa</button>
                </div>
              </li>
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
        const showtime = showtimesData.find(s => s.id == id);
        if (showtime) {
            idInput.value = showtime.id;
            movieSelect.value = showtime.movie_id;
            // Assuming start_time and end_time from API are parseable strings
            startInput.value = toLocalISO(showtime.start_time);
            endInput.value = toLocalISO(showtime.end_time);
            priceInput.value = showtime.price;
            
            modalTitle.innerText = 'Sửa Lịch Chiếu';
            openModal();
        }
    };

    addBtn.addEventListener('click', () => {
        modalTitle.innerText = 'Thêm Lịch Chiếu';
        openModal();
    });

    cancelBtn.addEventListener('click', closeModal);

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
                alert('Cập nhật thành công!');
            } else {
                await createShowtime(data);
                alert('Thêm mới thành công!');
            }
            closeModal();
            loadData(); // Reload both to ensure data consistency
        } catch (err) {
            alert('Lỗi: ' + err.message);
        }
    });

    const handleDelete = async (id) => {
        if (confirm('Bạn có chắc chắn muốn xóa lịch chiếu này?')) {
            try {
                await deleteShowtime(id);
                alert('Xóa thành công!');
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