import json
import math
import os
import sys
import asyncio
from pathlib import Path
import pandas as pd
import requests

# Set path to allow importing from V6
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT / "sub-projects" / "V6_Excel_Extractor"))
from bot_excel_crawler import download_excel

SCHEMA_PATH = ROOT / "sub-projects" / "V9_Hybrid_Sentinel" / "golden_schema_v9.json"
EXCEL_DIR = ROOT / "data" / "excel_imports"

# Map sections between API and Excel
SECTIONS = {
    "BALANCE_SHEET": "Balance Sheet",
    "INCOME_STATEMENT": "Income Statement",
    "CASH_FLOW": "Cash Flow"
}

# Sector Schema mapping
SECTOR_MAP = {
    "normal": {
        "BALANCE_SHEET": "CDKT",
        "INCOME_STATEMENT": "KQKD",
        "CASH_FLOW": "LCTT"
    },
    "bank": {
        "BALANCE_SHEET": "CDKT_BANK",
        "INCOME_STATEMENT": "KQKD_BANK",
        "CASH_FLOW": "LCTT_BANK"
    },
    "sec": {
        "BALANCE_SHEET": "CDKT_SEC",
        "INCOME_STATEMENT": "KQKD_SEC",
        "CASH_FLOW": "LCTT_SEC"
    }
}

async def ensure_excel(ticker: str):
    file_path = EXCEL_DIR / f"{ticker}_BCTC_Vietcap.xlsx"
    if not file_path.exists():
        print(f"[{ticker}] File Excel không tồn tại. Đang tải xuống (Playwright)...")
        await download_excel(ticker, headless=True)
    return file_path

def fetch_api_2024(ticker: str, section: str):
    url = f"https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{ticker}/financial-statement?section={section}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://trading.vietcap.com.vn",
        "Referer": "https://trading.vietcap.com.vn/"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        d = r.json()
        api_values = {}
        if d.get("successful") and d.get("data") and d["data"].get("years"):
            for row in d["data"]["years"]:
                # API uses yearReport
                if str(row.get("yearReport")) == "2024":
                    for k, v in row.items():
                        if isinstance(v, (int, float)):
                            api_values[k] = v
            return api_values
    except Exception as e:
        print(f"[{ticker} - {section}] Lỗi gọi API: {e}")
    return {}

def run_sentinel_single(ticker: str, sector: str):
    print(f"\n🚀 Khởi chạy Sentinel Worker cho [{ticker}] - Sector: {sector}")
    
    # 1. Download Excel
    excel_path = asyncio.run(ensure_excel(ticker))
    if not excel_path.exists():
        print(f"❌ [{ticker}] Không thể tải Excel Ground Truth. Bỏ qua.")
        return

    # 2. Load schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = json.load(f)

    updates = 0

    # 3. Process each section (CDKT, KQKD, LCTT)
    for api_section, excel_sheet in SECTIONS.items():
        schema_sheet_id = SECTOR_MAP[sector][api_section]
        
        # Load API data
        api_values = fetch_api_2024(ticker, api_section)
        if not api_values:
            print(f"[{ticker}] Không có data API 2024 cho {api_section}.")
            continue
            
        # Load Excel data (skip first 10 meta rows normally applied for Vietcap Excel)
        try:
            df = pd.read_excel(excel_path, sheet_name=excel_sheet, skiprows=10)
            col_2024 = [c for c in df.columns if str(c) == "2024"][0]
        except Exception as e:
            print(f"[{ticker}] Lỗi đọc Excel {excel_sheet}: {e}")
            continue

        # Build Excel Name -> Value mapping
        excel_map = {}
        for _, row in df.iterrows():
            name = str(row.iloc[0]).strip().lower()
            if name == "nan": continue
            val = row[col_2024]
            if pd.isna(val): continue
            excel_map[name] = val

        print(f"[{ticker}] Đã đọc {len(excel_map)} dòng từ Excel ({excel_sheet}).")

        # Map Excel -> API -> Schema
        for fld in schema["fields"]:
            if fld["sheet"] == schema_sheet_id:
                name_clean = fld["vn_name"].strip().lower()
                ex_val = None
                
                # Fuzzy/Exact Match in Excel
                if name_clean in excel_map:
                    ex_val = excel_map[name_clean]
                else:
                    for k, v in excel_map.items():
                        if name_clean in k or k in name_clean:
                            ex_val = v
                            break
                            
                if ex_val is not None:
                    # Ignore values near zero (to prevent matching random 0.0 shadow keys)
                    if abs(ex_val) < 1.0: 
                        continue
                        
                    # Find matching keys in API
                    # API values might be in actual units, Excel is usually in Billion VND. 
                    # Need to check both 1x and 1e9x scalings.
                    matches = []
                    for ak, av in api_values.items():
                        if abs(av - ex_val) < 1.0 or abs(av - (ex_val * 1e9)) < 1.0:
                            matches.append(ak)
                    
                    # Resolve overlapping bsa/isb/cfb
                    if len(matches) > 1:
                        prefix_hint = "bs" if api_section == "BALANCE_SHEET" else "is" if api_section == "INCOME_STATEMENT" else "cf"
                        # Sector specific priority: bank -> bsb/isb/cfb, sec -> bss/iss/cfs, normal -> bsa/isa/cfa
                        sec_char = 'b' if sector == 'bank' else 's' if sector == 'sec' else 'a'
                        target_prefix = f"{prefix_hint}{sec_char}"
                        
                        specific = [m for m in matches if m.startswith(target_prefix)]
                        if specific:
                            matches = specific

                    if matches:
                        best_match = matches[0]
                        # Verify against shadow keys (ignore 0.0 mapping bugs)
                        # Ensure vietnam_key structure exists
                        if "vietcap_key" not in fld:
                            fld["vietcap_key"] = {}
                        if not isinstance(fld["vietcap_key"], dict):
                            # Convert legacy string to dict
                            old_val = fld["vietcap_key"]
                            fld["vietcap_key"] = {"normal": old_val}
                            
                        old_key = fld["vietcap_key"].get(sector)
                        if old_key != best_match:
                            print(f"  ✅ [Map] {fld['vn_name'][:40]:<40} : {old_key} -> {best_match}")
                            fld["vietcap_key"][sector] = best_match
                            updates += 1

    if updates > 0:
        with open(SCHEMA_PATH, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
        print(f"[{ticker}] Đã cập nhật {updates} keys vào schema.")
    else:
        print(f"[{ticker}] Cấu trúc đã chuẩn xác. Không cần cập nhật.")

if __name__ == "__main__":
    sample_targets = {
        "FPT": "normal",
        "VNM": "normal",
        "MBB": "bank",
        "VCB": "bank",
        "SSI": "sec",
        "VND": "sec"
    }
    
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", help="Specific ticker to run")
    ap.add_argument("--sector", help="Specific sector: normal, bank, sec")
    args = ap.parse_args()

    if args.ticker and args.sector:
        run_sentinel_single(args.ticker, args.sector)
    else:
        print("Bắt đầu quy trình Sentinel Auto-Mapping (6 Sample Tickers)...")
        for tkr, sec in sample_targets.items():
            run_sentinel_single(tkr, sec)
