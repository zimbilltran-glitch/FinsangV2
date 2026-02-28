import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, './sub-projects/Version_2')

from metrics import calc_metrics

df = calc_metrics('VHC', 'quarter')
print("Columns:", df.columns.tolist()[:10])

if df.empty:
    print("DataFrame is empty!")
    sys.exit(1)

meta_cols = ["field_id", "vn_name", "unit", "level"]
period_cols = [c for c in df.columns if c not in meta_cols]

print("\n--- Rows with predominantly empty/NaN/0.0 values ---")
for _, row in df.iterrows():
    # Only check actual metric rows, not group headers
    if row["level"] == 0:
        continue
    
    # Check how many periods are missing data
    empty_count = 0
    for p in period_cols:
        val = row[p]
        if val is None or str(val).strip() == "" or str(val) == "nan" or str(val) == "0.0":
            empty_count += 1
            
    # If more than 80% are missing
    if len(period_cols) > 0 and (empty_count / len(period_cols)) > 0.8:
        print(f"- {row['vn_name']} ({row['field_id']}): Missing {empty_count}/{len(period_cols)} periods")

