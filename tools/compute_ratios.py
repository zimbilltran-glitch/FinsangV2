"""
Phase C CFO Advanced Analytics (compute_ratios.py)

WHAT IT DOES:
Calculates key financial ratios (Gross Margin, Net Margin, ROE, ROA, Debt/Equity) using data from the
`income_statement` and `balance_sheet` tables mapped directly to the Fireant Universal Data Framework (`tt200_coa`), 
then upserts the results into the `financial_ratios` table.

WHY IT'S DESIGNED THIS WAY (Architectural Decisions):
1. Pre-Computation (MOLAP approach): Financial ratios could technically be computed on-the-fly via SQL Views or React frontend. 
   However, pre-computing them into a dedicated `financial_ratios` table dramatically reduces CPU load during API calls 
   and allows complex cross-period queries (e.g., "Find all VN30 companies with ROE > 15% in Q4") instantly.
2. Single Source of Truth: We rely purely on exact `item_id`s (e.g. `kqkd_3`, `cdkt_66`) rather than scraping text,
   guaranteeing mathematical stability and preventing KeyError crashes during Machine Learning processing.
"""
import os
import sys
import logging
import pandas as pd
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError as e:
    print(f"FAILED: Missing dependencies. {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def connect_supabase() -> Client:
    url: str = os.environ.get("SUPABASE_URL") or ""
    key: str = os.environ.get("SUPABASE_KEY") or ""
    return create_client(url, key)

def fetch_periods(supabase: Client, symbol: str) -> list:
    """Find out which periods exist in the database for the given symbol."""
    response = supabase.table("income_statement").select("period").eq("stock_name", symbol).execute()
    periods = set([r["period"] for r in response.data])
    return sorted(list(periods))

def get_value(supabase: Client, table: str, symbol: str, period: str, target_id: str) -> float:
    """
    Helper to fetch an exact value matching the Fireant target_id (`item_id`).
    """
    res = supabase.table(table).select("value").eq("stock_name", symbol).eq("period", period).eq("item_id", target_id).execute()
    if res.data and len(res.data) > 0 and res.data[0]['value'] is not None:
        return float(res.data[0]['value'])
    return 0.0

def compute_ratios_for_symbol(symbol: str):
    logger.info(f"Computing CFO Financial Ratios for {symbol} using Fireant Framework...")
    load_dotenv()
    supabase = connect_supabase()
    
    periods = fetch_periods(supabase, symbol)
    if not periods:
        logger.warning(f"No data found for {symbol} to compute ratios.")
        return

    ratios_records = []

    for period in periods:
        # Fetch key metrics by Fireant Exact ID
        revenue = get_value(supabase, "income_statement", symbol, period, "kqkd_3") # 3. Doanh thu thuần
        gross_profit = get_value(supabase, "income_statement", symbol, period, "kqkd_5") # 5. Lợi nhuận gộp
        net_income = get_value(supabase, "income_statement", symbol, period, "kqkd_19") # 19. Lợi nhuận sau thuế TNDN
        
        total_assets = get_value(supabase, "balance_sheet", symbol, period, "cdkt_66") # TỔNG CỘNG TÀI SẢN
        total_equity = get_value(supabase, "balance_sheet", symbol, period, "cdkt_100") # I. Vốn chủ sở hữu
        total_liabilities = get_value(supabase, "balance_sheet", symbol, period, "cdkt_68") # A. Nợ phải trả

        # Calculate Ratios
        gross_margin = (gross_profit / revenue * 100) if revenue else 0.0
        net_margin = (net_income / revenue * 100) if revenue else 0.0
        roe = (net_income / total_equity * 100) if total_equity else 0.0
        roa = (net_income / total_assets * 100) if total_assets else 0.0
        debt_to_equity = (total_liabilities / total_equity) if total_equity else 0.0

        ratios = {
            "Biên lợi nhuận gộp (%)": gross_margin,
            "Biên lợi nhuận ròng (%)": net_margin,
            "ROE - Lợi nhuận trên VCSH (%)": roe,
            "ROA - Lợi nhuận trên Tài sản (%)": roa,
            "D/E - Nợ trên VCSH (Lần)": debt_to_equity
        }

        for ratio_name, val in ratios.items():
            ratios_records.append({
                "stock_name": symbol,
                "asset_type": "STOCK",
                "source": "KBSV",
                "ratio_name": ratio_name,
                "period": period,
                "value": round(val, 2)
            })

    if ratios_records:
        logger.info(f"Upserting {len(ratios_records)} ratio records...")
        try:
            supabase.table("financial_ratios").upsert(ratios_records, on_conflict="stock_name,period,ratio_name,source").execute()
            logger.info("Successfully upserted ratios!")
        except Exception as e:
            logger.error(f"Failed to upsert ratios: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, required=True, help="Stock Ticker")
    args = parser.parse_args()
    compute_ratios_for_symbol(args.symbol.upper())
