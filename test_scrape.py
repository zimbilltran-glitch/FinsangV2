import asyncio
from playwright.async_api import async_playwright
try:
    from playwright_stealth import stealth_async
except:
    stealth_async = None

async def extract():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        c = await b.new_context(viewport={'width': 1920, 'height': 1080})
        page = await c.new_page()
        if stealth_async: await stealth_async(page)
        
        await page.goto('https://trading.vietcap.com.vn/iq/company?ticker=MBB&tab=financial&isIndex=false&financialTab=financialStatement', wait_until='networkidle')
        await asyncio.sleep(8)
        
        # Click Quý -> Năm
        try:
            nam_btn = page.locator("button:has-text('Năm')").first
            await nam_btn.click()
            await asyncio.sleep(2)
        except Exception as e:
            pass

        # Parse tabular data
        text = await page.evaluate('''() => {
            let res = "";
            document.querySelectorAll("tr").forEach(row => {
               let rText = [];
               row.querySelectorAll("th, td").forEach(col => rText.push(col.innerText.trim()));
               if(rText.length > 0) res += rText.join(" | ") + "\\n";
            });
            return res;
        }''')
        
        with open('mbb_table.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        print('Saved table out')
        await b.close()

if __name__ == "__main__":
    asyncio.run(extract())
