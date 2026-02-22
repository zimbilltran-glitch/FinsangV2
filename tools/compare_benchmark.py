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
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)

    benchmark_file = os.path.join(".tmp", "NLG_benchmark.csv")
    if not os.path.exists(benchmark_file):
        print("Benchmark CSV not found.")
        return

    df_bench = pd.read_csv(benchmark_file)

    # Clean up column names 
    print("--- BENCHMARK COLUMNS ---")
    print(df_bench.columns.tolist())
    
    # Typically column 0 is the item name? 
    # Let's inspect the first few items
    item_col = df_bench.columns[0]
    bench_items = df_bench[item_col].dropna().astype(str).str.strip().tolist()
    
    print("\n--- SAMPLE BENCHMARK ITEMS (First 15) ---")
    for i, itm in enumerate(bench_items[:15]):
        print(f"{i}: {itm}")

    # Fetch Supabase data for Income Statement
    print("\n--- FETCHING SUPABASE INCOME STATEMENT ---")
    res_is = supabase.table("income_statement").select("item, levels").eq("stock_name", "NLG").execute()
    db_is_items = set([x['item'].strip() for x in res_is.data])
    
    print(f"Total Income Statement items in DB: {len(db_is_items)}")
    print("Sample DB IS Items:", list(db_is_items)[:5])

    # Fetch Supabase data for Balance Sheet
    res_bs = supabase.table("balance_sheet").select("item, levels").eq("stock_name", "NLG").execute()
    db_bs_items = set([x['item'].strip() for x in res_bs.data])
    print(f"Total Balance Sheet items in DB: {len(db_bs_items)}")
    
    # Detect what's completely missing
    print("\n--- MISSING ANALYSIS ---")
    missing_from_db = []
    for b_item in bench_items:
        # We lowercase and remove numbers/dots from start to match loosely
        b_clean = b_item.lower().strip()
        matched = False
        for db_item in db_is_items.union(db_bs_items):
            db_clean = db_item.lower().strip()
            if db_clean in b_clean or b_clean in db_clean:
                matched = True
                break
        if not matched:
            missing_from_db.append(b_item)

    print(f"\nItems in Benchmark but NOT found in DB (substring match): {len(missing_from_db)}")
    for m in missing_from_db[:20]:
        print(f" - {m}")

if __name__ == "__main__":
    main()
