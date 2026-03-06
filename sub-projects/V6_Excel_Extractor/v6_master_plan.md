# V6 Master Plan: Automated Excel Extraction Pipeline

## MỤC TIÊU (OBJECTIVE)
Giải quyết dứt điểm Technical Debt của dự án Finsang V2: Dữ liệu Thuyết minh BCTC (CASA, NPL của Ngân hàng) bị chặn (Lỗi 403 Forbidden) qua API công khai của Vietcap. 
**Hướng giải quyết:** Tự động điều khiển trình duyệt bằng Playwright giả lập người dùng tải file Báo cáo Tài chính Excel từ Vietcap, bóc tách dữ liệu và biến Excel thành nguồn Ground Truth.

## YÊU CẦU CỐT LÕI (CORE REQUIREMENTS)
1. **Thiết kế Kiến trúc (Architecture):** Tách bạch luồng Kích hoạt (Trigger), luồng Rút trích (Extraction Bot) và luồng Kiểm định (Validation & Upsert).
2. **Tần suất chạy:** 1 lần / 1 tháng (vì Báo cáo Tài chính quý chỉ có mới nhất 1 lần/quý, khác với giá OHLC).
3. **Phạm vi triển khai:** Ban đầu **áp dụng cho nhóm VN30**, sau đó sẽ Scale up cho toàn bộ thị trường.
4. **Phạm vi Dữ liệu (Ground Truth):** Validate và Upsert cho cả 3 nhóm ngành (Phi Tài Chính, Ngân Hàng, Chứng Khoán), không chỉ riêng Ngân hàng. Dữ liệu từ file Excel luôn luôn là **Nguồn Chân Lý** (Ground Truth), ưu tiên ghi đè nếu API hiện hành bị sai.

## LUỒNG THỰC THI (WORKFLOW)

**Tầng 1: Trigger Layer (Dò tìm BCTC mới)**
- Tích hợp vào Pipeline V2. Thay vì quét Excel mù quáng mỗi ngày, `sync_supabase.py` khi tải dữ liệu API sẽ nhận diện được Quý mới (VD: Bỗng nhiên xuất hiện 2024-Q4).
- Ghi vào một file meta `v6_pending_audits.json` danh sách các mã VN30 có BCTC mới cần tải Excel.

**Tầng 2: Extraction Layer (Bot tải file - Playwright)**
- Worker `bot_excel_crawler.py` đọc danh sách từ Tầng 1.
- Mở Headless Browser (Chromium), tự động điều hướng đến trang tài chính của mã tương ứng. Do tốc độ tải được kiểm soát ở mức vừa phải (Moderate), việc tải file Excel hiện tại **không cần tài khoản Vietcap**.
- Tải file Excel vào thư mục `data/excel_imports/<TICKER>_<PERIOD>.xlsx`.
- Random sleep (5-15s) giữa các thao tác để chống Cloudflare / Anti-bot.

**Tầng 3: Validation & Processing Layer (Pandas Parser)**
- Worker `excel_data_auditor.py` đọc file `.xlsx`.
- **Thuyết minh:** Tìm đích danh dòng "Tiền gửi không kỳ hạn" (CASA), "Nợ nhóm 3,4,5" (NPL). Tính tỷ lệ và đẩy vào Supabase (`financial_ratios`).
- **CDKT, KQKD, LCTT:** Merge toàn bộ file Excel với `golden_schema.json` để quy đổi ra `item_id`. So sánh 1-1 với dữ liệu API có sẵn trong database.
- Ghi đè (Overwrite) Supabase nếu có sai lệch. Đánh dấu hoàn tất trong `v6_pending_audits.json` bằng cờ `status: "completed"`.

---
**Ghi chú cho Agent:**
Đây là bản Master Plan. Chi tiết Kỹ Thuật (Technical Specs) vui lòng đọc file `v6_technical_specs.md`. Các công việc cần làm ở file `v6_task_tracker.md`.
