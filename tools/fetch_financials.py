"""
Phase A & D Data Extraction Pipeline (fetch_financials.py)

WHAT IT DOES:
This script extracts raw financial report data from the KBSV API, transforms it from a Wide JSON structure
into a Long DataFrame, and merges it with a standardized Chart of Accounts (COA) template to create "Dense Data".
It then loads the dense data into Supabase `income_statement`, `balance_sheet`, or `cash_flow` tables.

WHY IT'S DESIGNED THIS WAY (Architectural Decisions):
1. Sparse to Dense Conversion: The raw KBSV API omits rows if a company has no activity (Value = 0) for that item.
   If saved natively, the Database would be missing rows (Sparse Data), causing KeyError crashes in Dashboarding and Data Science models.
   Solution: We query `tt200_coa` (The Master Template) and perform a Left-Join. Missing API values are forced to 0.0.
2. Recursive Level Calculation: The API often fails to provide the `Levels` attribute (defaults to 0).
   Solution: We reconstruct the tree locally by tracing `ReportNormID` to `ParentReportNormID` via an iterative/recursive function.
3. Wide to Long Pivot: To avoid altering the DB schema every single quarter (adding new columns), we store data
   vertically (period, item, value). Supabase JSONB or Frontend React handles the horizontal table rendering.
"""
import os
import sys
import json
import logging
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError as e:
    print(f"FAILED: Missing dependencies. {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
KBS_URL = "https://kbbuddywts.kbsec.com.vn/sas/kbsv-stock-data-store/stock/finance-info/"
TMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".tmp")

def get_report_name(report_type: str) -> str:
    mapping = {
        "KQKD": "Kết quả kinh doanh",
        "CDKT": "Cân đối kế toán",
        "LCTT": "Lưu chuyển tiền tệ"
    }
    return mapping.get(report_type, "Kết quả kinh doanh")

