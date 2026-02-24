---
description: Pipeline PDF_TRANS - Extract, Normalize & Audit Financial Reports from HSX/HNX
---

# Workflow: PDF_TRANS (Financial Document Extraction to Database)

Dự án con `PDF_TRANS` vận hành song song với `Finsang`, thực hiện thu thập, trích xuất và chuẩn hoá dữ liệu báo cáo tài chính từ file PDF gốc của sàn HSX, HNX và chuyển thẳng vào Database (thông qua staging area).

## 1. Khởi tạo & Thu thập Liên kết (Discovery & Scraping)
// turbo
Chạy script scraper để thu thập link PDF báo cáo tài chính.
```bash
python scripts/run_scraper.py --source hsx,hnx --keywords "Báo cáo tài chính hợp nhất,BCTC HN" --output .tmp/link_list.json
```
- **Xử lý ngoại lệ**: Nếu HSX/HNX không phản hồi hoặc bị thay đổi DOM, script sẽ tự động chuyển sang fallback source (ví dụ: `finance.vietstock.vn`).

## 2. Trích xuất PDF sang Markdown (PDF Ripping)
// turbo
Sử dụng công cụ `pdf-to-markdown-extractor` để xử lý hàng loạt link PDF đã lấy được, ưu tiên nhận diện và cắt bảng.
```bash
python scripts/run_extractor.py --input .tmp/link_list.json --output-dir .tmp/raw_data/
```
- **Trọng tâm**: Tìm kiếm fuzzy (mờ) các keyword như "Kết quả kinh doanh", "Lưu chuyển tiền tệ", "Bảng cân đối kế toán" do PDF các công ty kiểm toán khác nhau có định dạng khác nhau. Có fallback sang cơ chế OCR nếu file PDF là dạng scan.

## 3. Chuẩn hoá & Đối chiếu Dữ liệu (Cleaning & Normalization)
// turbo
Gọi kĩ năng `financial-data-normalizer` để chuẩn bị dữ liệu theo Finsang Universal Schema.
```bash
python scripts/run_normalizer.py --input-dir .tmp/raw_data/ --output .tmp/normalized_data.json
```
- **Cross-Reference**: Đối chiếu ngẫu nhiên với dữ liệu từ CafeF/Vietstock. Gắn cờ (flag: `checksum_warning`) nếu chênh lệch (discrepancy) > 1%.

## 4. Kiểm toán Dữ liệu (CFO Analyst Audit)
// turbo
Hệ thống CFO Analyst kiểm tra tính đúng đắn của phương trình kế toán. Đẩy dữ liệu đạt chuẩn vào CSDL, dữ liệu lỗi vào bảng Staging.
```bash
python scripts/run_audit_and_ingest.py --input .tmp/normalized_data.json
```
- **Quy tắc Kiểm toán**: Xác thực `Doanh thu - Giá vốn = Lợi nhuận gộp`, Tài sản = Nguồn vốn, v.v.
- **Ingestion**: Dữ liệu pass tất cả rules được Insert/Update vào Database chính, dữ liệu fail bị đẩy vào bảng staging chờ admin duyệt.

## 5. Báo cáo & Xóa Dữ liệu tạm (Clean-up & Reporting)
// turbo
Dọn dẹp `.tmp` và sinh báo cáo kết quả tiến trình BLAST.
```bash
python scripts/generate_report.py --clear-tmp
```
