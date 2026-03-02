import { getAllBookings, deleteBooking, getShowtimeDetail } from '../api/apiClient.js';
import AdminSidebar from '../components/AdminSidebar.js';

const AdminBookingsPage = {
  render: async () => {
    return `
      <div class="admin-layout">
        ${AdminSidebar.render('bookings')}
        <div class="admin-content">
            <div class="container-fluid">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2 class="fw-bold mb-0">Manage Bookings</h2>
                    <div>
                        <input type="text" id="booking-search" class="form-control" placeholder="Search by email..." style="width: 250px;">
                    </div>
                </div>

                <div class="card shadow-sm border-0">
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th class="ps-4">ID</th>
                                        <th>User Email</th>
                                        <th>Showtime</th>
                                        <th>Seats</th>
                                        <th>Amount</th>
                                        <th>Status</th>
                                        <th class="text-end pe-4">Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="admin-bookings-list">
                                    <tr><td colspan="7" class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>
    `;
  },
  afterRender: async () => {
    AdminSidebar.afterRender();

    const list = document.getElementById('admin-bookings-list');
    const searchInput = document.getElementById('booking-search');

    let allBookings = [];

    const renderList = (bookings) => {
        if (!bookings || bookings.length === 0) {
            list.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-5">No bookings found.</td></tr>';
            return;
        }

        // Sort by ID desc
        const sorted = [...bookings].sort((a,b) => b.id - a.id);

        list.innerHTML = sorted.map(b => `
          <tr>
            <td class="ps-4 fw-bold text-primary">#${b.id}</td>
            <td>${b.customer_email || b.email || 'N/A'}</td>
            <td>
                <small class="text-muted">ID: ${b.showtime_id}</small>
            </td>
            <td><span class="badge bg-light text-dark border">${b.seat_number}</span></td>
            <td>${b.amount ? b.amount.toLocaleString() : 0} VND</td>
            <td>
                <span class="badge ${b.status === 'confirmed' ? 'bg-success' : 'bg-warning text-dark'}">
                    ${b.status}
                </span>
            </td>
            <td class="text-end pe-4">
                <button class="btn btn-sm btn-outline-danger delete-btn" data-id="${b.id}">
                    <i class="bi bi-trash"></i> Cancel
                </button>
            </td>
          </tr>
        `).join('');

        // Attach events
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => handleDelete(e.currentTarget.dataset.id));
        });
    };

    const loadData = async () => {
        try {
            allBookings = await getAllBookings();
            renderList(allBookings);
        } catch (err) {
            list.innerHTML = `<tr><td colspan="7" class="text-center text-danger py-4">Error loading data: ${err.message}</td></tr>`;
        }
    };

    const handleDelete = async (id) => {
        if (confirm(`Are you sure you want to cancel booking #${id}? This will free up the seat.`)) {
            try {
                await deleteBooking(id);
                loadData(); // Reload
            } catch (err) {
                alert('Error: ' + err.message);
            }
        }
    };

    // Search Logic
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allBookings.filter(b => 
            (b.customer_email && b.customer_email.toLowerCase().includes(query)) ||
            (b.email && b.email.toLowerCase().includes(query)) ||
            (b.id.toString().includes(query))
        );
        renderList(filtered);
    });

    await loadData();
  }
};

export default AdminBookingsPage;
