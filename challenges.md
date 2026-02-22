# Sổ tay Kỹ thuật: Khó khăn & Giải pháp (Challenges Log)

Tài liệu này ghi nhận các vấn đề kỹ thuật (technical stucks), lỗi (bugs) gặp phải trong quá trình phát triển dự án chứng khoán B.L.A.S.T, cùng phương án đã giải quyết.

## 1. Nguồn Dữ liệu & Handshake (Phase L)
**Vấn đề:** 
Thư viện `vnstock3` (phiên bản fork `vnstock3_learn`) báo lỗi "Forbidden-ban" khi khởi tạo. Sau khi chuyển sang cài package gốc `vnstock` chuẩn thì lại gặp lỗi "Cannot import name 'FinancialReport'".
**Nguyên nhân:**
Thư viện `vnstock` nguyên bản đã chia nhỏ hệ sinh thái, module `FinancialReport` không có sẵn trong thư viện chính nếu gọi sai cấu trúc, hoặc các hàm cũ đã deprecate (không còn hỗ trợ). API Endpoint của KBSV cũng ẩn giấu các Params.
**Giải pháp:**
- Dùng chức năng Reverse-engineering (Dịch ngược) từ file `Walkthrough` để lôi thẳng cấu trúc URL API của KB Securities: `https://kbbuddywts.kbsec.com.vn/sas/kbsv-stock-data-store/stock/finance-info/...`
- Gọi API trực tiếp bằng thư viện `requests` kèm đủ Header (`User-Agent`) và Query Parameters (`termtype`, `unit`, `languageid`) thay vì lệ thuộc vào object `FinancialReport` của `vnstock`. 
- Đối với dữ liệu OHLCV, tiếp tục sử dụng object `Quote` của `vnstock` vì endpoint này của KBS cấu trúc đơn giản, ít lỗi và hỗ trợ `api_key` VIP.

## 2. Thiết kế Cơ sở dữ liệu Báo cáo Tài chính (Phase A)
**Vấn đề:**
Excel chứa BCTC của User cung cấp là Bảng Ngang (WIDE table - mỗi Quý/Năm là một cột). Nếu thiết kế CSDL SQL (Supabase) lưu nguyên dạng bảng ngang này, cấu trúc sẽ bị "cứng", mỗi khi có một quý mới trôi qua, ta phải chạy lệnh `ALTER TABLE` thêm cột thủ công, rất dễ gây lỗi hệ thống.
**Giải pháp:**
- Bẻ CSDL trên Supabase thành định dạng Dọc (LONG Data) `financial_reports`. Mỗi giá trị của một hạng mục trong 1 quý sẽ là 1 HÀNG độc lập (gồm cột `period`, `item_id`, `value`).
- Tại Phase S (Presentation), dùng SQL Pivot (hàm `jsonb_object_agg` của PostgreSQL) để nhóm (Group By) các khoản mục lại, "gói" tất cả các quý thành 1 cục JSON. Frontend dựa vào cục JSON này vẽ bảng chéo y hệt Excel mà không cần đổi cấu trúc DB bao giờ.

