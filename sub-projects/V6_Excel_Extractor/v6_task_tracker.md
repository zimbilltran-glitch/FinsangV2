# V6 Master Task Tracker: Automated Excel Extraction

> Phân bổ công việc (Action Items) cho Hệ thống Tải & Phân tích Excel BCTC.

## Phase 6.1: Khởi tạo Prototype & Môi trường (Environment Setup)
- [ ] Thiết lập thư mục `data/excel_imports/` và thêm vào `.gitignore`.
- [ ] Khởi tạo kịch bản `bot_excel_crawler.py` sử dụng `Playwright` và `playwright-stealth`.
- [ ] **Test Run:** Bot vào được Vietcap và tải được file `MBB_BCTC.xlsx` về máy (không cần login do tốc độ tải vừa phải).

## Phase 6.2: Core Parser & NPL/CASA Engine (Tầng 3)
- [ ] Viết script `excel_data_auditor.py` sử dụng thư viện `pandas` (`read_excel`).
- [ ] Ánh xạ thành công cấu trúc Bảng Cân Đối Kế Toán của MBB từ Excel sang `golden_schema.json` format.
- [ ] **NPL & CASA Extractor:** Bot đọc được sheet Thuyết Minh (NOTE) hoặc tìm chính xác dòng "Tiền gửi không kỳ hạn" và "Nợ nhóm 3,4,5".
- [ ] Push tỷ lệ CASA, NPL tính được lên DB Supabase bảng `financial_ratios`.

## Phase 6.3: Ground Truth Validator (Kiểm định API vs Excel)
- [ ] Viết chức năng Compare giữa Dữ liệu đã có (từ API) và Dữ liệu mới parse (từ Excel).
- [ ] Nếu có khác biệt, bật chế độ **Overwrite** ghi đè lên Supabase DB để vá lỗi API. Đảm bảo RLS cho phép Update.

## Phase 6.4: Tích hợp Trigger & Scale cho VN30 (Tầng 1)
- [ ] Sửa đổi `V2_Data_Pipeline/sync_supabase.py`: Phát hiện Quý mới -> Bật cờ `requires_excel_audit = True` vào `v6_pending_audits.json`.
- [ ] Đặt Master Controller để chạy Bot 1 lần/tháng cho toàn bộ 30 mã VN30 với delay lớn.
- [ ] Scale hệ thống đọc Excel cho 2 nhóm ngành còn lại (Chứng Khoán & Phi Tài Chính).
- [ ] Review toàn bộ & Đóng Phase 6.
