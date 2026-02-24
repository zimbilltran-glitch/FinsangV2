# Finsang B.L.A.S.T. Execution Plan — Vietcap Migration

> **Version:** 2.0 | **Date:** 2026-02-24 | **Status:** 🟢 PHASES B+L+A+S COMPLETE
> **Primary Source:** [Vietcap IQ](https://trading.vietcap.com.vn/iq/company?ticker=VHC)
> **Golden Schema:** `VHC_BCTC.xlsx` (4 sheets — Quarter/Year × CĐKT/KQKD/LCTT/CSTC)
> **Supersedes:** `task_plan.md` v1.0 (KBSV / vnstock era)

---

## 🗺️ Skill Register (Phân quyền Đội ngũ)

| # | Skill / Role | Responsibility in this Pipeline |
|---|---|---|
| 🎯 | `@product-manager-toolkit` | **Orchestrator** — PRD, RICE score, scope gate at each phase |
| 📐 | `@data-engineer` | Schema design, ETL strategy, Parquet partition architecture |
| 🕷️ | `@autonomous-web-scraper` | Executes extraction (API intercept **or** headless Excel download) |
| 🔄 | `@financial-data-normalizer` | Maps raw payload → Golden Schema (VHC_BCTC 4-sheet standard) |
| 📊 | `@data-scientist` | Statistical validation, derived metrics (YoY, margins, ratios) |
| 💼 | `@professional-cfo-analyst` | Final audit — checksum, accounting identity (A = L + E) |
| 🎨 | `@ui-ux-designer` + `@ui-ux-pro-max` | Terminal/Markdown tabbed layout mimicking Vietcap's Quarter/Year tabs |
| 🏛️ | `@cto-mentor-supervisor` | Architectural review — production readiness, anti-over-engineering |

---

## Phase 1 — 🔵 BLUEPRINT
> *Define requirements, investigate extraction strategy, map the Golden Schema*

### 1.1 `@product-manager-toolkit` — Product Requirements

**Epic:** "As a financial analyst, I can switch between Quarter/Year tabs for any ticker to view CĐKT, KQKD, LCTT, and CSTC — identical to the Vietcap IQ interface."

**User Stories (RICE Prioritized):**

| Story | R | I | C | E | Score |
|---|---|---|---|---|---|
| View KQKD by Quarter (latest 8Q) | 9 | 9 | 3 | 1.0 | **27** |
| View CĐKT by Year (latest 5Y) | 8 | 8 | 3 | 1.0 | **21** |
| Switch between tabs (Q ↔ Y) | 9 | 9 | 2 | 1.0 | **40** |
| Search by ticker symbol | 7 | 7 | 2 | 0.8 | **24** |
| Download raw Excel (Golden Schema) | 5 | 4 | 2 | 0.6 | **10** |

**In-Scope:** VHC as pilot ticker → any VN ticker.
**Out-of-Scope:** Real-time prices, trading signals, portfolio management.

**Acceptance Criteria (Phase Gate):**
- [ ] PRD signed off by PM
- [ ] VHC_BCTC.xlsx fully parsed and schema documented
- [ ] Extraction method decided (API vs. Excel) with rationale

---

### 1.2 `@data-engineer` — Extraction Strategy Investigation

**Decision Matrix: API Interception vs. Headless Excel Download**

| Criterion | API Interception | Excel Download |
|---|---|---|
| **Stability** | 🟡 Medium (headers may rotate) | 🟢 High (file download is stable) |
| **Data Fidelity** | 🟢 Exact JSON → direct mapping | 🟢 Excel = Golden Schema format |
| **Speed** | 🟢 Fast (no parse overhead) | 🟡 Medium (Playwright + openpyxl) |
| **Rate-limit Risk** | 🔴 High (per-request token) | 🟡 Medium (file-level throttle) |
| **Maintenance** | 🔴 Breaks on endpoint change | 🟡 Breaks on layout change |
| **Golden Schema alignment** | 🔴 Requires full custom mapping | 🟢 Native alignment |

> **✅ CONFIRMED (2026-02-24):**
> **Primary → API** `https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{TICKER}/financial-statement?section={SECTION}`
> **Auth: NONE required** — API is fully public. One call per section returns all periods (year + quarter in same payload).
> **Fallback → Excel** via `...export?language=1` endpoint — no Playwright required, direct GET download.

**Tasks:**
- [x] Capture Vietcap IQ network requests via DevTools for VHC → document all JSON endpoints + auth headers
- [x] Verify token refresh mechanism → **No auth/token needed** (public API)
- [x] Map Excel download trigger → `export?language=1` endpoint confirmed
- [x] Prototype: fire live GET request for VHC BALANCE_SHEET section → 200 OK, 8Y+32Q returned

---

### 1.3 `@financial-data-normalizer` — Golden Schema Analysis

**Source:** `VHC_BCTC.xlsx` — 4 sheets:

| Sheet | Vietnamese Name | English Equivalent | Key Metrics |
|---|---|---|---|
| `CDKT` | Cân Đối Kế Toán | Balance Sheet | Total Assets, Total Liabilities, Equity |
| `KQKD` | Kết Quả Kinh Doanh | Income Statement | Revenue, COGS, Gross Profit, Net Profit |
| `LCTT` | Lưu Chuyển Tiền Tệ | Cash Flow Statement | Operating CF, Investing CF, Financing CF |
| `CSTC` | Chỉ Số Tài Chính | Financial Ratios | EPS, P/E, ROE, ROA, D/E |

**Tasks:**
- [x] Parse VHC_BCTC.xlsx → CDKT=122, KQKD=25, LCTT=41, NOTE=157 fields
- [x] Create `golden_schema.json` — 345 fields written to `Version_2/`
- [ ] Flag fields in Vietcap JSON payload absent from Golden Schema (Phase L task)

**Phase 1 Gate:** ✅ PASSED — 2026-02-24T22:52:59+07:00
- [x] Extraction strategy confirmed → **API PRIMARY** (public, no auth), Excel fallback via export endpoint
- [x] `golden_schema.json` finalized → 345 fields, 40 period columns per sheet
- [x] Endpoint/download mechanism documented → see `Version_2/findings.md`

---

## Phase 2 — 🟣 LINK
> *Scraper connects to Vietcap using Data Engineer specifications*

### 2.1 `@autonomous-web-scraper` — Vietcap Connection

**Input:** Extraction spec from Phase 1 (endpoint map OR download trigger path)

**Tasks (API Interception — PRIMARY):**
- [ ] Intercept `Authorization` bearer token from Vietcap IQ login session
- [ ] Map all BCTC JSON endpoints (CDKT/KQKD/LCTT/CSTC) per period type (quarter/year)
- [ ] Parametrize requests: `?ticker={TICKER}&period=quarter&limit=8` and `&limit=10` for year
- [ ] Save raw JSON responses to `.tmp/raw/{TICKER}/` with timestamp
- [ ] Verify response integrity (non-empty payload, expected field keys present)

**Tasks (Excel Download — FALLBACK, trigger only on API failure):**
- [ ] Launch headless Playwright → navigate to `https://trading.vietcap.com.vn/iq/company?ticker={TICKER}`
- [ ] Click "Tải về" (Download) button for each financial tab
- [ ] Save downloaded `.xlsx` to `.tmp/raw/{TICKER}/` with timestamp
- [ ] Verify file integrity (non-zero size, valid XLSX header)
- [ ] Log fallback activation to `pipeline_runs.extraction_method = 'excel_fallback'`

**Phase 2 Gate: ✅ PASSED — 2026-02-24T23:05:00+07:00**
- [x] Raw VHC data successfully retrieved and saved to `.tmp/` via `probe_vietcap_api.py`
- [x] 8 years + 32 quarters of data available per section (40 periods total)
- [x] No rate-limit blocks encountered in test run (public API, no auth)
- [x] All 4 sections 200 OK: BALANCE_SHEET, INCOME_STATEMENT, CASH_FLOW, NOTE

---

## Phase 3 — 🟠 ARCHITECT
> *Build the full data pipeline, storage layer, and validation rules*

### 3.1 `@data-engineer` — Parquet Hive-Style Pipeline

**Storage Architecture:**
```
data/
└── financial/
    └── {ticker}/
        └── period_type={quarter|year}/
            └── sheet={cdkt|kqkd|lctt|cstc}/
                └── {ticker}_{period}.parquet
```

**Pipeline Flow:**
```
.tmp/raw/{TICKER}/*.json  (or *.xlsx if fallback)
        ↓ (requests / pandas read_excel)
   Raw DataFrame
        ↓ (financial-data-normalizer)
   Normalized DataFrame (Golden Schema)
        ↓ (pandas to_parquet, Hive-partitioned)
   data/financial/{ticker}/.../*.parquet
        ↓ 🗑️ GARBAGE COLLECTION (auto-delete .tmp/raw/{TICKER}/*)
        ↓ (pyarrow filtered read)
   In-memory DataFrame → UI render
        ↓ (supabase-py upsert)
   Supabase → metadata + pipeline_runs
```

**Supabase Metadata Schema:**
```sql
CREATE TABLE pipeline_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker TEXT NOT NULL,
  period_type TEXT CHECK (period_type IN ('quarter', 'year')),
  sheet TEXT CHECK (sheet IN ('cdkt', 'kqkd', 'lctt', 'cstc')),
  periods_fetched TEXT[],
  source TEXT DEFAULT 'vietcap',
  extraction_method TEXT,
  run_at TIMESTAMPTZ DEFAULT now(),
  status TEXT DEFAULT 'success',
  error_log TEXT
);

CREATE TABLE financial_fields (
  field_id TEXT PRIMARY KEY,
  vn_name TEXT NOT NULL,
  en_name TEXT,
  sheet TEXT,
  unit TEXT,
  data_type TEXT DEFAULT 'DECIMAL'
);
```

**Tasks:**
- [x] Build `pipeline.py` — orchestrates Extract → Normalize → Store → GC
- [x] Implement Parquet writer with Hive partitioning (`data/financial/{ticker}/period_type={...}/sheet={...}/`)
- [x] Build `load_tab(ticker, period_type, sheet)` → returns wide DataFrame sorted by row_number
- [ ] Upsert `pipeline_runs` on each run (Supabase — Phase T)
- [x] **Garbage Collection:** `cleanup_tmp(ticker)` — auto-deletes `.tmp/raw/{ticker}/` after successful write
- [x] **Phase A Refinement:** Fixed `get_api_value()` to use 1-indexed sheet position (enumerate) not Excel row_number
  - `isa5` (Lợi nhuận gộp 2022) = 2,975,935,067,448 VND ✅
  - Added `sheet_row_idx` column to Parquet for field lineage audit

---

## Phase V/M — Validation & Metrics 🟡 NEXT

### `@data-scientist` — Derived Metrics (Phase M)
| Metric | Formula | Sheet |
|---|---|---|
| Gross Margin % | `Lợi nhuận gộp / Doanh thu thuần * 100` | KQKD |
| Net Margin % | `LNST / Doanh thu thuần * 100` | KQKD |
| Revenue YoY/QoQ | `%Δ Doanh thu thuần` | KQKD |
| Current Ratio | `Tài sản ngắn hạn / Nợ ngắn hạn` | CĐKT |
| D/E Ratio | `Nợ phải trả / Vốn chủ sở hữu` | CĐKT |

### `@professional-cfo-analyst` — Financial Audit Rules (Phase V)
**Checksums bắt buộc:**
```
Total Assets (bsa96) = Total Liabilities (bsa97) + Total Equity (bsa127)  (tolerance: ±0.1%)
Total Assets = Curent Assets + Non-Current Assets
Total Liabilities = Current Liabilities + Non-Current Liabilities
```

**Output Tab `[ CSTC ]`:**
- Terminal UI sẽ hiển thị một tab thứ 5 là "Chỉ số tài chính".
- Gắn cờ ✅ / ⚠️ / ❌ cho Audit Check ở các tab CĐKT/KQKD.

---

## Phase 5 — 🔴 TRIGGER
> *End-to-end test with a new ticker; CTO architectural review*

### 5.1 Integration Test — Ticker: `FPT`

- [ ] Scraper downloads FPT BCTC from Vietcap
- [ ] Normalizer maps FPT to Golden Schema (log new fields)
- [ ] Parquet files created at correct Hive paths
- [ ] Scientist validation: no critical nulls, continuous time-series
- [ ] CFO audit: accounting identity PASS
- [ ] UI renders all 4 tabs (Q+Y) for FPT
- [ ] `pipeline_runs` row in Supabase: `status = 'success'`

### 5.2 `@cto-mentor-supervisor` — Production Readiness Review

- [ ] Pipeline is idempotent (re-run = no duplicates)
- [ ] All failure modes log gracefully to `pipeline_runs`
- [ ] No secrets hardcoded (`.env` for all keys)
- [ ] Parquet read < 2s for 8-quarter load
- [ ] Extraction fallback path documented
- [ ] Complexity ≤ 3 Python files for core pipeline
- [ ] README updated with architecture diagram + quickstart
- [ ] CTO readiness score ≥ 80/100

---

## 📋 Phase Summary

* **Phase B (Blueprint)**: Chuẩn hóa Schema từ Excel. ✅
* **Phase L (Link)**: Kết nối và cào dữ liệu từ API Vietcap. ✅
* **Phase A (Architect)**: Xây dựng ETL, lưu trữ Parquet (Hive format). ✅
* **Phase S (Stylize)**: Hiển thị giao diện Terminal Tab-based. ✅
* **Phase T (Trigger)**: Tự động hóa, Supabase Logging, Multi-ticker. ✅
* **Phase V (Validate)**: Audit tài chính chuẩn CFO (A = L + E). ⏳ (Next)
* **Phase M (Metrics)**: Tính toán chỉ số phái sinh tự động. ⏳ (Next)

---

> **⚠️ HOLD — Awaiting USER approval before Phase 1 begins.**
