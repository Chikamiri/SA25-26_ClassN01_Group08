import { getMovieById, getShowtimes } from '../api/apiClient.js';

const MovieDetailsPage = {
  render: async () => {
    return `
      <div id="movie-detail-container">
        Loading detail...
      </div>
    `;
  },
  afterRender: async () => {
    const container = document.getElementById('movie-detail-container');
    
    // Lấy ID từ URL thủ công vì router của ta đơn giản
    const pathParts = window.location.pathname.split('/');
    const id = pathParts[2]; // /movies/1 -> id là 1

    if (!id) {
        container.innerHTML = '<p>Không tìm thấy ID phim.</p>';
        return;
    }

    try {
        // Fetch song song
        const [movie, showtimes] = await Promise.all([
            getMovieById(id),
            getShowtimes(id)
        ]);

        if (!movie) {
             container.innerHTML = '<p>Phim không tìm thấy.</p>';
             return;
        }

        const showtimesHTML = showtimes.length > 0 
            ? `<ul style="list-style: none; padding: 0;">
                ${showtimes.map(st => `
                    <li style="margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p><strong>Thời gian:</strong> ${st.start_time} - ${st.end_time}</p>
                            <p><strong>Giá vé:</strong> ${st.price ? st.price.toLocaleString() : 'N/A'} VND</p>
                        </div>
                        <a href="/book/${st.id}" style="padding: 8px 12px; background-color: #28a745; color: white; text-decoration: none; border-radius: 4px;">
                            Đặt vé
                        </a>
                    </li>
                `).join('')}
               </ul>`
            : '<p>Hiện không có suất chiếu nào cho phim này.</p>';

        container.innerHTML = `
            <h2>${movie.title}</h2>
            <p><strong>Thể loại:</strong> ${movie.genre}</p>
            <p><strong>Thời lượng:</strong> ${movie.duration} phút</p>
            <p><strong>Ngày phát hành:</strong> ${movie.release_date}</p>
            <p><strong>Mô tả:</strong> ${movie.description || 'Không có mô tả.'}</p>

            <h3 style="margin-top: 30px;">Các Suất Chiếu</h3>
            ${showtimesHTML}

            <div style="margin-top: 30px;">
                <a href="/movies" style="text-decoration: none; color: #6c757d; margin-right: 10px;">&larr; Quay lại danh sách phim</a>
            </div>
        `;

    } catch (err) {
        container.innerHTML = `<p style="color: red;">Lỗi: ${err.message}</p>`;
    }
  }
};

export default MovieDetailsPage;