def extract_kbs(symbol: str, report_type: str, period: str) -> tuple[list, list]:
    """
    Extract raw JSON data directly from KBSV API.
    
    WHY: vnstock3 library is unstable/banned and vnstock doesn't export FinancialReport easily anymore.
    Direct API calls bypass library rot and allow direct extraction of 'Head' (Period metadata) and 'Content' (Data rows).
    """
    logger.info(f"Extracting {report_type} ({period}) for {symbol}...")
    termtype = 1 if period == "year" else 2
    
    url = f"{KBS_URL}{symbol.upper()}"
    params = {
        "page": 1,
        "pageSize": 8, # 8 periods
        "type": report_type,
        "termtype": termtype,
        "unit": 1000000000,
        "languageid": 1
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            head = data.get("Head", [])
            content = data.get("Content", {})
            report_name = get_report_name(report_type)
            items = content.get(report_name, [])
            
            # If exact match fails, try substring match or fallback to the first available list in Content
            if not items and content:
                for key, val in content.items():
                    if type(val) is list and len(val) > 0:
                        items = val
                        break
                        
            return head, items
            
        logger.error(f"Extract failed. HTTP {response.status_code}.")
    except Exception as e:
        logger.error(f"Request Error: {e}")
    return [], []

def transform_kbs(head: list, items: list, symbol: str, report_type: str, period_type: str, coa_data: list = None) -> pd.DataFrame:
    """
    Transform the WIDE JSON into a LONG DataFrame and resolve the Dense Data structure.
    
    WHY LONG FORMAT: Relational databases struggle with dynamically adding columns (Q1-2024, Q2-2024...).
    A Long format (Symbol, Period, Item, Value) allows infinite scaling without schema changes.
    
    WHY DENSE MERGING (coa_data): Bypasses the "Sparse Data" problem shown in `challenges.md`.
    """
    logger.info("Transforming JSON to LONG DataFrame and resolving dense structure...")
    if not items or not head:
        return pd.DataFrame()
    
    long_records = []
    
    # Map Value1, Value2... to actual period names from Head
    value_map = {}
    for i, h in enumerate(head):
        year = h.get("YearPeriod", "")
        term = h.get("TermCode", "")
        suffix = term if period_type == "quarter" else "year"
        val_name = f"Value{i+1}"
        period_name = f"{year}-{suffix}"
        value_map[val_name] = period_name
        
    # Build dictionary for sparse API items (id -> period -> value)
    api_data_by_item = {}
    for item in items:
        item_id = str(item.get("ReportNormID", ""))
        api_data_by_item[item_id] = {}
        for val_key, period_name in value_map.items():
            if val_key in item and item[val_key] is not None:
                api_data_by_item[item_id][period_name] = item[val_key]
                
    if coa_data and len(coa_data) > 0:
        logger.info(f"Using tt200_coa template with {len(coa_data)} items for Dense Merging.")
        for coa in coa_data:
            c_id = str(coa["item_id"])
            c_item = coa["item"]
            c_level = coa["levels"]
            c_rownum = coa["row_number"]
            c_kbsv_id = str(coa.get("kbsv_id", ""))
            
            for val_key, period_name in value_map.items():
                if c_kbsv_id == "CALC_TAX":
                    v16 = api_data_by_item.get("2219", {}).get(period_name, 0.0)
                    v17 = api_data_by_item.get("2220", {}).get(period_name, 0.0)
                    val = v16 + v17
                else:
                    val = api_data_by_item.get(c_kbsv_id, {}).get(period_name, 0.0)
                    
                record = {
                    "stock_name": symbol.upper(),
                    "asset_type": "STOCK",
                    "source": "KBSV",
                    "period": period_name,
                    "item": c_item,
                    "item_id": c_id,
                    "levels": c_level,
                    "row_number": c_rownum,
                    "unit": "Tỷ VND",
                    "value": val
                }
                long_records.append(record)
    else:
        logger.warning("No COA Data found. Falling back to sparse API schema.")
        parent_map = {item.get("ReportNormID"): item.get("ParentReportNormID") for item in items}
        def get_real_level(norm_id, visited=None):
            if visited is None:
                visited = set()
            if norm_id in visited:
                return 0
            visited.add(norm_id)
            parent_id = parent_map.get(norm_id)
            if not parent_id or parent_id == norm_id or parent_id not in parent_map:
                return 0
            return 1 + get_real_level(parent_id, visited)

        for item in items:
            item_id = str(item.get("ReportNormID", ""))
            item_name = item.get("Name", "")
            row_num = item.get("ID", 0)
            real_level = get_real_level(item.get("ReportNormID"))
            
            for val_key, period_name in value_map.items():
                if val_key in item and item[val_key] is not None:
                    record = {
                        "stock_name": symbol.upper(),
                        "asset_type": "STOCK",
                        "source": "KBSV",
                        "period": period_name,
                        "item": item_name,
                        "item_id": item_id,
                        "levels": real_level,
                        "row_number": row_num,
                        "unit": "Tỷ VND",
                        "value": item[val_key]
                    }
                    long_records.append(record)
                    
    df = pd.DataFrame(long_records)
    
    os.makedirs(TMP_DIR, exist_ok=True)
    tmp_file = os.path.join(TMP_DIR, f"{symbol}_{report_type}_{period_type}.csv")
    df.to_csv(tmp_file, index=False, encoding='utf-8')
    logger.info(f"Transformed to {len(df)} rows. Saved tmp: {tmp_file}")
    
    return df

def load_supabase(df: pd.DataFrame, report_type: str):
    """
    Upsert the transformed DataFrame into the respective Supabase table.
    
    WHY UPSERT (on_conflict): Allows idempotent execution. If the script is run multiple times, 
    it updates changed values instead of creating duplicates, tracked by (stock_name, period, item_id, source).
    """
    logger.info("Loading into Supabase...")
    if df.empty:
        logger.warning("Empty DataFrame, skipping load.")
        return
        
    url: str = os.environ.get("SUPABASE_URL") or ""
    key: str = os.environ.get("SUPABASE_KEY") or ""
    supabase: Client = create_client(url, key)
    
    records = df.to_dict(orient="records")
    
    table_map = {
        "KQKD": "income_statement",
        "CDKT": "balance_sheet",
        "LCTT": "cash_flow",
    }
    table_name = table_map.get(report_type, "income_statement")
    
    try:
        data, count = supabase.table(table_name).upsert(
            records, 
            on_conflict="stock_name,period,item_id,source"
        ).execute()
        logger.info(f"SUCCESS: Upserted {len(records)} records to Supabase table {table_name}.")
    except Exception as e:
        logger.error(f"FAILED to upsert into {table_name}: {e}")

def run_etl(symbol: str, report_type: str, period_type: str):
    load_dotenv()
    url: str = os.environ.get("SUPABASE_URL") or ""
    key: str = os.environ.get("SUPABASE_KEY") or ""
    supabase: Client = create_client(url, key)
    
    # Fetch COA Template
    if report_type == "LCTT":
        coa_res = supabase.table("tt200_coa").select("*").in_("report_type", ["LCTT_TT", "LCTT_GT"]).order("row_number").execute()
    else:
        coa_res = supabase.table("tt200_coa").select("*").eq("report_type", report_type).order("row_number").execute()
    coa_data = coa_res.data if coa_res.data else []
    
    # Extract
    head, items = extract_kbs(symbol, report_type, period_type)
    
    # Transform
    df = transform_kbs(head, items, symbol, report_type, period_type, coa_data)
    
    # Load
    load_supabase(df, report_type)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, required=True, help="Stock Ticker")
    parser.add_argument("--type", type=str, default="KQKD", choices=["KQKD", "CDKT", "LCTT"])
    parser.add_argument("--period", type=str, default="quarter", choices=["quarter", "year"])
    args = parser.parse_args()
    
    run_etl(args.symbol, args.type, args.period)
