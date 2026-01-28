import { getMovies } from '../api/apiClient.js';

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
      </div>
    `;
  },
  afterRender: async () => {
    const list = document.getElementById('admin-movies-list');
    const addBtn = document.getElementById('add-movie-btn');

    addBtn.addEventListener('click', () => {
        alert('Chức năng Thêm phim chưa được cài đặt (TODO).');
    });

    try {
        const movies = await getMovies();
        if (movies.length === 0) {
            list.innerHTML = '<p>Không có phim nào.</p>';
            return;
        }

        list.innerHTML = movies.map(movie => `
          <li style="margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>${movie.title}</strong> (${movie.duration} phút)
            </div>
            <div>
                <button onclick="alert('Edit movie ID: ${movie.id} (TODO)')" style="margin-right: 5px;">Sửa</button>
                <button onclick="alert('Delete movie ID: ${movie.id} (TODO)')" style="color: red;">Xóa</button>
            </div>
          </li>
        `).join('');
    } catch (err) {
        list.innerHTML = `<p style="color:red">Lỗi tải dữ liệu: ${err.message}</p>`;
    }
  }
};

export default AdminMoviesPage;
