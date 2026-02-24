# Findings V2.0 — Vietcap Pipeline

> **Version:** 2.0  
> **Auditor:** `@cto-mentor-supervisor`  
> **Scope:** Vietcap IQ data source → Parquet Hive pipeline → Tabbed UI  
> **Golden Schema:** `VHC_BCTC.xlsx` (4 sheets)

---

## 🏛️ Standing Architecture Decisions

| Decision | Chosen | Rationale |
|---|---|---|
| Primary extraction | API Interception (JSON) | Speed, low resource, no Playwright overhead |
| Fallback extraction | Headless Excel Download | Stable if API tokens rotate |
| Local storage | Parquet + Hive partitioning | Enables tab-switch filtering without DB query |
| Cloud metadata | Supabase (`pipeline_runs`, `financial_fields`) | Audit trail + field registry |
| Golden Schema | `VHC_BCTC.xlsx` (4 sheets) | Absolute standard; normalizer always maps to this |
| Data horizon | 8 quarters + 10 years | User-specified requirement |

---

## 🕵️ CTO Audit Reports

### Phase B Gate — ✅ PASSED
> **Timestamp:** 2026-02-24T22:44:22+07:00
> **Auditor:** `@cto-mentor-supervisor` (passive log)

**Results:**

| Sheet | Excel Tab | Fields | Periods |
|---|---|---|---|
| `CDKT` | Balance Sheet | **122** | 40 |
| `KQKD` | Income Statement | **25** | 40 |
| `LCTT` | Cash Flow | **41** | 40 |
| `NOTE` | Note / Supplements | **157** | 40 |
| **TOTAL** | | **345** | |

**Period columns detected:** 8 years (2018–2025) + 32 quarters per sheet.

**Outputs generated:**
- ✅ `Version_2/golden_schema.json` — 345 fields, canonical field registry
- ✅ `Version_2/schema_report.md` — human-readable full field table per sheet
- ✅ `Version_2/extract_golden_schema.py` — reproducible extractor script

**CTO Score (Phase B):** 88/100
- ✅ stdlib-only (no new dependencies)
- ✅ Footer rows correctly excluded (Vietcap branding stripped)
- ✅ field_id deduplication via suffix counter
- ⚠️ `en_name` fields blank — to be filled by `@financial-data-normalizer` in Phase A
- ⚠️ `level` detection uses whitespace heuristic — may need manual review for NOTE sheet



---

### Phase L Gate — [PENDING]
> *No audit yet — Phase L not started*

---

### Phase A Gate — [PENDING]
> *No audit yet — Phase A not started*

---

### Phase S Gate — [PENDING]
> *No audit yet — Phase S not started*

---

### Phase T Gate — [PENDING]
> *No audit yet — Phase T not started*

---

## 📡 Source Intelligence

### Vietcap IQ — ✅ CONFIRMED (2026-02-24T22:52:59+07:00)

**Access:** Fully **public** — no login / bearer token required for read access.

**Base URL pattern:**
```
https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{TICKER}/financial-statement?section={SECTION}
```

| Section Value | Sheet | Maps to Golden Schema |
|---|---|---|
| `BALANCE_SHEET` | CDKT | ✅ 122 fields |
| `INCOME_STATEMENT` | KQKD | ✅ 25 fields |
| `CASH_FLOW` | LCTT | ✅ 41 fields |
| `NOTE` | NOTE | ✅ 157 fields |

**Key discovery:** Switching `Quý ↔ Năm` in the UI does **NOT** trigger a new API call — both period types are embedded in the **same JSON payload** (a `years: [...]` array). This means one API call per section captures all periods.

**Export endpoint:**
```
GET https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{TICKER}/financial-statement/export?language=1
```
Triggered by "Tải xuống" button — returns Excel file directly.

**UI Tab Structure:**
```
Tài Chính (Financial)
  ├─ Tóm tắt (Summary)
  ├─ Lợi nhuận KD (Business Profit)
  ├─ Chỉ số (Financial Ratios)
  └─ Báo cáo tài chính (Financial Statements)  ← our target
       ├─ [Quý] [Năm]                           ← period switch (client-side only)
       ├─ Bảng cân đối kế toán (CDKT)
       ├─ Kết Quả Kinh Doanh (KQKD)
       ├─ Báo Cáo Lưu Chuyển Tiền Tệ (LCTT)
       ├─ Thuyết Minh (NOTE)
       └─ [Tải xuống] ↓                         ← export button
```

**Strategic Impact on Phase L:**
- ✅ **API approach is confirmed PRIMARY** — 4 simple GET requests, no auth, no Playwright needed for data fetch
- ✅ **Excel fallback still available** via the export endpoint (same URL, just triggers file download)
- ✅ **Complexity budget stays low** — `requests.get()` only, no headless browser for API path

### Golden Schema (`VHC_BCTC.xlsx`)
- **Source:** User-provided ground truth
- **Sheets:** CDKT (122), KQKD (25), LCTT (41), NOTE (157) = **345 total fields**
- **Canonical field registry:** `Version_2/golden_schema.json` ✅ WRITTEN
- **Human report:** `Version_2/schema_report.md` ✅ WRITTEN

---

## 🔄 Open Questions (Phase B to resolve)

- [ ] What is the exact Vietcap API endpoint structure per sheet/period type?
- [ ] Does the bearer token expire per session or per day?
- [ ] Are CSTC ratios computed server-side or derivable from raw data?
- [ ] Does Vietcap enforce IP-level rate limiting on JSON endpoints?

---

*— Last updated by `@cto-mentor-supervisor` | 2026-02-24T22:34:31+07:00*
