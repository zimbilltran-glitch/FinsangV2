# Tools SOP: Writing Deterministic Scripts

## 1. Nguyên tắc viết Script tại thư mục `tools/`
- **Mỗi script là Atomic (Đơn nhiệm):** 
  - Ví dụ: `fetch_financials.py` chỉ làm nhiệm vụ kéo Báo cáo tài chính.
  - Ví dụ: `fetch_ohlc.py` chỉ làm nhiệm vụ kéo giá.
- Tách biệt rõ ràng **3 quá trình (ETL)** trong một script:
  1. `Extract`: Query API.
  2. `Transform`: Chuyển đổi định dạng Data từ WIDE (bảng ngang nhiều quý/năm ở các cột) sang LONG (chuẩn PostgreSQL). Lưu ra `.tmp/tên_file.csv`.
  3. `Load`: Khởi tạo Supabase client, đẩy dữ liệu lên Database.

## 2. Cấu trúc bảng dự kiến (Database Schema Setup on Supabase)
Dựa trên hình ảnh báo cáo tài chính mẫu (dữ liệu theo định dạng các cột n_1.revenue, n_2, với các quý ngang), chúng ta sẽ thiết kế một Cấu trúc dạng **LONG (chuẩn hóa SQL)**.
Điều này giúp Database không bị giới hạn số cột (nếu thiết kế dạng WIDE thì mỗi Quý mới phải ALTER TABLE thêm cột).

- **`financial_reports`**:
  - `id` (uuid, PK mặc định)
  - `ticker` (text) - Mã cổ phiếu (vd: 'HPG')
  - `report_type` (text) - 'KQKD' (Kết quả kinh doanh), 'CDKT', 'LCTT'
  - `period` (text) - Ghép từ `Head.YearPeriod` và `Head.TermCode` (vd: '2025-Q4')
  - `item` (text) - Tương đương trường `Name` trong JSON KBSV
  - `item_id` (text) - Tương đương trường `ReportNormID` trong JSON KBSV (vd: 5409)
  - `levels` (int4) - Tương đương trường `Levels` trong JSON KBSV (0, 1, 2)
  - `row_number` (int4) - Tương đương trường `ID` trong JSON KBSV (để sort đúng như ảnh mẫu)
  - `unit` (text) - Đơn vị (mặc định 'Tỷ VND')
  - `value` (numeric) - Giá trị tương đương `Value1`, `Value2` tương ứng với Kỳ
  - `last_updated` (timestamptz) - Thời điểm Cập nhật
  - **Constraint:** UNIQUE(`ticker`, `report_type`, `period`, `item_id`) để dễ dàng Upsert không trùng lặp.

- **`stock_ohlcv`**:
  - `ticker` (text)
  - `time` (timestamptz)
  - `open`, `high`, `low`, `close`, `volume` (numeric)
  - **Constraint:** UNIQUE(`ticker`, `time`)

## 3. Self-healing Loop
- Nếu fail tại `Extract` (HTTPS 403, 500): In ra lỗi, chờ retry.
- Nếu fail tại `Transform`: Lưu log, pass.
- Nếu fail tại `Load` (Trùng khóa hoặc Lỗi Supabase): Giữ file csv tại `.tmp/` để phân tích.
