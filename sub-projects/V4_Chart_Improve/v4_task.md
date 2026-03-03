# 📋 V4 Task Tracker — Analysis Charts Integration

> **Thư mục Project**: `sub-projects/V4_Chart_Improve`
> **Kế hoạch**: `v4_implementation_plan.md`
> **Trạng thái**: 🚀 Bắt đầu

---

## ✅ Phase 1: Blueprint & Layer (Setup & Data Routing)
- [ ] **P1.0**: Tạo môi trường V4 (`v4_implementation_plan.md`, `v4_task.md`, `v4_changelog.md`...)
- [ ] **P1.1**: Cài đặt dependency `recharts` vào `frontend/package.json`.
- [ ] **P1.2**: Update `App.jsx` cấu hình Tab mới có `id: 'ANALYSIS_CHARTS'`.
- [ ] **P1.3**: Xây dựng thư viện transform data `frontend/src/hooks/useAnalysisChartsData.js` lấy data Supabase đang có trên context.

## 🧩 Phase 2: Assemble (Frontend Components)
- [ ] **P2.1**: Dựng `AnalysisTab.jsx` (Container). Lọc & truyền data theo nhóm ngành (Bank, Sec, Normal).
- [ ] **P2.2**: Dựng Recharts Wrapper: `CompareBarChart.jsx`
- [ ] **P2.3**: Dựng Recharts Wrapper: `TrendLineChart.jsx`
- [ ] **P2.4**: Dựng Recharts Wrapper: `StackedAreaChart.jsx`
- [ ] **P2.5**: Dựng Recharts Wrapper: `DualAxisChart.jsx`
- [ ] **P2.6**: Connect toàn bộ Chart vào `AnalysisTab.jsx` với Data tương ứng.

## 🎨 Phase 3: Style (Theme & Polish)
- [ ] **P3.1**: Style Grid CSS cho Tab (Desktop 2 columns, Mobile 1 column).
- [ ] **P3.2**: Custom Recharts Tooltip giống SWS Theme (Dark glass, Inter font).
- [ ] **P3.3**: Hoàn thiện Formatter numbers trục Y và Tooltip.

## 🧪 Phase 4: Test (Audit & Finalize)
- [ ] **P4.1**: CFO Audit: Verify data chart với số bảng / Excel Sheet.
- [ ] **P4.2**: CTO Audit: Optimize React re-render.
- [ ] **P4.3**: Release & Update Changelog.
