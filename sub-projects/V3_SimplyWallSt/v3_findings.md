# V3 Findings Log

> Ghi nhận các phát hiện kỹ thuật trong quá trình triển khai V3.

---

## F-V3-001: Supabase Data Coverage (2026-03-01)

| Table | Rows | Tickers | Status |
|---|---|---|---|
| `balance_sheet` | 119,367 | 31 (VN30+VHC) | ✅ Full |
| `income_statement` | 32,992 | 31 | ✅ Full |
| `cash_flow` | 60,705 | 31 | ✅ Full |
| `financial_ratios` | 39,690 | 31 | ✅ Full |
| `companies` | 34 | 34 | ✅ Full |
| `stock_ohlcv` | 9,455 | 31 (VN30+VHC) | ✅ Full |
| `company_overview` | 31 | 31 (VN30+VHC) | ✅ Full |

## F-V3-002: Existing Frontend Tab Structure

Hiện tại App.jsx có 4 tabs: CDKT, KQKD, LCTT, CSTC.  
V3 sẽ thêm tab "360 Overview" — KHÔNG thay thế tabs hiện tại.

## F-V3-003: Chart Library Choice

Quyết định cuối cùng (Updated 2026-03-01): **Pure SVG** code cứng trực tiếp trong Component.
Lý do:
1. Chart kiểu SWS Snowflake là dạng Radar 5 trục tĩnh, thiết kế rất đơn giản bằng toán học SVG `<polygon>`.
2. Bỏ hoàn toàn dependencies của Plotly (~200KB-1MB), giúp tab Overview load tức thì (0 ms trễ render).
3. Area Chart cho OHLCV cũng dùng `<path>` SVG nội tuyến cực nhẹ, đạt tốc độ render tối đa.

## F-V3-004: Bank-specific Metrics Data Sources 
- `vnstock` hiện không ổn định cho hàm `ratio_summary()` (VCI lỗi 403, TCBS module lỗi).
- Báo cáo tài chính Note section của Vietcap API trả về JSON cấu trúc lộn xộn, khó map cứng các field Nợ Xấu.
- API Fireant trả dữ liệu ổn cho `/financial-indicators` nhưng cần giải quyết Bearer Token lấy từ authentication headers.
- Bảng `financial_ratios` (CFO_CALC_V2) trong database Supabase đã chứa sẵn:
  - "Biên lãi ròng (NIM) Ước tính" (`item_id: bank_4_6`)
  - "Tiền gửi của khách hàng" (`item_id: bank_2_1`)
  - "Cho vay khách hàng" (`item_id: bank_1_2`)
- 💡 **Giải pháp**: Ưu tiên tận dụng data in-house từ `financial_ratios` để tính NIM và Loan/Deposit, kết hợp fetch thêm API Fireant cho NPL (Tỷ lệ nợ xấu) nếu cần.
## F-V3-005: CSTC Tab Layout Optimization (2026-03-03)
Phát hiện: Bảng chỉ số tài chính cho các mã Ngân hàng/Chứng khoán có giá trị hàng tỷ VND quá dài gây tràn container.
Giải pháp:
1. CSS: Dùng `table-layout: fixed` và `width: 80px` cho các cột giá trị.
2. Sticky: Cố định cột "Chỉ tiêu" bên trái bằng `position: sticky`.
3. Format: Hàm `formatNumber` thích ứng: >= 10K tỷ -> 0 decimal; chia triệu cho "Cổ phiếu".

## F-V3-006: Bank Balance Sheet Mapping (2026-03-03)
Phát hiện: Dữ liệu BS của mã Ngân hàng không dùng `cdkt_tai_san_*` mà dùng `cdkt_bank_*`.
Mapping cho Charts:
- Total Assets: `cdkt_bank_tong_tai_san`
- Total Debt: `cdkt_bank_tong_no_phai_tra`
- Equity: `cdkt_bank_von_chu_so_huu`
- Total Liab + Eq: `cdkt_bank_no_phai_tra_va_von_chu_so_huu`

## F-V3-007: Local Development Requirements
Phát hiện: Khi chạy Vite local, web bị trắng trang nếu thiếu `.env` chứa `VITE_SUPABASE_URL` và `VITE_SUPABASE_ANON_KEY`.
Lưu ý: Luôn kiểm tra file `.env` tồn tại trong thư mục `frontend/` trước khi dev.
