# Checklist: Dự án Movie Ticket Booking System (Kiến trúc Phần mềm)

Tài liệu theo dõi tiến độ thực hiện bài tập lớn, chuyển đổi từ mô hình Monolith sang Microservices theo lộ trình Lab của môn học.

**Tech Stack:**

- **Ngôn ngữ:** Python3
- **Framework:** Flask
- **Database:** SQLite
- **Message Broker:** RabbitMQ
- **Tools:** Postman/cURL, Draw.io

## Giai đoạn 1: Kiến trúc Phân lớp (Layered Monolith)

*Mục tiêu: Xây dựng Core Logic xử lý phim và suất chiếu dưới dạng một khối thống nhất (Lab 2 & Lab 3).*

### Lab 2: Thiết kế Kiến trúc (Logical View)

- [x] **Xác định 4 tầng (Layers):**
  - [x] Presentation Layer (API Controllers)
  - [x] Business Logic Layer (Services)
  - [x] Persistence Layer (Repositories)
  - [x] Data Layer (Database)
- [x] **Vẽ sơ đồ Component (Component Diagram):**
  - [x] Minh họa flow: `MovieController` -> `MovieService` -> `MovieRepository`.
  - [x] Định nghĩa Interface cho các component này.

### Lab 3: Hiện thực hóa (Implementation)

- [ ] **Setup Project Python Flask:**
  - [x] Cấu trúc thư mục: `presentation/`, `business_logic/`, `persistence/`.
  - [ ] Cài đặt môi trường ảo (venv) và thư viện Flask.
- [ ] **Database & Models:**
  - [ ] Tạo Class `Movie` (id, title, genre, duration, release_date).
  - [ ] Tạo `MovieRepository`: Kết nối DB, xử lý query (SQL/ORM).
- [ ] **Business Logic:**
  - [ ] Tạo `MovieService`: Validate dữ liệu (ví dụ: phim phải có tên, thời lượng > 0).
- [ ] **API Endpoints (Presentation):**
  - [ ] `POST /api/movies`: Thêm phim mới.
  - [ ] `GET /api/movies`: Lấy danh sách phim.
  - [ ] `GET /api/movies/{id}`: Xem chi tiết phim.
- [ ] **Test:** Kiểm thử API bằng Postman.

## Giai đoạn 2: Thiết kế Microservices

*Mục tiêu: "Đập" khối Monolith ra thành các dịch vụ nhỏ (Lab 4).*

### Lab 4: Phân rã & Giao tiếp (Decomposition)

- [ ] **Xác định các Microservices:**
  - [ ] **Movie Service:** Quản lý phim, lịch chiếu (Tách từ module Lab 3).
  - [ ] **Booking Service:** Quản lý đặt vé, chọn ghế (Core nghiệp vụ).
  - [ ] **Notification Service:** Gửi vé điện tử, email xác nhận.
- [ ] **Thiết kế API Contract (Đặc tả API):**
  - [ ] Định nghĩa input/output JSON cho từng service.
- [ ] **Vẽ sơ đồ C4 Model (Level 1 - System Context):**
  - [ ] Thể hiện Web App, Admin, Payment Gateway và Hệ thống đặt vé.

## Giai đoạn 3: Triển khai Microservices & Gateway

*Mục tiêu: Code các service độc lập và tạo cổng giao tiếp chung (Lab 5 & Lab 6).*

### Lab 5: Xây dựng Movie Service độc lập

- [ ] **Tách Project:** Tạo folder riêng cho `movie_service`.
- [ ] **Database riêng:** Setup Database riêng cho Movie (tách khỏi DB chung cũ).
- [ ] **Code API hoàn chỉnh:**
  - [ ] Tìm kiếm phim theo tên/thể loại.
  - [ ] CRUD suất chiếu (Showtimes).

### Lab 6: API Gateway Pattern

- [ ] **Setup Gateway Project:** Tạo một Flask app mới làm Gateway (chạy port 5000).
- [ ] **Routing (Định tuyến):**
  - [ ] Request `/api/movies` -> Chuyển tiếp sang `Movie Service` (port 5001).
  - [ ] Request `/api/bookings` -> Chuyển tiếp sang `Booking Service` (port 5002).
- [ ] **Security (Giả lập):**
  - [ ] Check Header `Authorization`.
  - [ ] Chặn request nếu token không hợp lệ trước khi vào service con.

## Giai đoạn 4: Kiến trúc Hướng sự kiện (Event-Driven)

*Mục tiêu: Xử lý bất đồng bộ cho việc gửi vé/thông báo (Lab 7).*

### Lab 7: Tích hợp RabbitMQ

- [ ] **Setup RabbitMQ:** Chạy bằng Docker hoặc cài trực tiếp.
- [ ] **Booking Service (Producer):**
  - [ ] Khi đặt vé thành công -> Gửi message `OrderPlacedEvent` vào hàng đợi (Queue).
  - [ ] Message chứa: `ticket_id`, `email`, `movie_name`.
- [ ] **Notification Service (Consumer):**
  - [ ] Lắng nghe hàng đợi `ticket_events`.
  - [ ] Nhận message -> Giả lập in vé gửi email (print log ra màn hình).
  - [ ] Đảm bảo Booking Service không bị treo khi chờ gửi email.

## Giai đoạn 5: Hoàn thiện & Triển khai

*Mục tiêu: Đóng gói và đánh giá kiến trúc (Lab 8).*

### Lab 8: Deployment & Đánh giá (ATAM)

- [ ] **Deployment Diagram:**
  - [ ] Vẽ sơ đồ triển khai: Client -> Load Balancer -> API Gateway -> Services -> Databases.
  - [ ] Thể hiện rõ mỗi service có DB riêng.
- [ ] **Dockerize (Optional nhưng nên làm):**
  - [ ] Viết `Dockerfile` cho từng service.
  - [ ] Viết `docker-compose.yml` để chạy toàn bộ hệ thống bằng 1 lệnh.
- [ ] **Phân tích ATAM:**
  - [ ] Đánh giá lại ASRs (Scalability, Availability) đã nêu ở Lab 1.
  - [ ] So sánh kiến trúc Monolith (Giai đoạn 1) vs Microservices (Giai đoạn hiện tại).
