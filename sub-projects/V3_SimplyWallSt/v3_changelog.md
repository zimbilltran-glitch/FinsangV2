# V3 Progress Logs (V3 Historical)
> **Status:** ✅ COMPLETED / ARCHIVED

> Nhật ký tiến độ theo thời gian. Agent ghi log sau mỗi task hoàn thành.

---

## 2026-03-01 20:35 — Phase 0 Complete

**Agent**: Antigravity (Planning)  
**Action**: Hoàn thành research & viết implementation plan  
**Files created**: `README.md`, `implementation_plan.md`, `findings.md`, `challenges.md`, `logs.md`

**Decisions**:
- Chart library: Pure SVG (zero deps, không cần Plotly)
- Valuation: P/E based
- Tab: Thêm "360 Overview" riêng biệt, giữ nguyên 4 tabs cũ
- OHLCV: Fetch VN30 qua vnstock (VCI source)

---

## 2026-03-01 22:08 — Phase 1 & 2 Complete ✅

**Agent**: Antigravity (Implementation)  
**Sessions**: S1 (Migration) + S2 (OHLCV) + S6 (App.jsx + Hook) + S7-S8 (Components) + S9 (CSS)

### Delivered

| Phase | Task | Result |
|---|---|---|
| P1.3 | `company_overview` table | ✅ Created via migration |
| P1.1 | `fetch_ohlcv_vn30.py` | ✅ 9,455 rows (31 tickers × 305 rows) |
| P2.0 | Tab "360 Overview" trong App.jsx | ✅ Lazy-loaded, không regression |
| P2.8 | `useOverviewData.js` hook | ✅ 3 Supabase queries |
| P2.2 | `CompanyHero.jsx` | ✅ Price, change %, sector badge |
| P2.3 | `SnowflakeChart.jsx` | ✅ Pure SVG 5-axis radar |
| P2.7 | `QuickStats.jsx` | ✅ 2×4 metric grid |
| P2.4 | `ValuationGauge.jsx` | ✅ CSS gradient P/E gauge |
| P2.5 | `ChecklistCards.jsx` | ✅ Sector-aware pass/fail |
| P2.6 | `PriceChart.jsx` | ✅ Pure SVG area + hover tooltip |
| P2.1 | `OverviewTab.jsx` | ✅ Container |
| P3.1-3.2 | SWS CSS Theme | ✅ 420+ lines appended to App.css |

### Issues Resolved

- **VNDirect blocked**: Switched to vnstock (VCI source) — tested working
- **RLS policy**: Added `anon_write_ohlcv` policy on `stock_ohlcv` table
- **Price units**: vnstock = 1 unit → 1,000 VND. Fixed ×1000 in hook + chart

### Browser Verified

- ✅ 360 tab renders (zero console errors)
- ✅ Snowflake radar chart (5-axis, pure SVG)
- ✅ Valuation gauge (green/yellow/red zones)
- ✅ Price chart with real VHC data (2025-01-01 → 2026-02-27)
- ✅ Existing 4 tabs no regression (CDKT/KQKD/LCTT/CSTC)

### Remaining Tasks

| Task | Blocked On | Priority |
|---|---|---|
| P1.2: `fetch_company_overview.py` | ✅ DONE (Vietcap API -> vnstock fallback) | 🟢 LOW |
| P1.4: `calc_snowflake.py` | ✅ DONE | 🟢 LOW |
| P1.5: Extend `metrics.py` | ✅ DONE (ROE, ROA, D/E implemented in Snowflake) | 🟢 LOW |
| P4: CTO/CFO Audit | Ready for Audit | 🔴 HIGH |

---

## 2026-03-01 23:15 — Phase 1 & 3 Complete ✅

**Agent**: Antigravity (Implementation / Verification)  

### Delivered
| Phase | Task | Result |
|---|---|---|
| P1.2 | `fetch_company_overview.py` | ✅ Fetched P/E, P/B, Market Cap for 31 VN30 tickers via vnstock. Upserted to `company_overview`. |
| P1.4 | `calc_snowflake.py` | ✅ Calculated Value, Future, Past, Health, Dividend scores. |
| DB | `company_overview` schema | ✅ Applied migration adding EPS, ROE, Current Ratio, etc., and enabled `anon` RLS policies. |
| P4 | Data Verification | ✅ Verified UI correctly displaying `VHC` 61,500 VND and 54% Snowflake score. |