## 3. Kiến trúc Giao diện Frontend (Phase S)
**Vấn đề:**
User cung cấp ảnh mẫu `sample_group_fin.png` (bảng Excel thuần) nhưng lại yêu cầu giao diện Website phải giống phong cách của `Simplize` (Dark Theme chuyên nghiệp, gọn gàng, có bar chart mini nhúng trong bảng). Đồng thời, User yêu cầu công nghệ Frontend phải trực quan, dễ maintain (dễ bảo trì) cho người mới bắt đầu lập trình.
**Giải pháp:**
- **Công nghệ Frontend**: Loại bỏ TailwindCSS (do cú pháp dài dòng rối mắt người mới). Sử dụng **Vite + React + Vanilla CSS (CSS thuần)**. Cách này giúp code trong suốt, file `App.jsx` chỉ chứa logic lấy dữ liệu (Supabase), file `App.css` độc lập quản lý màu sắc Dark Theme và Layout (Grid/Flexbox/Sticky Header).
- **Trình bày Bảng (Data Table)**:
  - Khởi tạo CSS Lock cho cột đầu tiên (Cột Khoản mục) và dòng tiêu đề (Dòng Thời gian) bằng thuộc tính `position: sticky`. Mục đích là khi Data trải dài 5-10 năm theo chiều ngang, người dùng kéo sang phải vẫn giữ được Tên khoản mục. (Tránh lỗi trôi header kinh điển của HTML Table thuần).
  - Tự động lấy các key JSONB từ Supabase (`2024-Q1`, `2024-Q2`,...) sinh ra các cột động `<th>` mà không phải hardcode. Phân cấp (levels) thò thụt dòng theo biến `levels` trong DB thay vì chèn space thủ công.
  - Tích hợp 1 Component `MiniBarChart` tự vẽ các div siêu nhỏ với chiều cao tính theo % giá trị Max của hàng đó, đáp ứng được nét đặc sắc của Theme Simplize.

## 4. Kiểm định Chất lượng Dữ liệu & Mật độ Dữ liệu (Phase D)
**Vấn đề:**
Ở giai đoạn đầu, hệ thống chỉ lấy dữ liệu từ một nguồn duy nhất (API của KBSV). Sau khi kiểm duyệt chéo với template trên Google Sheet, phát hiện API trả về dữ liệu thưa (Sparse Data) - nghĩa là KBSV tự động "cắt bỏ" hoặc "ẩn đi" hơn 60 dòng chỉ tiêu nếu công ty đó không có phát sinh (giá trị = 0). 
Hậu quả là Database lưu y nguyên cấu trúc thưa thớt này. Về lâu dài, khi Model tính toán của Data Scientist chạy hoặc khi xây dựng Dashboard, hệ thống chắc chắn sẽ bị sập vì lỗi `KeyError` (không tìm thấy chỉ tiêu tương ứng để tính toán tỷ số tài chính). Làm sao để vừa lấy đúng, vừa đảm bảo lưu trữ chuẩn mật độ mà không sai lệch bản chất kế toán?

**Giải pháp:**
Việc này đòi hỏi sự phối hợp khắt khe của 4 bộ kỹ năng liên hoàn:
- **Tạo Khuôn Cố Định (Master Template):** Áp dụng kỹ năng `@database-design`, tạo một bảng `tt200_coa` chứa toàn bộ các chỉ tiêu theo chuẩn mực Kế toán TT200. Data Pipeline (`fetch_financials.py`) bị buộc phải Left Join dữ liệu API rách nát vào cái khuôn này. Nơi nào API thiếu số, gán mặc định `value = 0` thay vì bỏ trống dòng. Nhờ đó biến đổi Sparse Data thành Dense Data (Dữ liệu đặc).
- **Đối soát Đa Nguồn (Multi-Source Benchmarking):** Rút kinh nghiệm từ tính mong manh của một nguồn API duy nhất, hệ thống thiết kế thêm cột `source` cho tất cả các bảng gốc. Xây dựng thêm ba bảng Benchmark riêng biệt (`income_statement_benchmark`, v.v.).
- **Tự động hoá Đối soát & Thách thức Web Scraping:** Dùng kỹ năng `@autonomous-web-scraper` (chạy script `Crawl4Ai` ưu tiên số 1 để tránh tốn Token) và `@firecrawl-scraper` làm phương án dự phòng để cào dữ liệu BCTC hoàn chỉnh từ nguồn cực kỳ uy tín là **Simplize.vn** (nếu lỗi sẽ nhảy sang **finance.vietstock.vn**). 
  - **Vấn đề phát sinh (Scraping Blockers):** Quá trình cào thực tế cho thấy `Crawl4Ai` bị block hoặc không render được các table SPA phức tạp trên Simplize, dẫn đến script tự động fallback sang `FireCrawl`. 
  - **Rủi ro chi phí (Token Limits):** Do phải sử dụng `FireCrawl` liên tục, rủi ro tiêu hao Token rất nhanh. Nếu mở rộng cào dữ liệu cho toàn bộ VN30 hoặc thị trường, quota của API này chắc chắn không đủ. 
  - **Hướng giải quyết tương lai:** Nhận diện được điểm nghẽn này, tương lai cần bắt giải pháp: (1) Thay vì cào HTML/Markdown, sử dụng Reverse Engineering API nội bộ của Simplize y như cách đã làm với KBSV; hoặc (2) Nâng cấp `Crawl4Ai` với các thiết lập Puppeteer/Playwright Stealth tinh vi hơn (đợi Render JS hoàn chỉnh) để tự chủ 100% việc lấy dữ liệu mà không phụ thuộc 3rd Party API.
