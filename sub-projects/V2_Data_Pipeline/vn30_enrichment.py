import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "sub-projects/V2_Data_Pipeline"))

load_dotenv(dotenv_path=ROOT / ".env")

try:
    from supabase import create_client
except ImportError:
    print("❌ supabase-py not installed.")
    sys.exit(1)

from pipeline import run_pipeline
# sync_supabase is functionally a script, but we can import it
# Wait, sync_supabase.py relies on argparse in __main__, we can just call it via os.system or subprocess
import subprocess

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
if not url or not key:
    print("❌ SUPABASE_URL / SUPABASE_KEY not set")
    sys.exit(1)

sb = create_client(url, key)

FALLBACK_VN30 = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG", 
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB", 
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

def get_vn30_list():
    try:
        from vnstock3 import Vnstock
        stock = Vnstock().stock(symbol='VN30', source='VCI')
        # Vnstock3 API might be different. Let's fallback to the hardcoded list
        # It's safer to use the hardcoded list for reliability.
        return FALLBACK_VN30
    except Exception as e:
        print(f"⚠️ Could not fetch dynamic VN30 list: {e}. Using fallback.")
        return FALLBACK_VN30

def check_existing_periods(ticker: str) -> int:
    """
    Check how many quarterly periods already exist in Supabase for this ticker.
    We check balance_sheet for a standard field exactly (e.g. bsa1 = Tiền và tương đương tiền).
    """
    try:
        # We query the pipeline_runs to see if it has been run recently and logged
        # Or better, query balance_sheet
        response = sb.table("balance_sheet").select("period").eq("stock_name", ticker).like("period", "Q%").eq("item_id", "bsa1").execute()
        return len(response.data) if response.data else 0
    except Exception as e:
        print(f"  ⚠️ Error checking Supabase for {ticker}: {e}")
        return 0

def run_vn30_enrichment():
    print(f"\n{'='*60}")
    print(f"🦁 VN30 DATA ENRICHMENT (VIETCAP SOURCE) 🦁")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    tickers = get_vn30_list()
    print(f"Targeting {len(tickers)} tickers in VN30.")

    # Vietcap provides max 32 quarters (8 years) per fetch.
    TARGET_QUARTERS = 28 # If we have at least 28 quarters, we consider it "sufficiently enriched" for now

    successful = 0
    skipped = 0

    for i, ticker in enumerate(tickers, start=1):
        print(f"\n[{i}/{len(tickers)}] Processing {ticker}...")
        
        # 1. Check existing
        existing_q_count = check_existing_periods(ticker)
        print(f"   -> Found {existing_q_count} quarters in Supabase.")
        
        if existing_q_count >= TARGET_QUARTERS:
            print(f"   -> Skipping {ticker} (Already has >= {TARGET_QUARTERS} quarters).")
            skipped += 1
            continue
            
        print(f"   -> Fetching from Vietcap and generating Parquet...")
        try:
            # 2. Run pipeline (Extract to Parquet)
            run_pipeline(ticker)
            
            # 3. Upsert to Supabase
            print(f"   -> Upserting to Supabase...")
            script_path = str(ROOT / "sub-projects/V2_Data_Pipeline/sync_supabase.py")
            subprocess.run([sys.executable, script_path, "--ticker", ticker], check=True)
            
            successful += 1
            
            # 4. Sleep to prevent Rate Limit (Vietcap is quite lenient but play safe)
            print(f"   -> Sleep 3 seconds to avoid rate limit...")
            time.sleep(3)
            
        except Exception as e:
            print(f"   ❌ Failed to process {ticker}: {e}")

    print(f"\n{'='*60}")
    print(f" ENRICHMENT COMPLETE ")
    print(f" Processed: {successful}, Skipped: {skipped}, Total VN30: {len(tickers)}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    run_vn30_enrichment()