---

## 2026-03-02 23:55 — Phase 5 Data Pipeline Investigations (P7.1)

**Agent**: Antigravity  

### Delivered
| Phase | Task | Result |
|---|---|---|
| DB | `company_overview` | ✅ Applied migration adding bank metrics: `nim`, `npl_ratio`, `provision_coverage`, `loan_to_deposit`, `total_deposits`, `total_loans`, `financial_leverage`. |
| Docs | Control files update | ✅ `v3_task.md`, `v3_challenges.md`, `v3_findings.md` updated with API limitations and alternative DB solutions. |

### Investigations
- ❌ Probed `vnstock` sources (VCI & TCBS) cho Bank metrics: Thất bại do thay đổi phía server (VCI 403, TCBS AttributeError).
- ❌ Probed Vietcap Note API (thuyết minh BCTC): Schema json lộn xộn, mapping string phức tạp.
- ⚠️ Probed Fireant API: Yêu cầu Bearer token phức tạp khi chạy tự động.
- ✅ Truy vấn bảng `financial_ratios`: Database Version 2 (CFO_CALC_V2) đã tích hợp sẵn hầu hết các chỉ tiêu NIM (`bank_4_6`), Tiền gửi (`bank_2_1`), Cho vay KH (`bank_1_2`).
- 👉 **Hướng tới P5.1**: Dừng việc lấy dữ liệu qua vnstock API. Chúng ta sẽ điều chỉnh React Hook hoặc Backend script rút dữ liệu nội bộ từ `financial_ratios` để fill vào `company_overview` (hoặc render trực tiếp tại Component).
---

## 2026-03-03 16:25 — Phase 5, 6 & 7 Complete ✅

**Agent**: Antigravity (CFO & Lead Dev)
**Action**: Triển khai toàn bộ V3.1 (Financial Health Deep-Dive & Layout).

### Delivered
| Phase | Task | Result |
|---|---|---|
| P7.1 | `populate_bank_metrics.py` | ✅ Populate NIM, Deposits, Loans, LDR cho Top 10 Banks từ DB nội bộ. |
| P7.2 | `useOverviewData.js` extension | ✅ Support Balance Sheet item mapping (Normal + Bank items). |
| P5.1 | `BankKeyInfo.jsx` | ✅ Sector-aware summary (NIM/LDR cho Bank, P/E/D/E cho Normal). |
| P5.2 | `FinancialPositionChart.jsx` | ✅ SVG Stacked Bar (Assets vs Liab+Eq) + Bank logic fallback. |
| P5.3 | `DebtEquityHistoryChart.jsx` | ✅ SVG 8-year trend line (Nợ vs Vốn CSH) + Bank logic fallback. |
| P5.4 | `ChecklistCards.jsx` upgrade | ✅ Expandable narratives + icon dots summary header. |
| P6.1 | Sticky Section Navigation | ✅ Glassmorphic sub-nav bar + Smooth scroll. |
| UI/UX | CSTC Tab Layout Fix | ✅ Thẻ bảng CSTC không còn bị tràn màn hình; sticky "Chỉ tiêu" col; adaptive formatting. |
| Infra | Vite & Env fixes | ✅ Sửa lỗi `.env` thiếu Supabase keys và lỗi phân quyền hệ thống. |

### Browser Verified
- ✅ **Mã VHC**: Hiển thị D/E Chart, Position Chart, Health Checklist 4/5 đạt kèm narrative.
- ✅ **Mã VCB**: Hiển thị NIM 9.61%, LDR 98.6%, và charts dùng data bank (Tổng tài sản).
- ✅ **Section Nav**: Bám dính (sticky) top và nhảy đến đúng section khi click.
- ✅ **CSTC Tab**: Bảng cân đối, thu nhỏ tỷ lệ cho Ngân hàng/CTCK.

### Issues Resolved
- **Horizontal Overflow**: Khống chế `table-layout: fixed` và format số "Tr CP", "Tỷ VND" nhỏ gọn.
- **Bank BS Structure**: Map `cdkt_tai_san_ngan_han` sang `cdkt_bank_tong_tai_san` cho charts.

### Next Steps
- 🟢 Chuẩn bị Version 3.1 Release
- 🟢 Cập nhật tài liệu hướng dẫn vận hành pipeline mới.
