# V6 Technical Specifications: Excel Parsing & Automation (Playwright & Pandas)

## 1. Yêu Cầu Kỹ Thuật Hệ Thống (Technical Stack)
- **Tải file Excel (Web Scraping):** `playwright` (async), `playwright-stealth` (Tránh bị Cloudflare/Anti-bot nhận diện)
- **Xử lý Dữ liệu Excel (Parser):** `pandas` (`read_excel`), sử dụng tham số `skiprows` để bỏ qua các Header rác của Vietcap. Cần hàm Regex để parse chuỗi.
- **ORM & Database:** Supabase (`supabase-py`).
- **Trigger Config:** `is_prod_run` (Bool) để phân biệt chạy Test hay Production.

## 2. Technical Design: Tầng 1 (Trigger mechanism)
Thay vì dùng cronjob tải file Excel mù quáng mỗi ngày, `sync_supabase.py` (V2) khi đồng bộ dữ liệu API từ Vietcap về Supabase, nếu Record trả về thuộc `period` (VD: `2024-Q4`) chưa từng có trong Supabase của mã đó.
Ghi đối tượng JSON:
```json
{
    "ticker": "MBB",
    "period": "2024-Q4",
    "requires_excel_audit": true,
    "status": "pending"
}
```
Vào tệp `sub-projects/V6_Excel_Extractor/v6_pending_audits.json`.

## 3. Technical Design: Tầng 2 (Crawler Bot)
Script `bot_excel_crawler.py`
```python
# 1. Khởi động Chromium Headless (Hoặc có giao diện để Debug login)
# 2. inject stealth plugin
# 3. Mở https://trading.vietcap.com.vn/quote/<TICKER>/financial-data
# 4. Do tốc độ tải vừa phải, không cần login tài khoản Vietcap.
# 5. Phân tích Network Requests để tìm API trả về dữ liệu file Excel.
# 6. Locate nút "Xuất BCTC" nếu cần. Wait for event `download` hoặc gọi thẳng API export.
# 7. Lưu về `data/excel_imports/MBB_2024-Q4.xlsx`
# 8. Sleep rand(5, 15) seconds.
```

## 4. Technical Design: Tầng 3 (Pandas Ground Truth Validator)
Script `excel_data_auditor.py`
Khó khăn lớn nhất là File Excel của Vietcap không có chung Schema chuẩn mà tuỳ vào 3 nhóm ngành (Bank, Securities, Normal).
Tuy nhiên, Cột đầu tiên luôn là Tên Chỉ Tiêu (Tiếng Việt). Cột 2, 3, 4, 5... là dữ liệu các Quý tương ứng `2024-Q4, 2024-Q3, ...`.
- Sử dụng Module `golden_schema.json` (đang có ở V2).
- Cấu trúc file Excel Vietcap:
  - Sheet `CDKT`, `KQKD`, `LCTT`
  - So khớp `vn_name` từ Excel với `vn_name` trong `golden_schema.json` để lấy ra `item_id`.
  - **Lưu ý Thuyết minh Ngân hàng:** Ở Tầng 3, thay vì đọc API Note (bị 403), script quét toàn bộ Sheet Thuyết minh (nếu có) hoặc tìm kiếm theo regex string: `r"Tiền gửi (.*)không kỳ hạn(.*)"`.
- Map toàn bộ Cột Quý (Quarters) -> `period`
- Đẩy ngược Object Dữ Liệu vào Supabase Table `balance_sheet`, `income_statement`, `cash_flow` và `financial_ratios`.
- Ưu tiên: `INSERT INTO ... ON CONFLICT (stock_name, period, item_id) DO UPDATE SET value = EXCLUDED.value`.

## 5. Security Checklist (CTO)
- [x] RLS Policy tại Supabase đã bật chưa? (Chỉ Server có Service Key mới được Update Value của Excel) -> Đã xử lý ở Phase 5.
- [x] Không Hardcode Auth Token Vietcap vào source code.
- [x] Giãn cách Request để tránh rớt mạng (Throttle).
- [x] Thư mục `.tmp` hoặc `excel_imports` phải được thêm vào `.gitignore` (Không commit đẩy BCTC rác lên Github).
