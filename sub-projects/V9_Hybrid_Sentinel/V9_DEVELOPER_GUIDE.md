# Finsang Architectural Handover Guide: Phase 9 Hybrid Sentinel

## 🛡️ The "Golden Rule" (Never Roll Back)
**Do NOT manually edit `vietcap_key` values in `golden_schema.json` if they fail.** 
Manual editing leads to the "Rollback Loop" (Fixing one Sector breaks another). 

---

## 🏗️ The Hybrid Pipeline Architecture
Instead of static mapping, Phase 9 utilizes a dynamic **Sentinel Worker**.

### 1. Data Ingestion Stream
`Vietcap API (Requests)` ➔ `Normalization` ➔ `Parquet (8-Year Pruned)` ➔ `Supabase Wide View`

### 2. The Sentinel (Mapping Authority)
If data is missing or wrong:
1. Run `sub-projects/V9_Hybrid_Sentinel/sentinel_worker.py --ticker [TICKER] --sector [bank|sec|normal]`.
2. The worker will:
   - Download the **Excel Ground Truth** file.
   - Fetch the **API JSON Payload**.
   - Compare values to find the **True API Key**.
   - Automatically update `golden_schema.json` for all tickers in that sector.

### 3. Data Pruning (8-Year Limit)
Finsang now strictly enforces an **8-year / 32-quarter** limit. 
- Avoid fetching older data to keep Supabase performance high and mapping complexity low.
- Focus on the "Relevant Window" (2018-2025).

---

## 🛠️ Handling Sector Overlaps
Vietcap uses generic keys (`bsa1`, `bsa2`) across different report structures. 
- **Mapping Logic**: Always check the `sector` attribute in `companies` table before selecting a `vietcap_key` branch in `golden_schema.json`.
- **Bank/Securities**: Use `bsb/bss` or `isb/iss` branches preferentially.

---

## 📂 Folder Checklist
- **`sub-projects/V2_Data_Pipeline`**: Core extraction & loading logic.
- **`sub-projects/V6_Excel_Extractor`**: Historical Excel downloader (Used for Sentinel).
- **`sub-projects/V9_Hybrid_Sentinel`**: Future home of the Auto-Mapping Sentinel scripts.
