# Business Requirement Document (BRD): 8-Skill Architecture Orchestration

**Author:** `@product-manager-toolkit`
**Version:** 1.0 (Draft)
**Status:** In Review

---

## 1. Mục tiêu Cốt lõi (Product Vision)
Xây dựng nền tảng Dữ liệu và Phân tích chứng khoán Việt Nam (B.L.A.S.T Framework) dựa trên cấu trúc siêu tự động hóa. Đảm bảo dữ liệu chính xác tuyệt đối, luồng xử lý mượt mà, giao diện chuyên nghiệp và bảo mật rủi ro bằng cách sử dụng Cơ chế Phân quyền 8 Kỹ năng (8-Skill Orchestration).

## 2. Mô hình Tổ chức & Phân quyền Kỹ năng (Skill Roles & Limits)

`@product-manager-toolkit` đóng vai trò là Tổng Đạo diễn (Orchestrator). MỌI kỹ năng khác chỉ được kích hoạt hoặc xét duyệt sau khi PM Toolkit đã định nghĩa Scope (RICE Prioritization) / PRD.

| ID | Skill Name | Role / Trách nhiệm chính | Điểm Kích hoạt (Trigger Phase) |
|---|---|---|---|
| 1 | `@product-manager-toolkit` | **Product Manager (CEO)**: Viết PRD, đánh giá RICE, giao tiếp liên phòng ban. Ngăn chặn hội chứng "Phân tích quá độ" (Analysis Paralysis). | Xuyên suốt (Lên kế hoạch, Duyệt kết quả). |
| 2 | `@professional-cfo-analyst` | **CFO**: Đọc BCTC, duyệt chuẩn kế toán (Tài sản = Nợ + Vốn). Audit chuẩn IBCS màu sắc UI. Định nghĩa dữ liệu Tài chính (`DECIMAL`, Double-entry). | Khởi tạo bảng CSDL. Audit số liệu cuối. |
| 3 | `@data-engineering-data-pipeline` | **Data Engineer**: Xây dựng Schema (Tables, Views), thiết kế luồng ETL, chia Partition, Tối ưu Delta Lake/Supabase. | Phase Schema / Thiết kế Backend. |
| 4 | `@data-quality-frameworks` | **QA Engineer (Data)**: Sinh test dbt/Great Expectations giám sát `Null`, đứt gãy Time-series, cảnh báo lỗi logic (VD: `levels = 0`). | Phase Execution (Lúc chạy Python Script). |
| 5 | `@data-scientist` | **Data Scientist**: Khai phá dữ liệu sạch, lo thuật toán định giá 360, Churn prediction, NLP sentiment từ tin tức. | Tương lai (Sau khi Data Pipeline chạy ổn định). |
| 6 | `@web-design-guidelines` | **UI/UX Designer**: Giám sát Code React, đảm bảo Component Tree-Table render mượt mà, đúng chuẩn Vercel. Kiểm tra Accessibility. | Phase S (Xây dựng Frontend App). |
| 7 | `@security-auditor` | **Security/DevSecOps**: Chống lộ lọt Key (Env/Supabase), OWASP Top 10, phân quyền Auth Supabase (RLS Policies). | Code Review Phase / Trước khi Deploy. |
| 8 | `@writing-skills/references/testing` | **Testing Architect**: Đảm bảo toàn bộ quy trình Code (Backend/Frontend) đều vượt qua bộ Test TDD (RED-GREEN-REFACTOR) chịu áp lực. Không có bug lọt ra Prod. | Xuyên suốt quá trình Code (TDD). |

## 3. Quy trình Giao tiếp Liên phòng ban (Communication Protocol)

**Bước 1: PM Khởi tạo PRD (Product Requirement Doc)**
- Mọi logic mới bám theo BRD này. `@product-manager-toolkit` sẽ định nghĩa Scope qua file `.md`.

**Bước 2: Hệ Gen-Data (Data Pipeline)**
- `@data-engineering` thiết kế Schema.
- `@professional-cfo-analyst` Audit logic. => Đạt mới được Code.
- Chạy Code: `@data-quality-frameworks` túc trực bắt lỗi Null/Format.

**Bước 3: Hệ Hiển thị (Presentation)**
- Code React Tree-Table. 
- Nhúng `@web-design-guidelines` (để review component) & `@professional-cfo-analyst` (kiểm tra màu gold/white chuẩn IBCS).

**Bước 4: Hệ Bảo vệ (Security & Testing)**
- Toàn bộ Code đi qua TDD của `@testing` (không làm tắc trách dưới áp lực).
- `@security-auditor` quét `RLS` của Supabase đảm bảo không ai cào trộm data từ Frontend.

## 4. Scaling Protocol
Khi dự án mở rộng sang thị trường khác hoặc tích hợp Trí tuệ AI tạo Data, BRD này sẽ tự động được PM Toolkit update để chèn Agent Workflow bổ sung. Mọi công cụ (Tools) đều phải khai báo ở đây trước khi cấp quyền.
