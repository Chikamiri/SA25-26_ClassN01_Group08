# Changelog

## 6/12/2025, 14:05

- Create README.md, changelog.md
- Create folder 'src', 'Design' and 'Documents'

## 16/12/2025, 15:38

- Add folders
- Add placeholder for each
- Add .gitignore
- Add requirements

## 20/12/2025

- Create booking_service.py in business_logic
- Create models.py in business_logic
- Create booking_repository.py in persistence
- Create app.py

## 1/1/2026

- Implement database (`movies.db` & `booking.db`)
- Refactor project structure into Microservices: `movie` (Admin) & `booking` (Customer)
- Implement `MovieService`: Add logic to auto-generate seats when creating showtimes
- Implement `BookingService`: Add logic to view available seats and book tickets

## 2/1/2026

- Add search functionality (filter by title & genre) for movies
- Update Movie & Showtime models to support manual ID input
- Complete CRUD operations for Movie Service

## 3/1/2026

- Add Api gateway
- Add run_app.py 

## 9/1/2026

- Implement security api-key
- Refactor architecture: Decouple `MovieService` and `BookingService` using Internal APIs (replaced direct Repository access).
- Implement `PaymentService`: Handle payments and invoice generation with SQLite.
- Implement `NotificationService`: Consumer service to listen for RabbitMQ events (Mock Email/Print logs).
- Integrate RabbitMQ (Docker): Enable Event-Driven communication for `OrderPlacedEvent` and `InvoiceGenerated` events.
- Update `run_app.py`: Register Payment and Notification services to the orchestration script.

## 11/1/2026

- Update gateway and notification
- Patch some code errors in movie, booking and payment

## 13/1/2026

- Add User folder
- Implement admin/user login logic
- Implement user register logic
- Update Notification

## 14/1/2026, 16:48
- Create issue report file
- Fix issue related to how process stop in Linux
- Modify database path resolution
- Update test file to match with new code

## 14/1/2026, 17:40
- Add more tests

## 28/1/2026
- Fix frontend login bug (mismatched 'email' vs 'username' keys)
- Fix missing Admin management routes in frontend router
- Create AdminMoviesPage and AdminShowtimesPage for movie/showtime management

## 2/2/2026
- Refactored Gateway to use `flask-cors` properly; allowed custom headers `peko-key`, `Authorization`, `X-User-Email` to fix "Missing or Invalid Header" errors.
- Enabled CORS for all individual microservices (`user`, `movie`, `booking`, `payment`) for easier testing and isolation.
- Implemented atomic seat locking (SQL `UPDATE ... WHERE status='available'`) in `BookingRepository` to prevent double-booking (ASR 2 compliance).
- Added backend endpoints (`GET /api/showtimes/<id>/seats`) to support visual seat selection.
- Connected Frontend to Payment Service; updated booking flow to "Reserve (Pending) -> Pay -> Confirm".
- Replaced manual seat text input with a 10x10 interactive visual seat map; added "My Bookings" page with real API data.
- Big UI changes.
- Add '.db' to .gitignore