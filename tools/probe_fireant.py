# tools/probe_fireant.py
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def sniff_fireant_api(symbol: str):
    logger.info(f"Sniffing Fireant API for {symbol}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        api_data = {}

        def handle_response(response):
            # Only intercept JSON responses to filter out images/css
            if response.request.resource_type in ["xhr", "fetch"]:
                try:
                    data = response.json()
                    api_data[response.url] = data
                except Exception:
                    pass

        def handle_request(request):
            # Try to snatch the Bearer token from any fireant API call
            headers = request.headers
            if "authorization" in headers and "Bearer" in headers["authorization"]:
                api_data["TOKEN"] = headers["authorization"]
                logger.info(f"Yess! Snapped Bearer Token: {headers['authorization'][:20]}...")

        page.on("request", handle_request)
        page.on("response", handle_response)
        
        # Go straight to the financial reports page
        target_url = f"https://fireant.vn/ma-chung-khoan/{symbol}/tinh-hinh-tai-chinh"
        logger.info(f"Navigating to {target_url}...")
        page.goto(target_url, wait_until="networkidle", timeout=60000)
        
        # Click on 'Báo cáo tài chính' if it exists, or directly 'Lưu chuyển tiền tệ'
        try:
            logger.info("Clicking on 'Báo cáo tài chính'...")
            page.locator("text=Báo cáo tài chính").nth(0).click(timeout=5000)
            page.wait_for_timeout(2000)
        except Exception:
            pass
            
        try:
            logger.info("Clicking on 'Lưu chuyển tiền tệ' (Trực Tiếp)...")
            page.locator("text=Lưu chuyển tiền tệ").nth(0).click(timeout=5000)
            page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Could not click 'Lưu chuyển tiền tệ': {e}")
            
        try:
            logger.info("Clicking on 'Gián tiếp' tab inside Lưu chuyển...")
            page.locator("text=Gián tiếp").nth(0).click(timeout=5000)
            page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Could not click 'Gián tiếp': {e}")

        # Print some snippet of the captured data
        logger.info(f"Captured {len(api_data)} API responses.")
        with open("fireant_network.json", "w", encoding="utf-8") as f:
            json.dump(api_data, f, ensure_ascii=False, indent=2)
        logger.info("Saved all intercepted network data to fireant_network.json")

        browser.close()

if __name__ == "__main__":
    import sys
    sym = sys.argv[1] if len(sys.argv) > 1 else 'NLG'
    sniff_fireant_api(sym)
