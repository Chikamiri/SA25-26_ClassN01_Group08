# Movie Booking System - Frontend

Dự án Frontend được xây dựng bằng React + Vite. Để hệ thống hoạt động đầy đủ, cần có các dịch vụ Backend và API Gateway chạy song song.

## 🚀 Khởi động nhanh (Sử dụng Docker - Khuyên dùng)

Đây là cách dễ nhất để chạy toàn bộ hệ thống (Frontend + Backend + Database + Gateway + Seeding dữ liệu).

1. Mở Terminal tại thư mục gốc của dự án.
2. Chạy lệnh:
   ```powershell
   docker-compose up --build
   ```
3. Truy cập vào trình duyệt: [http://localhost:5173](http://localhost:5173)

## 🛠 Khởi động thủ công (Dành cho phát triển)

Nếu bạn muốn chạy riêng Frontend để chỉnh sửa giao diện:

1. **Di chuyển vào thư mục frontend:**
   ```bash
   cd frontend
   ```
2. **Cài đặt thư viện:**
   ```bash
   npm install
   ```
3. **Chạy ứng dụng:**
   ```bash
   npm run dev
   ```
4. **Lưu ý quan trọng:** Để tính năng Đăng nhập và Đặt vé hoạt động, bạn phải đảm bảo các dịch vụ sau đang chạy:
   - **API Gateway:** Port 5000 (`src/gateway/app.py`)
   - **User Service:** Port 5004 (`src/user/app.py`)

## 🔐 Tài khoản dùng thử

Hệ thống đã được nạp sẵn dữ liệu mẫu (Seeding). Bạn có thể sử dụng các tài khoản sau:

| Quyền hạn | Username / Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `111111` |
| **User** | `user@example.com` | `password123` |

---
*Ghi chú: Nếu gặp lỗi "Fail to fetch", hãy kiểm tra xem API Gateway (Cổng 5000) đã được khởi động chưa.*
