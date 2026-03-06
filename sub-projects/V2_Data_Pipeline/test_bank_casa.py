import os, json, requests, logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

SYMBOL = "MBB"
FIREANT_TYPES = {"CDKT": 1, "CSTC": 3} # 1 is balance sheet, 3 is financial ratios? wait, 2 is KQKD, 4 is LCTT

def get_token():
    token = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(user_agent="Mozilla/5.0").new_page()
        def on_req(req):
            nonlocal token
            if not token and "authorization" in req.headers and "Bearer" in req.headers["authorization"]:
                token = req.headers["authorization"]
        page.on("request", on_req)
        try:
            page.goto(f"https://fireant.vn/ma-chung-khoan/{SYMBOL}/tinh-hinh-tai-chinh", wait_until="networkidle", timeout=30000)
        except Exception as e:
            logger.error(f"Playwright error: {e}")
        browser.close()
    return token

def fetch_api(type_id, token):
    url = f"https://restv2.fireant.vn/symbols/{SYMBOL}/full-financial-reports?type={type_id}&year=2024&quarter=4"
    r = requests.get(url, headers={"Authorization": token, "User-Agent": "Mozilla/5.0"}, timeout=20)
    if r.status_code != 200:
        return []
    return r.json()

def main():
    token = get_token()
    if not token:
        print("No token")
        return

    raw_cdkt = fetch_api(1, token)
    for row in raw_cdkt:
        name = str(row.get('name', '')).strip()
        if 'kỳ hạn' in name.lower() or 'khách hàng' in name.lower() or 'thanh toán' in name.lower() or 'casa' in name.lower():
            vals = row.get('values', [])
            val_2024 = [v for v in vals if v.get('year') == 2024 and v.get('quarter') == 4]
            latest_val = val_2024[0]['value'] if val_2024 else None
            print(f"CDKT: {name} => {latest_val}")

    url_ind = f"https://restv2.fireant.vn/symbols/{SYMBOL}/financial-indicators"
    r = requests.get(url_ind, headers={"Authorization": token, "User-Agent": "Mozilla/5.0"})
    if r.status_code == 200:
        for row in r.json():
            name = str(row.get('name', '')).strip()
            if 'casa' in name.lower():
                print(f"INDICATOR: {name} => {row.get('value')}")

if __name__ == "__main__":
    main()
