# Finsang V2 - Hướng dẫn Cập nhật Dữ liệu Hàng Quý

Document này hướng dẫn chi tiết quy trình cập nhật dữ liệu tài chính (BCTC, CSTC, dữ liệu công ty) cho 30 mã VN30 khi có báo cáo tài chính quý mới.

> **Yêu cầu môi trường:** Python 3.12+, biến môi trường đã được set trong `frontend/.env` (`VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, và lý tưởng là `SUPABASE_SERVICE_ROLE_KEY` để thực hiện cập nhật ghi/xóa bảng).

---

## Bước 1: Crawl & Tự động phát hiện Quý Mới
Thực hiện chạy tệp cập nhật thông tin tổng quát và kiểm tra quý mới nhất hiện có.
```bash
cd d:\Project_partial\Finsang
$env:PYTHONIOENCODING='utf-8'
python sub-projects/Version_2/vn30_enrichment.py
```
> **Tác dụng:**
> - Cập nhật thông tin tổng quát (Company Overview) cho 30 mã VN30 (vốn hóa, giá, EPS, PE, ...).
> - Script có khả năng tự động gọi resync pipeline nếu phát hiện thông tin lỗi thời.

## Bước 2: Chạy Full Resync (Đồng bộ Pipeline V5.5 -> Supabase)
Nếu bạn chỉ muốn fetch và đẩy dữ liệu tài chính BCTC mới nhất lên Supabase:
```bash
python sub-projects/Version_2/v5_full_resync.py
```
> **Tác dụng:**
> - Script đã được tối ưu bằng ThreadPoolExecutor, chạy song song 8 mã cùng lúc.
> - Tổng thời gian chạy cho 30 mã VN30 chỉ dưới 5 phút.
> - Fetch 3 sheet: CDKT, KQKD, LCTT về dạng Parquet, normalize, và stream trực tiếp lên Supabase (`balance_sheet`, `income_statement`, `cash_flow`).
> - Workflow an toàn, xóa gọn dữ liệu cũ theo mã và insert dữ liệu mới.

*Lưu ý: Bạn có thể truyền danh sách `--tickers` để chạy lẻ vài mã (VD: `--tickers MBB,VCB,SSI`).*

## Bước 3: Tính toán Chỉ số Tài chính (CSTC)
Dữ liệu BCTC đã có trên Supabase. Bây giờ chúng ta tính toán các Hệ số Tài chính (Financial Ratios).
```bash
python sub-projects/V5_improdata/run_metrics_batch.py
```
> **Tác dụng:**
> - Batch script chạy theo từng mã VN30.
> - Kéo CDKT, KQKD, LCTT từ Supabase (bước 2) xuống local RAM.
> - Gọi Engine `metrics.py` tính toán ra CSTC chuẩn (dùng `lite_schema.json`).
> - Có hỗ trợ riêng cho Sector Ngân hàng (LDR, CIR, NIM, YOEA) và Chứng khoán (Margin/Equity, CER, Brokerage Share).
> - Xóa CSTC cũ trên database (`financial_ratios`) và push CSTC mới lên.

## Bước 4: Verification & Log (Kiểm tra và Ghi nhận)
Sau khi kết thúc tiến trình 3 bước trên, bạn cần thực hiện Smoke Test.

1. Khởi động Web frontend cục bộ:
   ```bash
   cd frontend
   npm run dev
   ```
2. Mở trình duyệt tại `http://localhost:5173/overview`.
3. Kiểm tra ngẫu nhiên 3 ticker đại diện cho 3 sector:
   - **VHC / FPT (Sản xuất / Công nghệ)**: Kiểm tra các chỉ số P/E, ROE, Current Ratio.
   - **MBB (Ngân hàng)**: Kiểm tra tab BCTC Ngân hàng, các tỉ lệ CIR, LDR, Tỉ lệ Vốn CSH/Tổng TS.
   - **SSI (Chứng khoán)**: Kiểm tra Margin/Vốn CSH.
4. Mở file `Finsang_Master_Logs.md` trên root folder, ghi nhận ngày tháng cập nhật quý:
   > "Đã cập nhật dữ liệu thành công cho QX/202X. Data Pipeline verify 100%. No errs."

---
*Finsang V2 - Built with 💙 by Antigravity*
