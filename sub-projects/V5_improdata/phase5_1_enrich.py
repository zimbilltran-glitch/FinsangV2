import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(str(Path(__file__).parent.parent.parent))

dotenv_path = Path(__file__).parent.parent.parent / "frontend" / ".env"
load_dotenv(dotenv_path)
SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("VITE_SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TICKERS = [
    'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
    'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SHB', 'SSB', 'SSI', 'STB',
    'TCB', 'TPB', 'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE'
]

# Keys mapping
NET_INCOME_KEYS = {
    'normal': 'kqkd_loi_nhuan_cua_co_dong_cua_cong_ty_me',
    'bank': 'kqkd_bank_co_dong_cua_cong_ty_me',
    'sec': 'kqkd_sec_loi_nhuan_sau_thue_phan_bo_cho_chu_so_huu'
}

EQUITY_KEYS = {
    'normal': 'cdkt_von_chu_so_huu',
    'bank': 'cdkt_bank_von_chu_so_huu',
    'sec': 'cdkt_sec_von_chu_so_huu_1' # I will check the correct SEC equity key later, let's look it up
}

def get_latest_financial_value(ticker, item_id):
    # Retrieve the latest quarter/year value for a given item_id from supabase
    try:
        if "kqkd" in item_id:
            table = "income_statement_wide"
        elif "cdkt" in item_id:
            table = "balance_sheet_wide"
        else:
            return None

        res = supabase.table(table).select("periods_data").eq("stock_name", ticker).eq("item_id", item_id).execute()
        if not res.data:
            return None
        
        periods_data = res.data[0]['periods_data']
        # For equity -> get latest annual (year) or latest quarter
        # Filter quarterly keys
        q_keys = [k for k in periods_data.keys() if "Q" in k and "/" in k]
        if q_keys:
            latest_q = max(q_keys, key=lambda x: (int(x.split('/')[1]), int(x.split('Q')[1].split('/')[0])))
            return float(periods_data[latest_q] or 0)
        return None
    except Exception as e:
        print(f"Error fetching {item_id} for {ticker}: {e}")
        return None

def get_net_income_ttm(ticker, item_id):
    # get the sum of the last 4 quarters
    try:
        res = supabase.table("income_statement_wide").select("periods_data").eq("stock_name", ticker).eq("item_id", item_id).execute()
        if not res.data:
            return 0
        periods_data = res.data[0]['periods_data']
        q_keys = sorted([k for k in periods_data.keys() if "Q" in k and "/" in k], 
                       key=lambda x: (int(x.split('/')[1]), int(x.split('Q')[1].split('/')[0])), reverse=True)
        # Take latest 4
        ttm = 0
        for k in q_keys[:4]:
            val = periods_data[k]
            if val is not None:
                ttm += float(val)
                
        if ttm == 0:
            y_keys = [k for k in periods_data.keys() if "Q" not in k]
            if y_keys:
                latest_y = max(y_keys, key=lambda x: int(x))
                ttm = float(periods_data[latest_y] or 0)
                
        return ttm
    except Exception as e:
        print(f"Error fetching TTM {item_id} for {ticker}: {e}")
        return 0

def fetch_sec_equity_key():
    # Will do this just to confirm
    pass

def main():
    # First, let's correct the SEC equity key.
    sec_eq = supabase.table("balance_sheet_wide").select("item_id, item").eq("stock_name", "SSI").ilike("item", "Vốn chủ sở hữu").execute()
    sec_equity_item_id = sec_eq.data[0]["item_id"] if sec_eq.data else "cdkt_sec_von_chu_so_huu"
    EQUITY_KEYS['sec'] = sec_equity_item_id

    for ticker in TICKERS:
        try:
            print(f"\\nProcessing {ticker}...")
            # 1. Fetch current overview data
            ov_res = supabase.table("company_overview").select("sector, current_price, market_cap").eq("ticker", ticker).execute()
            if not ov_res.data:
                print(f"Skip {ticker} - not found in company_overview")
                continue
            
            ov = ov_res.data[0]
            sector = ov["sector"]
            market_cap_ty_vnd = float(ov["market_cap"]) if ov["market_cap"] else 0
            
            # 2. Get OHLCV for 52W High/Low and current price
            one_year_ago = (datetime.now() - timedelta(days=365)).isoformat()
            ohlcv_res = supabase.table("stock_ohlcv").select("high, low, close").eq("stock_name", ticker).gte("time", one_year_ago).execute()
            
            w52_high = 0
            w52_low = 0
            current_price = 0
            
            if ohlcv_res.data:
                w52_high = max(row["high"] for row in ohlcv_res.data) * 1000
                w52_low = min(row["low"] for row in ohlcv_res.data) * 1000
                current_price = float(ohlcv_res.data[-1]["close"]) * 1000  # latest close
                if ov["current_price"] and float(ov["current_price"]) > 0:
                    current_price = float(ov["current_price"])

            # 3. Calculate metrics
            ni_key = NET_INCOME_KEYS.get(sector)
            eq_key = EQUITY_KEYS.get(sector)
            
            net_income_ttm = get_net_income_ttm(ticker, ni_key)
            equity = get_latest_financial_value(ticker, eq_key)
            
            # Normalize to absolute VND
            if net_income_ttm and abs(net_income_ttm) < 1e7:
                net_income_ttm *= 1e9
            if equity and abs(equity) < 1e7:
                equity *= 1e9
            
            pe = 0
            pb = 0
            eps_ttm = 0
            
            if market_cap_ty_vnd > 0:
                mc_vnd = market_cap_ty_vnd * 1e9
                if net_income_ttm and net_income_ttm > 0:
                    pe = mc_vnd / net_income_ttm
                if equity and equity > 0:
                    pb = mc_vnd / equity
                    
                if pe != 0 and current_price > 0:
                    eps_ttm = current_price / pe

            # Fallback for PE if negative earnings etc
            pe_val = round(pe, 2) if pe != 0 else None
            pb_val = round(pb, 2) if pb > 0 else None
            eps_val = round(eps_ttm, 0) if eps_ttm != 0 else None
            
            update_data = {
                "week52_high": w52_high,
                "week52_low": w52_low,
                "eps_ttm": eps_val,
                "pe_ratio": pe_val,
                "pb_ratio": pb_val
            }
            if current_price > 0:
                update_data["current_price"] = current_price
            
            print(f"  {ticker} | PE: {pe_val} | PB: {pb_val} | EPS: {eps_val} | 52H: {w52_high} | 52L: {w52_low}")
            
            supabase.table("company_overview").update(update_data).eq("ticker", ticker).execute()
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")

if __name__ == "__main__":
    main()
