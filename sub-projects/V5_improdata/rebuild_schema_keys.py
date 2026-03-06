"""
V5 Phase 2 FINAL FIX — Hybrid mapping: Bank anchors + value fingerprinting.

We now know from Bank schema that:
- bsa53 = TỔNG TÀI SẢN  
- bsa54 = TỔNG NỢ PHẢI TRẢ
- bsa78 = VỐN CHỦ SỞ HỮU
- bsa96 = NỢ PHẢI TRẢ VÀ VỐN CHỦ SỞ HỮU (= Tổng nguồn vốn)

Strategy for CDKT (122 fields):
1. Name-exact match from Bank anchors (9 fields)
2. Bank anchors tell us: bsa29=TSCĐ, bsa43=ĐTDH, bsa53=TổngTS, bsa54=NợPT, bsa78=VốnCSH, bsa96=TổngNguồnVốn
3. For remaining 113 fields without name match:
   - Group 1 (Assets items, before TỔNG TÀI SẢN): sequential bsa1..bsa52 (skip anchored)
   - Group 2 (Liabilities items, bsa54..bsa77): sequential
   - Group 3 (Equity items, bsa78..bsa95): sequential
   - Group 4 (Supplementary, bsa159+): sequential
"""
import json, re
from pathlib import Path

V2 = Path(r'd:\Project_partial\Finsang\sub-projects\V2_Data_Pipeline')
V5 = Path(r'd:\Project_partial\Finsang\sub-projects\V5_improdata')

