import os, sys, time
from playwright.sync_api import sync_playwright

def download_excel(ticker):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(accept_downloads=True, user_agent="Mozilla/5.0")
        page = ctx.new_page()
        
        # Navigate to a general page to get token if needed, or go direct
        page.goto("https://trading.vietcap.com.vn/")
        
        # We need to know the exact URL to download the excel file in Vietcap
        # Let's intercept requests to see the URL when we manually click export.
        # Wait, since we cannot manually click, I will try hitting the export API with the token.
        token = None
        def on_req(req):
            nonlocal token
            if not token and "authorization" in req.headers and "Bearer" in req.headers["authorization"]:
                token = req.headers["authorization"]
                
        page.on("request", on_req)
        
        # Go to MBB financial page
        try:
            page.goto(f"https://trading.vietcap.com.vn/quote/{ticker}/financial-data", wait_until="networkidle", timeout=20000)
        except Exception as e:
            print(f"Network idle timeout: {e}")
            
        if not token:
            print("No token captured")
            browser.close()
            return
            
        print(f"Captured token: {token[:20]}...")
        import requests
        headers = {
            "Authorization": token,
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://trading.vietcap.com.vn/",
            "Origin": "https://trading.vietcap.com.vn",
        }
        
        # Try both IQ and normal API.
        # Export url might be like: 
        # https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/MBB/financial-statement/export
        url = f"https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{ticker}/financial-statement/export?lang=vi"
        r = requests.get(url, headers=headers, stream=True)
        print(f"Export API status: {r.status_code}")
        if r.status_code == 200:
            with open(f"{ticker}_export.xlsx", "wb") as f:
                f.write(r.content)
            print("Downloaded!")
        else:
            print(r.text[:500])
            
        browser.close()

if __name__ == "__main__":
    download_excel("MBB")
