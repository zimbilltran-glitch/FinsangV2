"""
Phase C CFO Advanced Analytics (compute_ratios.py)

WHAT IT DOES:
Calculates key financial ratios (Gross Margin, Net Margin, ROE, ROA, Debt/Equity) using data from the
`income_statement` and `balance_sheet` tables, then upserts the results into the `financial_ratios` table.

WHY IT'S DESIGNED THIS WAY (Architectural Decisions):
1. Pre-Computation (MOLAP approach): Financial ratios could technically be computed on-the-fly via SQL Views or React frontend. 
   However, pre-computing them into a dedicated `financial_ratios` table dramatically reduces CPU load during API calls 
   and allows complex cross-period queries (e.g., "Find all VN30 companies with ROE > 15% in Q4") instantly.
2. Cross-Table Dependency: Ratios like ROE require Net Income (from Income Statement) divided by Equity (from Balance Sheet). 
   Doing this via script acts exactly like a Data Warehouse ETL layer, ensuring data lineage.
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

def get_value(supabase: Client, table: str, symbol: str, period: str, search_items: list) -> float:
    """
    Helper to fetch a value matching any of the search_items names.
    
    WHY LIST MATCHING: The KBSV API items sometimes change slightly (e.g., "VỐN CHỦ SỞ HỮU" vs "Tổng cộng nguồn vốn chủ sỡ hữu").
    Passing an array of synonyms makes the ratio calculation resilient to upstream naming drift.
    """
    for item_name in search_items:
        res = supabase.table(table).select("value").eq("stock_name", symbol).eq("period", period).ilike("item", f"%{item_name}%").execute()
        if res.data and len(res.data) > 0 and res.data[0]['value'] is not None:
            return float(res.data[0]['value'])
    return 0.0

def compute_ratios_for_symbol(symbol: str):
    logger.info(f"Computing CFO Financial Ratios for {symbol}...")
    load_dotenv()
    supabase = connect_supabase()
    
    periods = fetch_periods(supabase, symbol)
    if not periods:
        logger.warning(f"No data found for {symbol} to compute ratios.")
        return

    ratios_records = []

    for period in periods:
        # Fetch key metrics
        revenue = get_value(supabase, "income_statement", symbol, period, ["Doanh thu thuần"])
        gross_profit = get_value(supabase, "income_statement", symbol, period, ["Lợi nhuận gộp"])
        net_income = get_value(supabase, "income_statement", symbol, period, ["Lợi nhuận sau thuế thu nhập doanh nghiệp"])
        
        total_assets = get_value(supabase, "balance_sheet", symbol, period, ["TỔNG CỘNG TÀI SẢN"])
        total_equity = get_value(supabase, "balance_sheet", symbol, period, ["VỐN CHỦ SỞ HỮU", "Tổng cộng nguồn vốn chủ sỡ hữu"])
        total_liabilities = get_value(supabase, "balance_sheet", symbol, period, ["NỢ PHẢI TRẢ"])

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
                "ratio_name": ratio_name,
                "period": period,
                "value": round(val, 2)
            })

    if ratios_records:
        logger.info(f"Upserting {len(ratios_records)} ratio records...")
        try:
            supabase.table("financial_ratios").upsert(ratios_records, on_conflict="stock_name,period,ratio_name").execute()
            logger.info("Successfully upserted ratios!")
        except Exception as e:
            logger.error(f"Failed to upsert ratios: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, required=True, help="Stock Ticker")
    args = parser.parse_args()
    compute_ratios_for_symbol(args.symbol.upper())
