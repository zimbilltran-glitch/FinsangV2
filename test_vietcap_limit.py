import requests

ticker = "FPT"
section = "BALANCE_SHEET"

urls = [
    f"https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{ticker}/financial-statement?section={section}",
    f"https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{ticker}/financial-statement?section={section}&limit=40",
    f"https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{ticker}/financial-statement?section={section}&size=40",
    f"https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{ticker}/financial-statement?section={section}&period=10",
]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://trading.vietcap.com.vn/",
    "Origin": "https://trading.vietcap.com.vn",
}

for u in urls:
    r = requests.get(u, headers=headers)
    d = r.json().get("data", {})
    qs = d.get('quarters', [])
    print(u.split("?")[-1], "->", len(qs), "quarters")
