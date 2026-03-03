# 🎯 Finsang V4 — Biểu Đồ Phân Tích Chuyên Sâu (Analysis Charts)
# B.L.A.S.T. Implementation Plan

> **Blueprint → Layer → Assemble → Style → Test**  
> **Date**: 2026-03-03 | **Version**: 1.0 (Draft)  
> **Thư viện Chart**: `recharts` (được User phê duyệt do tính linh hoạt, nhẹ, và thân thiện với React Vite).  
> **Mục tiêu**: Thêm Tab "Biểu đồ phân tích" bên cạnh các tab báo cáo tài chính, hiển thị dữ liệu trực quan bằng biểu đồ tương tự dữ liệu trong sheet "Biểu đồ" của các file Excel (Ngân hàng, Chứng khoán, Phi tài chính).

---

## 📌 Tổng quan dự án

- **UI/UX Core**: Giữ nguyên triết lý thiết kế của V3 (Simply Wall St theme - Dark mode OLED, `#1A1A1A` background, Inter font).
- **Data Source**: Re-use dữ liệu trực tiếp từ các table `_wide` trên Supabase, không crawl/ETL lại (trừ khi thiếu dữ liệu thật sự). Map theo period (Quý/Năm) đang có.
- **Tính năng chính**: 
  - Render list các Chart quan trọng tùy theo nhóm ngành (Sector-aware: `bank`, `sec`, `normal`).
  - Dữ liệu tương tác mượt, crosshair tooltip chuẩn format (Tỷ VND, %, v.v.).
  - Layout Grid Responsive.

---

## ⚡ PHASE 1: BLUEPRINT & LAYER (Data Preparation & Routing)

> **Agent Assignment**: Frontend / Data Agent  
> **Nhiệm vụ chính**: Khởi tạo cấu trúc Tab mới và Hook tải dữ liệu.

- **P1.1 Thêm Tab "Biểu đồ phân tích"**: Cập nhật `App.jsx`, thêm entry vào `REPORT_TABS` với id `ANALYSIS_CHARTS`.
- **P1.2 Tạo Data Hook `useAnalysisChartsData.js`**:
  - Không fetch data mới. Xây dựng hook này để lấy data từ các state hiện hành (`data`, `periods`) trong `App.jsx`, sau đó transform (pivot) lại cho phù hợp với format input của `recharts` (`[{ period: 'Q4.24', value1: 100, value2: 50 }, ...]`).
  - **Lưu ý**: Cần truyền `sector` vào để hook biết lấy các `item_id` tương ứng ngành nào.
- **P1.3 Setup thư viện**: Chạy `npm install recharts`.

---

## ⚡ PHASE 2: ASSEMBLE (Frontend Chart Components)

> **Agent Assignment**: Frontend Agent  
> **Nhiệm vụ chính**: Xây dựng các Reusable Chart Components và ghép vào Layout.

- **P2.1 Container Component (`AnalysisTab.jsx`)**: 
  - Là Grid bọc toàn bộ các chart. 
  - Switch/Render tập hợp các chart khác nhau tùy theo `sector` (Bank vs Sec vs Normal).
- **P2.2 Recharts Base Components**:
  - `CompareBarChart.jsx`: Cột ghép (VD: Doanh thu vs Giá vốn).
  - `TrendLineChart.jsx`: Đường xu hướng (VD: Biên LN, Tăng trưởng, NPL).
  - `StackedAreaChart.jsx`: Cơ cấu (VD: Cơ cấu Tài sản, Cơ cấu Nguồn Vốn).
  - `DualAxisChart.jsx`: Mix Cột & Đường (VD: VCSH & ROE).
- **P2.3 Dữ liệu & Đề mục cụ thể (Tham chiếu file Excel)**:
  - **Phi tài chính**: DT/LN, Biên LN, Cơ cấu CĐKT, Tăng trưởng EPS.
  - **Ngân hàng**: Lãi thuần (NII)/NIM, Tín dụng/Huy động, Tỷ lệ nợ xấu (NPL & LLCR), CIR.
  - **Chứng khoán**: Cơ cấu tài sản tài chính (FVTPL/AFS/HTM), Dư nợ Margin, Lãi tự doanh/Môi giới.

---

## ⚡ PHASE 3: STYLE (Theme Integration)

> **Agent Assignment**: Frontend / UI Agent  
> **Nhiệm vụ chính**: Format làm đẹp biểu đồ.

- **P3.1 SWS Theme applied to Recharts**:
  - Tắt background của biểu đồ (`fill="transparent"`).
  - Màu line/bar dùng CSS variables của project.
  - Custom Tooltip của `recharts` để có background Dark Glassmorphism, font Inter.
- **P3.2 Number Formatting**:
  - Đảm bảo hàm formatter trong recharts dùng đúng `formatNumber()` để format `1,500.2 Tỷ VND` hoặc `15.5%`.

---

## ⚡ PHASE 4: TEST (Verification & Audit)

> **Agent Assignment**: CTO/CFO Agent  
> **Nhiệm vụ chính**: Đảm bảo chất lượng code và tính phi chức năng.

- **P4.1 CFO Verification**:
  - Đối chiếu con số hiển thị trên Tooltip của Recharts với dữ liệu hiển thị ở bảng CDKT/KQKD. Đảm bảo đúng chiều (âm/dương) và tỷ lệ.
- **P4.2 CTO Audit**:
  - Component re-render check (tránh loop khi transform data).
  - Bundle size check (import module `recharts` trực tiếp hoặc lazy load tab Chart để tránh nặng `App.jsx`).
  - Reponsive: Test hiển thị chart trên điện thoại giả lập.

---

## 🗺️ Execution Roadmap (Trình tự chạy Agent)

1. **Agent Setup**: Chạy `npm install recharts` & tạo các file base rỗng. *(Frontend)*
2. **Hook Build**: Viết logic `useAnalysisChartsData.js` biến data bảng thành data biểu đồ. *(Data/Frontend)*
3. **Component Build**: Dựng các Chart thuần túy. *(Frontend)*
4. **Assembly**: Lắp Chart vào `AnalysisTab.jsx` và tinh chỉnh màu sắc. *(Frontend)*
5. **Testing**: Review cross-check. *(CTO/CFO)*
