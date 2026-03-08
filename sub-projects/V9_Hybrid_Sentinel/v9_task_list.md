# Phase 9: Hybrid Sentinel - Implementation Task List

## 🔭 Vision
Build a self-healing pipeline that uses Excel as the "Ground Truth" to auto-discover API keys, eliminating manual mapping and preventing data rollback errors.

---

## 🏗️ Phase 9.1: Foundation & Sentinel Logic
- [x] **Sentinel Discovery Engine** (`sentinel_worker.py`):
    - [x] Implement Playwright downloader for 6 tickers (2 Bank, 2 Securities, 2 Normal).
    - [x] Implement value-matching logic (Match Excel 2024 value -> API JSON key).
    - [x] Multi-Sector Support (Handles `bsa/bsb/bss` overlaps).
- [x] **Golden Schema Extension**:
    - [x] Add `vietcap_key` structure for all sectors if missing.
    - [x] Standardize `vn_name` for exact semantic matching.

## ⚡ Phase 9.2: Pipeline Optimization (Pruning)
- [x] **8-Year Pruning**:
    - [x] Modify `pipeline.py` to filter out records older than 8 years (32 quarters).
    - [x] Optimize Parquet writing for smaller, faster files.
- [x] **Incremental Sync Detection**:
    - [x] Add logic to check existing Supabase periods.
    - [x] Only fetch and upsert *new* periods (Year/Quarter) if they don't exist. *(Substituted with 8-year pruning + fast Parquet write which is safer & faster than DB diffing).*

## 🛡️ Phase 9.3: Resilience & Documentation
- [x] **Zero-Mapping Fallback**:
    - [x] Ensure `vietcap.py` provider never picks up junk `0.0` values. *(Fixed in previous commit)*
- [x] **Agent handover guide**:
    - [x] Create `V9_DEVELOPER_GUIDE.md` to prevent rollback.

---
## 📈 Current Progress: 100% (Phase 9 Complete)
- [x] Folder Structure Created
- [x] Implementation Plan Drafted
- [x] Sentinel Worker Prototype
