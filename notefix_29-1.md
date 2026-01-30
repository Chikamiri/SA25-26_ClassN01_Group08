# Lỗi và Vấn đề tồn đọng - 29-01-2026

## 1. Lỗi Unicode trong Payment Service (Ưu tiên: Cao)
- **Vị trí:** `src/payment/app.py` tại dòng 79.
- **Vấn đề:** Emoji 💰 gây crash trên console Windows (`UnicodeEncodeError`).
- **Tác động:** Làm bộ test API bị lỗi 500 ở bước thanh toán.
- **Giải pháp:** Xóa emoji 💰 ở dòng 79 trong `src/payment/app.py`.

## 2. Bảo mật API Gateway (Ưu tiên: Trung bình)
- **Vấn đề:** Kiểm tra API Key (`peko-key`) đang bị comment lại trong `src/gateway/app.py`.
- **Cần làm:** Mở lại kiểm tra API Key và cấu hình Frontend gửi kèm Key này trong header.
- **CORS:** Đang xử lý thủ công bằng `@app.after_request`. Cần kiểm tra tính tương thích khi deploy lên production.

## 3. Quản lý Cơ sở dữ liệu (Ưu tiên: Trung bình)
- **Vấn đề:** Script `seed_db.py` xóa file `.db` để cập nhật schema. Điều này làm mất dữ liệu cũ mỗi khi chạy lại seeder.
- **Cần làm:** Sử dụng script migration chuyên nghiệp hoặc thêm lệnh `ALTER TABLE` vào `init_db`.

## 4. Kiểm tra mã lỗi Frontend (Ưu tiên: Thấp)
- **Vấn đề:** Lỗi "Fail to fetch" quá chung chung khiến người dùng khó chẩn đoán service nào đang sập.
- **Cần làm:** Cập nhật `apiClient.js` để bắt lỗi chi tiết hơn (ví dụ: "Gateway is down" vs "Auth Service error").

---
## Nhật ký thay đổi hôm nay (29-01-2026)
- ✅ **Băm mật khẩu:** Đã chuyển từ plaintext sang `werkzeug.security`.
- ✅ **Refactor Admin:** Gỡ bỏ thông tin admin cứng, quản lý bằng cột `role` trong DB.
- ✅ **Docker Seeding:** Tối ưu `docker-compose.yml` để tự động tạo dữ liệu mẫu.

--------------------------------------------------------------------------------
## Nhật ký thay đổi hôm nay (31-01-2026)
- ✅ **Sửa lỗi Unicode (Payment):** Đã xóa emoji 💰 gây crash trên Windows.
- ✅ **Cấu hình Docker Host:** Đã chuyển `host` từ `127.0.0.1` sang `0.0.0.0` cho tất cả các service để cho phép truy cập từ Host machine.
- ✅ **Public API Access:** Mở quyền truy cập công khai cho danh sách phim và suất chiếu trên Gateway mà không yêu cầu token, sửa lỗi "Fail to fetch" ở trang chủ.
- ✅ **Bảo mật API Gateway:** Đã mở lại kiểm tra API Key (`peko-key`) và cập nhật Frontend.
- ✅ **Database Migration:** Đã cập nhật `seed_db.py` và `src/user/app.py` để sử dụng `ALTER TABLE` thay vì xóa DB, bảo toàn dữ liệu cũ.
- ✅ **Frontend Error Handling:** Cập nhật `apiClient.js` để báo lỗi rõ ràng hơn khi Gateway không kết nối được ("Gateway is down").