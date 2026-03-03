# V3 Challenges & Solutions

> Ghi nhận các thách thức gặp phải và giải pháp.

---

## C-001: OHLCV Volume vs API Rate Limit

**Challenge**: Fetch OHLCV daily cho 30 tickers × 365 ngày × 2 năm = ~21,900 API calls.  
**Risk**: Token overuse / API throttling từ Vietcap.

**Solution**: 
- Batch fetch: 1 request = full history per ticker (Vietcap trả multi-row per request)
- Rate limit: 0.5s delay between tickers
- Scope: Chỉ fetch 2025-01-01 đến nay (giảm ~50% volume)
- Fallback: Nếu Vietcap bị chặn → dùng VNDirect hoặc TCBS API

## C-002: Cross-Platform Chart Compatibility

**Challenge**: Chart phải chạy được cả Vite (React) và Streamlit (Python).  
**Solution**: Dùng Plotly.js — là thư viện duy nhất hoạt động natively trên cả hai:
- React: `react-plotly.js`
- Streamlit: `st.plotly_chart(fig)`
- Cùng data format (JSON traces), dễ chuyển đổi.

**Updated Solution**: Sau khi research, quyết định dùng **Pure SVG** code cứng cho Snowflake và Price Chart để tối ưu tải trang về 0 KB dependency, rất phù hợp với Dashboard React.

## C-003: Supabase RLS (Row Level Security) Permission Denied
**Challenge**: Khi script backend tự động ghi vào bảng `company_overview`, bị Supabase block do vi phạm RLS (cụ thể là HTTP 403 Forbidden).
**Solution**: Viết SQL migration scripts tạo `anon_insert` và `anon_update` policy cho roles `anon`.

## C-004: Windows Console CP1252 Encoding Issues
**Challenge**: Khi chạy lệnh in tiến trình ra Windows console (PowerShell), các emoji (✅, ❌) hoặc ký hiệu mũi tên (→) làm script Python crash do lỗi `UnicodeEncodeError: 'charmap' codec can't encode character`.
**Solution**: Thay các emoji này bằng format chữ trong CLI: `[OK]`, `[FAIL]`, `[SKIP]`, và đổi `→` thành `->` hoặc `=>`.

## C-005: Vnstock API Changes & 403 Forbidden for Bank Metrics
**Challenge**: Khi cần fetch các chỉ số chuyên sâu cho ngân hàng (NIM, NPL, Loan to Deposit) qua `vnstock.company.ratio_summary()`, source VCI trả về `403 Forbidden`, trong khi nguồn TCBS báo lỗi `AttributeError: 'Company' object has no attribute 'ratio_summary'`.
**Solution**: Đang điều tra các nguồn thay thế:
- Sử dụng bảng `financial_ratios` đã có (được tính toán bởi version 2, cột value có chứa NIM).
- Lấy qua API của Fireant (yêu cầu Authorization Bearer token).
- Quét API Note của BCTC Vietcap.
## C-006: Horizontal Overflow in CSTC Tables
**Challenge**: Bảng chỉ số tài chính quá nhiều cột và giá trị VND quá lớn làm giao diện bị vỡ, người dùng phải scroll ngang quá nhiều.
**Solution**:
- Cố định cột tiêu đề (sticky left).
- Rút gọn tiêu đề cột năm (2025 thay vì 31/12/2025).
- Tự động rút gọn số (ví dụ: 151,234.56 -> 151,235 Tỷ VND).

## C-007: Bank Balance Sheet structure mismatch
**Challenge**: Các charts SVG được thiết kế cho doanh nghiệp sản xuất (Assets = Current + Long-term). Ngân hàng không có sự phân chia này rõ ràng trong database thô.
**Solution**: Viết logic "Fallback" trong Component: Nếu không tìm thấy TS ngắn hạn, tự động map "Tổng tài sản" vào thanh bar chính và ẩn các label không phù hợp.

## C-008: Vite local environment configuration
**Challenge**: Lỗi phân quyền khi chạy script npm hoặc thiếu biến môi trường làm tốn nhiều thời gian debugging.
**Solution**:
- Sử dụng `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` khi chạy terminal trên Windows.
- Documentation: Ghi chú rõ yêu cầu file `.env` trong `v3_findings.md`.
