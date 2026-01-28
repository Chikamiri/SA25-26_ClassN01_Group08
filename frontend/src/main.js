import Header from './components/Header.js';
import HomePage from './pages/HomePage.js';
import LoginPage from './pages/LoginPage.js';
import MoviesPage from './pages/MoviesPage.js';
import MovieDetailsPage from './pages/MovieDetailsPage.js';
import AdminLoginPage from './pages/AdminLoginPage.js';
import AdminDashboardPage from './pages/AdminDashboardPage.js';
import AdminMoviesPage from './pages/AdminMoviesPage.js';
import AdminShowtimesPage from './pages/AdminShowtimesPage.js';
import BookingsPage from './pages/BookingsPage.js';
import MyBookingsPage from './pages/MyBookingsPage.js';
import './index.css';

// Hỗ trợ Router
const parseUrl = () => {
    const path = window.location.pathname.toLowerCase() || '/';
    const r = path.split("/");
    // path: /resource/id/verb
    return {
        resource: r[1],
        id: r[2],
        verb: r[3]
    };
}

const routes = {
    '/': HomePage,
    '/login': LoginPage,
    '/admin/login': AdminLoginPage,
    '/admin/dashboard': AdminDashboardPage,
    '/admin/movies/manage': AdminMoviesPage,
    '/admin/showtimes/manage': AdminShowtimesPage,
    '/movies': MoviesPage,
    '/movies/:id': MovieDetailsPage,
    '/book/:id': BookingsPage,
    '/my-bookings': MyBookingsPage
};

const router = async () => {
    const content = document.getElementById('root');
    const request = parseUrl();
    
    // Xây dựng parsed URL để match với routes object
    // Nếu request.resource tồn tại thì là /resource
    // Nếu có id thì là /resource/:id
    const parsedUrl = (request.resource ? `/${request.resource}` : '/') + 
                      (request.id ? '/:id' : '') + 
                      (request.verb ? `/${request.verb}` : '');
    
    // Tìm page
    const page = routes[parsedUrl] ? routes[parsedUrl] : HomePage;

    // Render Header
    const headerHTML = Header.render();
    content.innerHTML = headerHTML + '<div id="page-container" style="padding: 0 20px;">Loading...</div>'; // Placeholder

    // Render Page
    const pageContainer = document.getElementById('page-container');
    pageContainer.innerHTML = await page.render();

    // After Render
    if (Header.afterRender) Header.afterRender();
    if (page.afterRender) await page.afterRender();
};

// Navigation helper
const navigateTo = (url) => {
    history.pushState(null, null, url);
    router();
};

window.addEventListener('popstate', router);

document.addEventListener('DOMContentLoaded', () => {
    document.body.addEventListener('click', e => {
        // Tìm thẻ a gần nhất
        const target = e.target.closest('a'); 
        
        // Kiểm tra nếu là link nội bộ (cùng host) và không phải là download/external
        if (target && target.href && target.host === window.location.host && !target.hasAttribute('download')) {
             e.preventDefault();
             navigateTo(target.href);
        }
    });
    router();
});
