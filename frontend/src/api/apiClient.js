// src/api/apiClient.js

// Base URL cho API Gateway. Theo kế hoạch, nó chạy trên port 5000.
export const API_GATEWAY_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000/api';

// Hàm helper để thực hiện các yêu cầu fetch với header Authorization nếu có
export async function request(endpoint, options = {}) {
  const user = localStorage.getItem('user');
  const userToken = user ? JSON.parse(user).token : null;
  const userEmail = user ? JSON.parse(user).email : null;

  const headers = {
    'Content-Type': 'application/json',
    'peko-key': 'BO_CHIKA',
    ...(options.headers || {}),
  };

  // Thêm header Authorization nếu có token
  if (userToken) {
    headers['Authorization'] = `Bearer ${userToken}`;
  }
  // Thêm header X-User-Email nếu có email
  if (userEmail) {
    headers['X-User-Email'] = userEmail;
  }

  const url = `${API_GATEWAY_URL}/${endpoint}`;

  try {
    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
      // Xử lý các lỗi HTTP
      let errorData;
      try {
        errorData = await response.json();
      } catch (parseError) {
        errorData = { error: 'Unknown server error' };
      }
      
      const errorMessage = errorData.error || `Error ${response.status}: ${response.statusText}`;
      throw new Error(errorMessage);
    }

    if (response.status === 204) {
      return null;
    }
    return await response.json();

  } catch (error) {
    console.error('API request failed:', error);
    
    // Phân biệt lỗi Network (Fetch Error) với lỗi từ Server trả về
    if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
      throw new Error('Cannot connect to Server (Gateway is down or Network error)');
    }
    
    throw error;
  }
}

// Hàm helper cho việc đăng nhập
export async function loginUser(credentials) {
  // credentials sẽ là { email, password }
  return request('auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
}

// --- Các hàm API liên quan đến Phim và Suất Chiếu ---

// Lấy danh sách phim
export async function getMovies(query = '') {
  const endpoint = query ? `movies?query=${encodeURIComponent(query)}` : 'movies';
  return request(endpoint, { method: 'GET' });
}

// Lấy chi tiết một bộ phim
export async function getMovieById(id) {
  return request(`movies/${id}`, { method: 'GET' });
}

// Lấy danh sách suất chiếu cho một bộ phim (hoặc tất cả nếu movieId là null)
export async function getShowtimes(movieId = null) {
  const endpoint = movieId ? `showtimes?movie_id=${encodeURIComponent(movieId)}` : 'showtimes';
  return request(endpoint, { method: 'GET' });
}

// Lấy danh sách ghế của suất chiếu
export async function getShowtimeSeats(showtimeId) {
  return request(`showtimes/${showtimeId}/seats`, { method: 'GET' });
}

// Lấy danh sách phòng chiếu
export async function getRooms() {
  return request('rooms', { method: 'GET' });
}

// --- Các hàm API liên quan đến Đặt vé ---

// Đặt vé
export async function bookTicket(bookingData) {
  // bookingData sẽ chứa { showtime_id, seat_number }
  // Email của người dùng sẽ được thêm tự động bởi hàm request (qua header X-User-Email)
  return request('bookings', {
    method: 'POST',
    body: JSON.stringify(bookingData),
  });
}

// Lấy danh sách vé đã đặt của tôi
export async function getMyBookings() {
  return request('bookings/my', { method: 'GET' });
}

// Xử lý thanh toán
export async function processPayment(paymentData) {
  // paymentData: { booking_id }
  return request('payments', {
    method: 'POST',
    body: JSON.stringify(paymentData),
  });
}

// --- Các hàm API cho Admin (Movies) ---

export async function createMovie(movieData) {
  return request('movies', {
    method: 'POST',
    body: JSON.stringify(movieData),
  });
}

export async function updateMovie(id, movieData) {
  return request(`movies/${id}`, {
    method: 'PUT',
    body: JSON.stringify(movieData),
  });
}

export async function deleteMovie(id) {
  return request(`movies/${id}`, {
    method: 'DELETE',
  });
}

// --- Các hàm API cho Admin (Showtimes) ---

export async function createShowtime(showtimeData) {
  return request('showtimes', {
    method: 'POST',
    body: JSON.stringify(showtimeData),
  });
}

export async function updateShowtime(id, showtimeData) {
  return request(`showtimes/${id}`, {
    method: 'PUT',
    body: JSON.stringify(showtimeData),
  });
}

export async function deleteShowtime(id) {
  return request(`showtimes/${id}`, {
    method: 'DELETE',
  });
}
