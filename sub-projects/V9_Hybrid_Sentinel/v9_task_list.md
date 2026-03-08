# Phase 9: Hybrid Sentinel - Implementation Task List

## 🔭 Vision
Build a self-healing pipeline that uses Excel as the "Ground Truth" to auto-discover API keys, eliminating manual mapping and preventing data rollback errors.

---

## 🏗️ Phase 9.1: Foundation & Sentinel Logic
- [ ] **Sentinel Discovery Engine** (`sentinel_worker.py`):
    - [ ] Implement Playwright downloader for 6 tickers (2 Bank, 2 Securities, 2 Normal).
    - [ ] Implement value-matching logic (Match Excel 2024 value -> API JSON key).
    - [ ] Multi-Sector Support (Handles `bsa/bsb/bss` overlaps).
- [ ] **Golden Schema Extension**:
    - [ ] Add `vietcap_key` structure for all sectors if missing.
    - [ ] Standardize `vn_name` for exact semantic matching.

## ⚡ Phase 9.2: Pipeline Optimization (Pruning)
- [ ] **8-Year Pruning**:
    - [ ] Modify `pipeline.py` to filter out records older than 8 years (32 quarters).
    - [ ] Optimize Parquet writing for smaller, faster files.
- [ ] **Incremental Sync Detection**:
    - [ ] Add logic to check existing Supabase periods.
    - [ ] Only fetch and upsert *new* periods (Year/Quarter) if they don't exist.

## 🛡️ Phase 9.3: Resilience & Documentation
- [ ] **Zero-Mapping Fallback**:
    - [ ] Ensure `vietcap.py` provider never picks up junk `0.0` values.
- [ ] **Agent handover guide**:
    - [ ] Create `V9_DEVELOPER_GUIDE.md` to prevent rollback.

---
## 📈 Current Progress: 5% (Planning Complete)
- [x] Folder Structure Created
- [x] Implementation Plan Drafted
- [ ] Sentinel Worker Prototype