with open(V2 / "golden_schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)

# Load raw API
with open(V5 / "_raw" / "FPT_BALANCE_SHEET.json", "r", encoding="utf-8") as f:
    fpt_bs = json.load(f)
with open(V5 / "_raw" / "FPT_INCOME_STATEMENT.json", "r", encoding="utf-8") as f:
    fpt_is = json.load(f)
with open(V5 / "_raw" / "FPT_CASH_FLOW.json", "r", encoding="utf-8") as f:
    fpt_cf = json.load(f)

# ─── Known CORRECT mappings from Bank schema (bsa keys) ──────────────────────
BANK_ANCHORS = {
    "TỔNG TÀI SẢN": "bsa53",
    "TỔNG NỢ PHẢI TRẢ": "bsa54",
    "VỐN CHỦ SỞ HỮU": "bsa78",
    "VỐN ĐIỀU LỆ": "bsa80",
    "NỢ PHẢI TRẢ VÀ VỐN CHỦ SỞ HỮU": "bsa96",
}

# Build name-to-key from Bank schema (exact + fuzzy)
bank_fields = [f for f in schema["fields"] if f["sheet"] == "CDKT_BANK"]
bank_name_to_bsa = {}
for bf in bank_fields:
    key = bf["vietcap_key"]
    if key.startswith("bsa"):
        bank_name_to_bsa[bf["vn_name"].strip()] = key

# ─── CDKT normal mapping: Segment-based approach ─────────────────────────────
cdkt_fields = [f for f in schema["fields"] if f["sheet"] == "CDKT"]
cdkt_fields.sort(key=lambda x: x.get("row_number", 0))

# Known structural positions in our schema
STRUCTURAL_FIELDS = {
    "cdkt_tong_cong_tai_san":  "bsa53",   # Tổng cộng tài sản
    "cdkt_no_phai_tra":        "bsa54",   # Nợ phải trả (= Tổng nợ phải trả)
    "cdkt_von_chu_so_huu":     "bsa78",   # Vốn chủ sở hữu
    "cdkt_tong_cong_nguon_von":"bsa96",   # Tổng cộng nguồn vốn (= Nợ + Vốn)
}

# Find indices of structural fields
struct_indices = {}
for i, f in enumerate(cdkt_fields):
    if f["field_id"] in STRUCTURAL_FIELDS:
        struct_indices[f["field_id"]] = i

log = []
log.append("STRUCTURAL FIELD POSITIONS:")
for fid, idx in struct_indices.items():
    log.append(f"  {fid:45s} → schema[{idx}] = bsa key should be {STRUCTURAL_FIELDS[fid]}")

# ─── Segment the fields ──────────────────────────────────────────────────────
# Segment A: Assets (field[0] to field[idx_of_tong_tai_san])
# Segment B: Total Assets (one field)  
# Segment C: Liabilities (after Total Assets to before VốnCSH)
# Segment D: Equity (VốnCSH onwards to before TổngNguồnVốn)
# Segment E: Tổng nguồn vốn (last field)

idx_total_assets = struct_indices["cdkt_tong_cong_tai_san"]  # 65
idx_liabilities = struct_indices["cdkt_no_phai_tra"]          # 66
idx_equity = struct_indices["cdkt_von_chu_so_huu"]            # 97
idx_total_source = struct_indices["cdkt_tong_cong_nguon_von"] # 121

log.append(f"\nSegments:")
log.append(f"  A (Assets):      fields [0..{idx_total_assets-1}] = {idx_total_assets} fields → bsa1..bsa52")
log.append(f"  B (Total Assets): field [{idx_total_assets}] → bsa53")
log.append(f"  C (Liabilities): fields [{idx_liabilities}..{idx_equity-1}] = {idx_equity-idx_liabilities} fields → bsa54..bsa77")
log.append(f"  D (Equity):      fields [{idx_equity}..{idx_total_source-1}] = {idx_total_source-idx_equity} fields → bsa78..bsa95 + bsa159+")
log.append(f"  E (Total Source): field [{idx_total_source}] → bsa96")

# Build API key pools for each segment
all_bsa_nums = sorted(set(
    int(re.match(r'bsa(\d+)', k).group(1))
    for yr in fpt_bs.get("years", [])
    for k in yr
    if re.match(r'^bsa(\d+)$', k) and yr[k] is not None
))

pool_A = [n for n in all_bsa_nums if 1 <= n <= 52]           # Assets detail
pool_C = [n for n in all_bsa_nums if 54 <= n <= 77]          # Liabilities detail  
pool_D = [n for n in all_bsa_nums if (78 <= n <= 95) or (n >= 159)]  # Equity + supplementary

log.append(f"\nAPI key pools:")
log.append(f"  Pool A (1-52): {len(pool_A)} keys → {pool_A}")
log.append(f"  Pool C (54-77): {len(pool_C)} keys → {pool_C}")
log.append(f"  Pool D (78-95,159+): {len(pool_D)} keys → {pool_D}")

# Segment A: 65 schema fields, 52 API keys → more fields than keys!
# This means some schema fields don't have API data (Vietcap doesn't track those sub-items)
num_A_fields = idx_total_assets
num_A_keys = len(pool_A)
log.append(f"\n  Segment A: {num_A_fields} fields vs {num_A_keys} keys → {'OK' if num_A_fields == num_A_keys else f'MISMATCH ({num_A_fields - num_A_keys} extra fields)'}")

# Segment C: liabilities
num_C_fields = idx_equity - idx_liabilities
num_C_keys = len(pool_C)
log.append(f"  Segment C: {num_C_fields} fields vs {num_C_keys} keys → {'OK' if num_C_fields == num_C_keys else f'MISMATCH ({num_C_fields - num_C_keys} extra)'}")

# Segment D: equity + supplementary  
num_D_fields = idx_total_source - idx_equity
num_D_keys = len(pool_D)
log.append(f"  Segment D: {num_D_fields} fields vs {num_D_keys} keys → {'OK' if num_D_fields == num_D_keys else f'MISMATCH ({num_D_fields - num_D_keys} extra)'}")

# ─── Now apply the mapping ────────────────────────────────────────────────────
log.append(f"\n{'='*70}")
log.append("APPLYING SEGMENTED MAPPING:")

new_mapping = {}

# Segment A: Assets → bsa1..bsa52. We have MORE fields than keys.
# Map first 52 fields to bsa1..52, remaining get empty
for i in range(idx_total_assets):
    if i < len(pool_A):
        new_mapping[cdkt_fields[i]["field_id"]] = f"bsa{pool_A[i]}"
    else:
        new_mapping[cdkt_fields[i]["field_id"]] = ""  # No mapping

# Segment B: Total Assets
new_mapping["cdkt_tong_cong_tai_san"] = "bsa53"

# Segment C: Liabilities → bsa54..bsa77
liab_fields = cdkt_fields[idx_liabilities:idx_equity]
for j, f in enumerate(liab_fields):
    if f["field_id"] in STRUCTURAL_FIELDS:
        new_mapping[f["field_id"]] = STRUCTURAL_FIELDS[f["field_id"]]
    elif j < len(pool_C):
        new_mapping[f["field_id"]] = f"bsa{pool_C[j]}"
    else:
        new_mapping[f["field_id"]] = ""

# Segment D: Equity + supplementary → bsa78..bsa95, bsa159+
equity_fields = cdkt_fields[idx_equity:idx_total_source]
for j, f in enumerate(equity_fields):
    if f["field_id"] in STRUCTURAL_FIELDS:
        new_mapping[f["field_id"]] = STRUCTURAL_FIELDS[f["field_id"]]
    elif j < len(pool_D):
        new_mapping[f["field_id"]] = f"bsa{pool_D[j]}"
    else:
        new_mapping[f["field_id"]] = ""

# Segment E: Total Source
new_mapping["cdkt_tong_cong_nguon_von"] = "bsa96"

# Apply name-based corrections from Bank schema
for i, f in enumerate(cdkt_fields):
    vn_name = f["vn_name"].strip()
    if vn_name in bank_name_to_bsa:
        bank_key = bank_name_to_bsa[vn_name]
        if new_mapping.get(f["field_id"]) != bank_key:
            log.append(f"  NAME FIX: {f['field_id']:50s} {new_mapping.get(f['field_id'],''):10s} → {bank_key} ({vn_name})")
            new_mapping[f["field_id"]] = bank_key

# ─── Apply to schema ─────────────────────────────────────────────────────────
changes = 0
for f in schema["fields"]:
    if f["field_id"] in new_mapping:
        old = f.get("vietcap_key", "")
        new = new_mapping[f["field_id"]]
        if old != new:
            f["vietcap_key"] = new
            changes += 1

log.append(f"\n  Total changes applied: {changes}")

# ─── Save ─────────────────────────────────────────────────────────────────────
with open(V2 / "golden_schema.json", "w", encoding="utf-8") as f:
    json.dump(schema, f, ensure_ascii=False, indent=2)

log.append(f"  Saved to: {V2 / 'golden_schema.json'}")

# ─── Verify key fields ───────────────────────────────────────────────────────
yr_2024 = None
for yr in fpt_bs.get("years", []):
    if yr.get("yearReport") == 2024 and yr.get("lengthReport") == 5:
        yr_2024 = yr
        break

log.append(f"\n{'='*70}")
log.append("VERIFICATION (FPT 2024 values via new mapping):")
verify_fields = [
    "cdkt_tai_san_ngan_han",
    "cdkt_tai_san_dai_han", 
    "cdkt_tong_cong_tai_san",
    "cdkt_no_phai_tra",
    "cdkt_no_ngan_han",
    "cdkt_von_chu_so_huu",
    "cdkt_tong_cong_nguon_von",
]
for fid in verify_fields:
    key = new_mapping.get(fid, "?")
    val = yr_2024.get(key) if yr_2024 and key else None
    vn = next((f["vn_name"] for f in cdkt_fields if f["field_id"] == fid), "?")
    log.append(f"  {fid:45s} → {key:10s} = {val:>25} | {vn}")

with open(V5 / "_final_mapping_log.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log))
