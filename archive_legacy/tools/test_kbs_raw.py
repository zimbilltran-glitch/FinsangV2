import json
import requests

def test_kbs(symbol: str, report_type: str, termtype: int):
    url = f"https://kbbuddywts.kbsec.com.vn/sas/kbsv-stock-data-store/stock/finance-info/{symbol.upper()}"
    params = {
        "page": 1,
        "pageSize": 8,
        "type": report_type,
        "termtype": termtype,
        "unit": 1000000000,
        "languageid": 1
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    with open("tools/kbs_response.json", "w", encoding="utf-8") as f:
         json.dump(response.json(), f, ensure_ascii=False, indent=2)
    print(f"Status: {response.status_code}. Response written to kbs_response.json")

if __name__ == "__main__":
    test_kbs("VND", "KQKD", 2)
