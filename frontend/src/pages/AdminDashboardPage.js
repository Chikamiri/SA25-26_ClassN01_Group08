
import AdminSidebar from '../components/AdminSidebar.js';
import { getMovies, getAllBookings, getAllUsers } from '../api/apiClient.js';

const AdminDashboardPage = {
  render: async () => {
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (!user || user.role !== 'admin') {
        return `
          <div class="container py-5 text-center">
            <div class="alert alert-danger d-inline-block shadow-sm">
              <h4 class="alert-heading"><i class="bi bi-shield-lock"></i> Access Denied!</h4>
              <p>You do not have permission to access this page.</p>
              <hr>
              <a href="/admin/login" class="btn btn-outline-danger btn-sm">Admin Login</a>
            </div>
          </div>
        `;
    }

    // Fetch Data
    let moviesCount = 0;
    let revenue = 0;
    let bookingsCount = 0;
    let usersCount = 0;
    let recentActivity = [];

    try {
        const [movies, bookings, users] = await Promise.all([
            getMovies(),
            getAllBookings(),
            getAllUsers()
        ]);

        moviesCount = movies.length;
        
        if (Array.isArray(bookings)) {
            bookingsCount = bookings.length;
            revenue = bookings.reduce((sum, b) => sum + (b.price || 0), 0);
            
            // Get last 5 bookings for activity
            recentActivity = bookings.sort((a,b) => b.id - a.id).slice(0, 5);
        }

        if (Array.isArray(users)) {
            usersCount = users.filter(u => u.role === 'customer').length;
        }

    } catch (e) {
        console.error("Error fetching dashboard stats:", e);
    }

    const formatCurrency = (val) => {
        return val.toLocaleString('vi-VN') + ' VND';
    };

    return `
      <div class="admin-layout">
        ${AdminSidebar.render('dashboard')}
        
        <div class="admin-content">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h2 class="fw-bold mb-0">Dashboard Overview</h2>
                <div class="text-muted">Hello, <span class="fw-bold text-dark">${user.email}</span></div>
            </div>

            <!-- Stats Row -->
            <div class="row g-4 mb-4">
                <div class="col-md-3">
                    <div class="card stat-card bg-primary text-white h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-white-50 text-uppercase small fw-bold">Total Movies</h6>
                                    <h2 class="mb-0 fw-bold">${moviesCount}</h2>
                                </div>
                                <i class="bi bi-film fs-1 opacity-50"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card bg-success text-white h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-white-50 text-uppercase small fw-bold">Revenue</h6>
                                    <h2 class="mb-0 fw-bold">${(revenue/1000000).toFixed(1)}M</h2>
                                    <small class="text-white-50" style="font-size: 0.7rem;">${formatCurrency(revenue)}</small>
                                </div>
                                <i class="bi bi-currency-dollar fs-1 opacity-50"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card bg-warning text-dark h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-black-50 text-uppercase small fw-bold">Booked Tickets</h6>
                                    <h2 class="mb-0 fw-bold">${bookingsCount}</h2>
                                </div>
                                <i class="bi bi-ticket-perforated fs-1 opacity-50"></i>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card stat-card bg-info text-white h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="text-white-50 text-uppercase small fw-bold">Customers</h6>
                                    <h2 class="mb-0 fw-bold">${usersCount}</h2>
                                </div>
                                <i class="bi bi-people fs-1 opacity-50"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Actions & Recent Activity -->
            <div class="row g-4">
                <div class="col-lg-8">
                    <div class="card shadow-sm border-0 h-100">
                        <div class="card-header bg-white py-3 fw-bold border-bottom">
                            <i class="bi bi-clock-history"></i> Recent Booking Activity
                        </div>
                        <div class="list-group list-group-flush">
                             ${recentActivity.length === 0 ? '<div class="p-4 text-center text-muted">No activity yet.</div>' : ''}
                             ${recentActivity.map(b => `
                                 <div class="list-group-item px-4 py-3">
                                    <div class="d-flex w-100 justify-content-between">
                                        <h6 class="mb-1 text-primary">Booking #${b.id}</h6>
                                        <small class="text-muted fw-bold">${b.price ? b.price.toLocaleString() : 0} VND</small>
                                    </div>
                                    <p class="mb-1 small">
                                        Customer: <strong>${b.user_email || 'Unknown'}</strong><br>
                                        Seat: ${b.seat_number}
                                    </p>
                                 </div>
                             `).join('')}
                             
                             <div class="list-group-item px-4 py-3 text-center text-muted small bg-light">
                                <a href="#" onclick="alert('View all bookings feature is under development')" class="text-decoration-none">View all activity</a>
                             </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card shadow-sm border-0 h-100">
                        <div class="card-header bg-white py-3 fw-bold border-bottom">
                            <i class="bi bi-lightning-charge"></i> Quick Actions
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-3">
                                <a href="/admin/movies/manage" class="btn btn-outline-primary text-start p-3">
                                    <i class="bi bi-film me-2"></i> Manage Movies
                                </a>
                                <a href="/admin/showtimes/manage" class="btn btn-outline-dark text-start p-3">
                                    <i class="bi bi-calendar-plus me-2"></i> Add Showtime
                                </a>
                                <button class="btn btn-outline-secondary text-start p-3" disabled>
                                    <i class="bi bi-printer me-2"></i> Export Report (Coming Soon)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    `;
  },
  afterRender: () => {
     AdminSidebar.afterRender();
  }
};

export default AdminDashboardPage;
