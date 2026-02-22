# System SOP: Data Crawling Architecture

## 1. Mục đích
Hệ thống này sinh ra để Crawl (tự động lấy) hai loại dữ liệu chính cho các mã chứng khoán (VN30 hoặc tuỳ chọn):
- **Dữ liệu OHLCV (Giá cả & Khối lượng):** Crawl nhỏ giọt theo giờ (Hourly) để không làm quá tải server nguồn.
- **Báo cáo tài chính (CĐKT, KQKD, LCTT):** Crawl mỗi 24 giờ.

## 2. Các tầng dữ liệu (Data First)
Tất cả dữ liệu cuối cùng phải được đẩy lên **Supabase (PostgreSQL)**.
- Khi một script Python (Layer 3) chạy, nó sẽ kéo data thô từ API -> Lưu tạm dưới dạng file `.csv` ở `.tmp/` -> Thực hiện Upsert (Insert/Update) vào Supabase -> Xóa file tạm.

## 3. Quyết định nguồn dữ liệu (Source of Truth)
Nguồn dữ liệu **CHÍNH** sẽ là **Trực tiếp từ KBSV API (bằng thư viện `requests`)** vì nó ổn định và không phụ thuộc.
- Tham chiếu: `Walkthrough` (Reverse-engineered KBS API).
- **Phụ / Dự phòng (Fallback):** Nếu KBS API thay đổi Cấu trúc (Endpoint / Header / Auth), fallback sang `vnstock` kết hợp với VIP API KEY.

## 4. Edge Cases & Fallback Behavior
- **Giới hạn Rate-limit / Ban IP**: Giảm tần suất chạy (sleep giữa các request).
- **Trường hợp lỗi kết nối Database**: Dữ liệu csv vẫn nằm trong `.tmp/` - chờ lần sau push tiếp hoặc agent chạy lại self-healing.
- **Dữ liệu JSON KBS không có trường mong muốn**: Pass (không lỗi ứng dụng) và log lại ghi chú vào `progress.md`.
