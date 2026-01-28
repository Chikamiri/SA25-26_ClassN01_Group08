import { getShowtimes } from '../api/apiClient.js';

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
      </div>
    `;
  },
  afterRender: async () => {
    const list = document.getElementById('admin-showtimes-list');
    const addBtn = document.getElementById('add-showtime-btn');

    addBtn.addEventListener('click', () => {
        alert('Chức năng Thêm lịch chiếu chưa được cài đặt (TODO).');
    });

    try {
        const showtimes = await getShowtimes();
        if (showtimes.length === 0) {
            list.innerHTML = '<p>Không có lịch chiếu nào.</p>';
            return;
        }

        list.innerHTML = showtimes.map(st => `
          <li style="margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>Showtime #${st.id}</strong> - Phim ID: ${st.movie_id}<br/>
                ${st.start_time} - ${st.end_time}
            </div>
            <div>
                <button onclick="alert('Edit showtime ID: ${st.id} (TODO)')" style="margin-right: 5px;">Sửa</button>
                <button onclick="alert('Delete showtime ID: ${st.id} (TODO)')" style="color: red;">Xóa</button>
            </div>
          </li>
        `).join('');
    } catch (err) {
        list.innerHTML = `<p style="color:red">Lỗi tải dữ liệu: ${err.message}</p>`;
    }
  }
};

export default AdminShowtimesPage;
