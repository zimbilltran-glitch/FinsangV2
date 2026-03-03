"""
Phase D Master Template Initialization (seed_coa.py)

WHAT IT DOES:
Reads a manually curated, perfect benchmark CSV file (acting as our TT200 Chart of Accounts template), 
extracts the standardized item names, IDs, and hierarchical levels, and seeds them into the `tt200_coa` table.

WHY IT'S DESIGNED THIS WAY (Architectural Decisions):
1. The Antidote to Sparse Data: This script sets up the absolute source of truth for the financial schema. 
   When `fetch_financials.py` runs, it must Left-Join against this table. Even if the upstream API omits 90% of rows,
   the remaining 10% are mapped perfectly into this template, guaranteeing a mathematically sound structure 
   for dashboards and data scientists.
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    print("FAILED: Missing supabase")
    sys.exit(1)

def main():
    """
    Executes the ingestion of the Master Template into the Database.
    
    WHY: This is typically run ONCE during project setup (or when TT200 accounting standards change).
    Upsert guarantees it's idempotent (safe to re-run without duplicating records).
    """
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("Missing Supabase credentials in .env")
        return

    supabase = create_client(url, key)

    benchmark_file = os.path.join(".tmp", "NLG_benchmark.csv")
    if not os.path.exists(benchmark_file):
        print("Benchmark CSV not found.")
        return

    df = pd.read_csv(benchmark_file)
    
    # We will assume this is CDKT based on manual inspection.
    # CSV columns: 'Chỉ tiêu', 'item_id', 'Đơn vị', 'Level', + period columns
    
    records = []
    
    for idx, row in df.iterrows():
        item = str(row['Chỉ tiêu']).strip()
        item_id = str(row['item_id']).strip()
        level = int(row['Level'])
        
        # Determine row number: just 1-indexed based on order in file
        row_number = idx + 1
        
        record = {
            "report_type": "CDKT",
            "item_id": item_id,
            "item": item,
            "levels": level,
            "row_number": row_number
        }
        records.append(record)

    # Upsert
    try:
        res, count = supabase.table("tt200_coa").upsert(
            records,
            on_conflict="report_type,item_id"
        ).execute()
        print(f"SUCCESS: Seeded {len(records)} COA items into tt200_coa for CDKT.")
    except Exception as e:
        print(f"FAILED to seed: {e}")

if __name__ == "__main__":
    main()
