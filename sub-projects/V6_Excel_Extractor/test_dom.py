import asyncio
from playwright.async_api import async_playwright
import os

async def check_dom():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://trading.vietcap.com.vn/quote/MBB/financial-data", wait_until="networkidle")
        await asyncio.sleep(5) # Extra wait for React/Vue to mount
        
        # Dump all buttons to see what we have
        buttons = await page.locator("button").all_inner_texts()
        print([b.strip() for b in buttons if b.strip()])
        
        # We can also check svg or other elements if it's an icon button
        print("Checking for export texts...")
        body_text = await page.locator("body").inner_text()
        if "BCTC" in body_text or "Export" in body_text or "Excel" in body_text:
            print("Found export keywords in body!")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_dom())