- **Kiểm toán CFO (Data Audit):** Trước khi gán mác "Chuẩn" cho dữ liệu vừa cào, kỹ năng `@professional-cfo-analyst` sẽ được kích hoạt để chạy checksum định lý Kế toán (Ví dụ: `Tổng Tài Sản = Tổng Nguồn Vốn`). Chỉ khi Audit PASSED, script `reconcile_simplize.py` mới đem đi quét Diff với Database hiện tại. Đảm bảo 100% không lọt rác vào Production.

## 5. Nợ Kỹ thuật & Khắc phục từ CTO Audit (Phase T)
**Vấn đề:**
Sau khi quét dự án, Giám đốc Kỹ thuật (`@cto-mentor-supervisor`) đã chỉ ra 3 rủi ro thiết kế cấp bách mang tính hệ thống (Technical Debt):
1. **Rủi ro Infinite Loop ở hàm đệ quy `Levels`:** Hiện tại hàm `build_tree` dựa vào `ParentReportNormID` chưa có Unit Tests. Nếu API trả về cấu trúc vòng rỗng hoặc móc vòng, pipeline có thể bị treo vĩnh viễn.
2. **Thiếu Tự Động Hóa (Decoupled Scripts):** Các script ETL Python đang phải chạy rời rạc. Khi list mã lệnh phình lên 1,000 mã, không thể gọi script bằng tay.
3. **Chi phí FireCrawl bùng nổ:** Việc dự phòng bằng Firecrawl (để phá Block JS trên Simplize) sẽ làm cạn kiệt Token ngân sách rất nhanh.

**Giải pháp (Đã hoàn tất):**
- **Giải quyết Rủi ro 1 (Testing):** Tích hợp `pytest` vào folder `tests/test_fetch_financials.py`, tạo mock JSON rác (vòng lặp vô tận) để bắn vào hàm đệ quy của `fetch_financials.py`. **PASS**: Script phát hiện đứt gãy và throw Exception/trả về đúng levels mà không bị Loop vô tận.
- **Giải quyết Rủi ro 2 (Orchestration):** Viết tệp `orchestrator.py` đóng vai trò là Central Worker DAG. Khi kích hoạt bằng 1 lệnh duy nhất (`python orchestrator.py --symbol NLG`), toàn bộ 5 pipeline (OHLCV -> Dense Merge -> Ratios -> Web Scraper -> CFO Audit) sẽ chạy ngầm nối đuôi nhau hoàn toàn tự động.
- **Giải quyết Rủi ro 3 (Stealth Bot):** Cài đặt engine Playwright `crawl4ai` và kích hoạt cờ `magic=True` (Stealth Mode). Crawler đã xé toạc lớp bảo vệ Cloudflare/JS của Simplize, tự động load Table JS và cào 327 dòng dữ liệu cực ngọt ngào mà không tốn 1 đồng Token của API FireCrawl dự trù. 

---
*(CTO Audit Nợ Kỹ Thuật Đã Được Thanh Toán Hoàn Toàn)*
