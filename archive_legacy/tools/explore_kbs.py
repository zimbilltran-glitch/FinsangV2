import requests
import json
import pandas as pd

def get_kbs_financial_report(symbol: str, report_type: str = "KQKD", period: str = "year"):
    url = f"https://kbbuddywts.kbsec.com.vn/sas/kbsv-stock-data-store/stock/finance-info/{symbol.upper()}"
    
    termtype = 1 if period == "year" else 2
    
    params = {
        "page": 1,
        "pageSize": 5,
        "type": report_type,
        "unit": 1000000000,
        "termtype": termtype,
        "languageid": 1
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if "data" in data and "items" in data["data"] and len(data["data"]["items"]) > 0:
            return data["data"]["items"]
        else:
            print(f"No items found for {symbol} {report_type} {period}")
            return None
    else:
        print(f"Error {response.status_code}")
        return None

if __name__ == "__main__":
    items = get_kbs_financial_report("HPG", "KQKD", "year")
    if items:
        print("--- RAW JSON STRUCTURE (First item) ---")
        print(json.dumps(items[0], indent=2, ensure_ascii=False))
        df = pd.DataFrame(items)
        print("\nColumns:", df.columns.tolist())
    
    items_q = get_kbs_financial_report("FPT", "KQKD", "quarter")
    if items_q:
        print("\n--- QUARTER RAW JSON STRUCTURE (First item) ---")
        print(json.dumps(items_q[0], indent=2, ensure_ascii=False))
