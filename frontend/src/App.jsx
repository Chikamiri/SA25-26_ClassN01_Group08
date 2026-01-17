import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import React, { useState, useEffect } from 'react';

// --- Import các component trang ---
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import AdminLoginPage from './pages/AdminLoginPage';
import MoviesPage from './pages/MoviesPage';
import MovieDetailsPage from './pages/MovieDetailsPage';
import BookingsPage from './pages/BookingsPage';
import MyBookingsPage from './pages/MyBookingsPage';
import AdminDashboardPage from './pages/AdminDashboardPage';

// --- Component Chính App ---
function App() {
    // Giả lập trạng thái người dùng đã đăng nhập
    // Kiểm tra localStorage khi ứng dụng khởi động để khôi phục trạng thái đăng nhập
    const [user, setUser] = useState(() => {
        const storedUser = localStorage.getItem('user');
        return storedUser ? JSON.parse(storedUser) : null;
    });

    // Hàm xử lý đăng nhập: cập nhật state và lưu vào localStorage
    const handleLogin = (userData) => {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        alert('Đăng nhập thành công!'); // Thông báo giả lập
    };

    // Hàm đăng xuất: xóa state và xóa khỏi localStorage
    const handleLogout = () => {
        setUser(null);
        localStorage.removeItem('user');
        alert('Bạn đã đăng xuất.'); // Thông báo giả lập
    };

    return (
        <Router>
            {/* Thanh điều hướng đơn giản */}
            <nav style={{ padding: '10px', backgroundColor: '#f0f0f0', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <a href="/" style={{ marginRight: '15px', textDecoration: 'none', color: '#333' }}>Trang Chủ</a>
                    <a href="/movies" style={{ marginRight: '15px', textDecoration: 'none', color: '#333' }}>Phim</a>
                    {user && user.role === 'customer' && (
                        <a href="/my-bookings" style={{ marginRight: '15px', textDecoration: 'none', color: '#333' }}>Vé Của Tôi</a>
                    )}
                    {user && user.role === 'admin' && (
                        <a href="/admin/dashboard" style={{ marginRight: '15px', textDecoration: 'none', color: '#333' }}>Admin</a>
                    )}
                </div>
                <div>
                    {!user ? (
                        <>
                            <a href="/login" style={{ marginRight: '15px', textDecoration: 'none', color: '#333' }}>Đăng Nhập</a>
                            <a href="/admin/login" style={{ textDecoration: 'none', color: '#333' }}>Đăng Nhập Admin</a>
                        </>
                    ) : (
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                            <span style={{ marginRight: '15px' }}>Xin chào, {user.email} ({user.role})</span>
                            <button onClick={handleLogout} style={{ padding: '5px 10px', cursor: 'pointer' }}>Đăng xuất</button>
                        </div>
                    )}
                </div>
            </nav>

            <div style={{ padding: '0 20px' }}> {/* Container cho nội dung trang */}
                <Routes>
                    {/* Trang Chủ */}
                    <Route path="/" element={<HomePage />} />

                    {/* Trang Đăng Nhập Người Dùng - Chuyển hướng nếu đã đăng nhập */}
                    <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage onLogin={handleLogin} />} />

                    {/* Trang Đăng Nhập Admin - Chuyển hướng nếu đã đăng nhập */}
                    <Route path="/admin/login" element={user ? <Navigate to="/" replace /> : <AdminLoginPage onLogin={handleLogin} />} />

                    {/* Trang Danh sách Phim */}
                    <Route path="/movies" element={<MoviesPage />} />
                    {/* Trang Chi tiết Phim */}
                    <Route path="/movies/:id" element={<MovieDetailsPage />} />

                    {/* Trang Đặt Vé - Yêu cầu đăng nhập */}
                    <Route path="/book/:showtimeId" element={user ? <BookingsPage /> : <Navigate to="/login" replace />} />

                    {/* Trang Các Vé Đã Đặt Của Tôi - Yêu cầu đăng nhập */}
                    <Route path="/my-bookings" element={user ? <MyBookingsPage /> : <Navigate to="/login" replace />} />

                    {/* Trang Quản lý Admin - Chỉ dành cho Admin */}
                    <Route path="/admin/dashboard" element={user && user.role === 'admin' ? <AdminDashboardPage /> : <Navigate to="/login" replace />} />

                    {/* Route mặc định cho các trang không tìm thấy - Chuyển hướng về Trang Chủ */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;