"""
populate_bank_metrics.py — V3 P7.1
Populate bank-specific metrics (NIM, Deposits, Loans, Loan/Deposit ratio)
in company_overview table using data already in financial_ratios_wide.

No external API needed — 100% in-house data.

Usage:
    python populate_bank_metrics.py
"""
import os, sys
from dotenv import load_dotenv

# Load .env from project root
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Try frontend .env
    env_path2 = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', '.env')
    if os.path.exists(env_path2):
        load_dotenv(env_path2)

from supabase import create_client

URL = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

if not URL or not KEY:
    print("[FAIL] SUPABASE_URL / SUPABASE_KEY not set")
    sys.exit(1)

sb = create_client(URL, KEY)

# Bank tickers in VN30
BANK_TICKERS = ['VCB', 'MBB', 'BID', 'CTG', 'TCB', 'ACB', 'VPB', 'STB', 'HDB', 'TPB']

# Mapping: financial_ratios_wide item_id -> company_overview column
RATIO_MAPPING = {
    'bank_4_6': 'nim',             # Bien lai rong (NIM) Uoc tinh (%)
    'bank_2_1': 'total_deposits',  # Tien gui cua khach hang (ty dong - stored as VND)
    'bank_1_2': 'total_loans',     # Cho vay khach hang (ty dong - stored as VND)
}


def get_latest_annual_value(ticker: str, item_id: str):
    """Get the latest annual value from financial_ratios_wide periods_data."""
    resp = sb.table('financial_ratios_wide') \
        .select('periods_data') \
        .eq('stock_name', ticker) \
        .eq('item_id', item_id) \
        .maybe_single() \
        .execute()
    
    if not resp.data or not resp.data.get('periods_data'):
        return None
    
    pd = resp.data['periods_data']
    # Get latest annual key (4-digit year), sorted descending
    annual_keys = sorted(
        [k for k in pd.keys() if len(k) == 4 and k.isdigit()],
        reverse=True
    )
    if not annual_keys:
        return None
    
    val = pd[annual_keys[0]]
    if val is None:
        # Try second latest
        if len(annual_keys) > 1:
            val = pd[annual_keys[1]]
    return val


def populate():
    print(f"[START] Populating bank metrics for {len(BANK_TICKERS)} tickers...")
    
    for ticker in BANK_TICKERS:
        print(f"\n  [{ticker}]")
        update_data = {}
        
        for item_id, col_name in RATIO_MAPPING.items():
            val = get_latest_annual_value(ticker, item_id)
            if val is not None:
                if col_name == 'nim':
                    # NIM is already in % format, store as-is
                    update_data[col_name] = round(float(val), 4)
                else:
                    # Monetary values: stored in VND (dong), convert to Ty VND for display
                    update_data[col_name] = float(val)
                print(f"    {col_name} = {update_data[col_name]}")
            else:
                print(f"    {col_name} = NULL (no data)")
        
        # Calculate loan_to_deposit ratio
        deposits = update_data.get('total_deposits')
        loans = update_data.get('total_loans')
        if deposits and loans and deposits > 0:
            ldr = loans / deposits
            update_data['loan_to_deposit'] = round(ldr, 4)
            print(f"    loan_to_deposit = {update_data['loan_to_deposit']}")
        
        # Upsert to company_overview
        if update_data:
            try:
                resp = sb.table('company_overview') \
                    .update(update_data) \
                    .eq('ticker', ticker) \
                    .execute()
                if resp.data:
                    print(f"    -> Updated OK")
                else:
                    print(f"    -> No row found for {ticker}, skipping")
            except Exception as e:
                print(f"    -> ERROR: {e}")
        else:
            print(f"    -> No data to update")
    
    print("\n[DONE] Bank metrics population complete.")


if __name__ == '__main__':
    populate()
