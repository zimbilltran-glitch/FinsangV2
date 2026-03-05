# Finsang Version Control & Update Timeline

Traceable history of system updates, version tags, and feature deployments.

---

## 🚀 Version History

### [v5.1.0] — 2026-03-05 (Current)
- **Feature:** Hoàn thiện Phase 5.6 - Sector Metrics Finalization (Bank/SEC).
- **Security:** RLS Hardening (SELECT only) & Timeout implementation.
- **Ops:** Phát hành `QUARTERLY_UPDATE_GUIDE.md` & Production Build.
- **Performance:** ThreadPool Resync (~28s cho VN30).

### [v5.0.0] — 2026-03-05
- **Feature:** Exact Ground Truth Mapping (Sửa lỗi trượt dòng).
- **Performance:** Khởi tạo `v5_full_resync.py` & `lite_schema.json`.
- **Audit:** CTO Audit (Score 67/100) → Kế hoạch tối ưu cao độ.

### [v4.0.0] — 2026-03-03
- **Feature:** Khởi tạo `sub-projects/V4_Chart_Improve` - Tab Biểu đồ phân tích (Analysis Charts).
- **UI:** Tích hợp Data Hook biến đổi dữ liệu từ bảng CDKT/KQKD sang định dạng tương thích biểu đồ `recharts`.
- **Docs:** Tạo bộ Management Files chuẩn B.L.A.S.T cho V4.

### [v3.0.0] — 2026-03-01
- **Feature:** Tích hợp Simply Wall St (Snowflake, Radar Chart, Gauge).
- **Data:** Fetch OHLCV VN30 & Calc Snowflake Scores.

### [v2.3.0-audit] — 2026-03-01
- **Audit:** Full project review — 10 findings documented.

### [v2.2.0] — 2026-02-28
- **Feature:** VN30 data enrichment. Fix index mapping.

---

## 📦 Component Status

| Component | Version | Health | Last Update | Notes |
|---|---|---|---|---|
| ETL Pipeline | 5.5.0 | 🟢 High Perf | 2026-03-05 | ~28s/VN30 Sync |
| Golden Schema | 5.3.0 | 🟢 GroundTruth | 2026-03-05 | Exact Mapping |
| Supabase Sync | 5.5.0 | 🟢 Streamed | 2026-03-05 | Bypasses Parquet path |
| React Frontend | 5.6.0 | 🟢 SectorAware | 2026-03-05 | Charts show SEC/Bank data |
| Metrics Engine | 5.6.0 | 🟢 Verified | 2026-03-05 | 40+ ratios per ticker |
| Security (RLS) | 5.7.0 | 🔐 Hardened | 2026-03-05 | SELECT only for anon |

---

## 🗺️ Active Roadmap

| # | Phase | Status | Target |
|---|---|---|---|
| 1 | 🔧 Phase 5.5 - Performance Tuning | ✅ DONE | Week 1 |
| 2 | 🏦 Phase 5.6 - Sector Metrics | ✅ DONE | Week 1 |
| 3 | 🚀 Phase 7.0 - Production Readiness | 🚀 ACTIVE | Week 2 |
| 4 | 📄 Phase 6.0 - PDF Statement Parsing | ⏳ PENDING | Week 3 |
| 5 | 📱 Phase 8.0 - Mobile Optimization | ⏳ BACKLOG| - |

---

## 📎 Key Documents

| Doc | Purpose |
|---|---|
| `README.md` | Central Navigation |
| `Finsang_Master_Active_Roadmap.md` | Timeline |
| `Finsang_Master_Task.md` | Active Task Tracker |
| `Finsang_Master_Logs.md` | Audit Trail |
| `QUARTERLY_UPDATE_GUIDE.md` | Ops Guide |
