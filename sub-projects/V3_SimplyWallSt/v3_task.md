# 📋 V3 Task Tracker — Simply Wall St Integration (V3 Historical)
> **Status:** ✅ COMPLETED (Integrated into Main Production)
> **Last Updated**: 2026-03-03 16:20 (GMT+7)
> **Plan file**: `v3_implementation_plan.md` (cùng thư mục)
> **Changelog**: `v3_changelog.md`

---

## ✅ V3.0 — Đã hoàn thành (Phase 1-4)

### Phase 1: Backend Data Layer
- [x] P1.1: `fetch_ohlcv_vn30.py` — 9,455 rows (31 tickers)
- [x] P1.2: `fetch_company_overview.py` — 30+ metrics per ticker via vnstock
- [x] P1.3: Supabase migrations (4 migrations: create table, extend cols, add missing cols, RLS)
- [x] P1.4: `calc_snowflake.py` — 5-dim scoring (Value/Future/Past/Health/Dividend)
- [x] P1.5: ROE/ROA/D/E tính trong Snowflake (không cần sửa metrics.py)

### Phase 2: Frontend Components
- [x] P2.0: Thêm tab "360 Overview" vào `App.jsx`
- [x] P2.1: `OverviewTab.jsx` — container component
- [x] P2.2: `CompanyHero.jsx` — giá, vốn hóa, sector badge
- [x] P2.3: `SnowflakeChart.jsx` — Pure SVG 5-axis radar
- [x] P2.4: `ValuationGauge.jsx` — CSS gradient P/E gauge
- [x] P2.5: `ChecklistCards.jsx` — sector-aware pass/fail (bank/sec/normal)
- [x] P2.6: `PriceChart.jsx` — Pure SVG area chart + hover tooltip
- [x] P2.7: `QuickStats.jsx` — 2×4 metric grid
- [x] P2.8: `useOverviewData.js` — 3 Supabase queries (overview, OHLCV, ratios)

### Phase 3: SWS Theme
- [x] P3.1: CSS variables from `theme.css`
- [x] P3.2: 420+ lines CSS styling for 360 tab
- [x] P3.3: Inter font imported

### Phase 4: Verification
- [x] P4.1: Data verification (31 tickers, non-null scores)
- [x] P4.2: Browser tests (VHC/VCB/SSI, all 5 tabs)
- [x] P4.3: CTO audit (RLS, no API key leaks, error handling)
- [x] P4.4: CFO validation (P/E, ROE, Snowflake sanity)

---

## ✅ V3.1 — Bổ sung tính năng (Phase 5-7) — Đã hoàn thành

### Phase 5: Financial Health Deep-Dive 🔴 PRIORITY 1

- [x] **P5.1**: `BankKeyInfo.jsx` — Key Information box chuyên biệt theo sector
  - [x] Hiển thị NIM, Tiền gửi, Cho vay, LDR cho Ngân hàng
  - [x] Hiển thị P/E, D/E, ROE cho Phi tài chính và Chứng khoán
- [x] **P5.2**: `FinancialPositionChart.jsx` — Stacked Bar (Assets vs Liabilities)
  - [x] Pure SVG stacked bars: Tài sản NH/DH ↔ Nợ NH/DH + Vốn CSH
  - [x] Added Bank Fallback: Tự động dùng `cdkt_bank_*` nếu là mã Ngân hàng
- [x] **P5.3**: `DebtEquityHistoryChart.jsx` — Line+Area trend chart 8 năm
  - [x] Dual line (Nợ phải trả = red, Vốn CSH = blue)
  - [x] Added Bank Fallback: Historical data cho Bank items
- [x] **P5.4**: Expandable Checklist Cards
  - [x] Narrative field + animation expand trong `ChecklistCards.jsx`
  - [x] Icon row dots summary (🟢🔴) header

### Phase 6: Multi-Section 360 Tab Layout 🟡 PRIORITY 2

- [x] **P6.1**: Section-Based Navigation (Summary / Valuation / Health / Structure / History)
  - [x] Sub-nav bar: Sticky glassmorphism (12px blur)
  - [x] Smooth scroll behavior
- [x] **P6.2**: Checklist Header Icon Row
  - [x] Tích hợp row dots vào header phần sức khỏe tài chính

### Phase 7: Data Pipeline Enhancement 🟢 PRIORITY 3

- [x] **P7.1 (Script)**: Fetch & Populate Bank-Specific Metrics
  - [x] `populate_bank_metrics.py` — Rút data nội bộ từ `financial_ratios_wide` để fill `company_overview`.
  - [x] Đã chạy cho 10 mã ngân hàng lớn (VCB, BID, CTG, TCB, MBB, ACB, HDB, STB, VIB, LPB).
- [x] **P7.2**: Historical Balance Sheet Summary Data
  - [x] Cập nhật `useOverviewData.js` hook fetch trực tiếp `balance_sheet_wide`.
  - [x] Tích hợp mapping bank item IDs (`cdkt_bank_tong_tai_san`...).


---

## 🗺️ Execution Order khuyến nghị

```
Bước 1: P7.1 (bank data migration + fetch)    → ~5K tokens
Bước 2: P7.2 (BS summary view)                → ~3K tokens
Bước 3: P5.4 (expandable checklists)          → ~5K tokens  ← có thể song song Bước 1-2
Bước 4: P5.1 (BankKeyInfo component)          → ~5K tokens
Bước 5: P5.2 + P5.3 (Position + D/E charts)   → ~8K tokens  ← song song
Bước 6: P6.1 + P6.2 (section nav + icons)     → ~8K tokens
Bước 7: Browser test toàn bộ                  → ~3K tokens
```

**Tổng ước tính**: ~37K tokens, 5-7 sessions
