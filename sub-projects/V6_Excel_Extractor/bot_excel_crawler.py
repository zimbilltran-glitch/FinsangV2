import asyncio
from playwright.async_api import async_playwright
import os

async def download_excel(ticker: str):
    print(f"Bắt đầu tải Excel cho {ticker}...")
    
    # Tạo thư mục tải
    download_dir = os.path.abspath(f"../data/excel_imports/{ticker}")
    os.makedirs(download_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Thiết lập để mô phỏng người dùng thực
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            accept_downloads=True
        )
        
        # Áp dụng Stealth để trách bị phát hiện là Bot
        # Tuy nhiên python-playwright-stealth có thể không chạy tốt trên async, test thử
        try:
            from playwright_stealth import stealth_async
        except ImportError:
            stealth_async = None
            
        page = await context.new_page()
        if stealth_async:
            await stealth_async(page)
            
        print(f"Đang mở trang Tài chính {ticker} trên Vietcap...")
        await page.goto(f"https://trading.vietcap.com.vn/quote/{ticker}/financial-data", wait_until="networkidle")
        
        # Chờ trang load xong Data (có thể có spinner)
        await asyncio.sleep(3)
        
        print("Đang tìm nút Xuất BCTC (Export Excel)...")
        # Nút "Xuất BCTC" trên Vietcap
        export_button = page.locator("button:has-text('Xuất BCTC')").first
        
        if await export_button.count() == 0:
            print("❌ Không tìm thấy nút 'Xuất BCTC'. Cấu trúc website có thể đã thay đổi.")
            await browser.close()
            return

        print("Đã tìm thấy nút Xuất BCTC. Bắt đầu tải...")
        # Lắng nghe sự kiện download
        async with page.expect_download() as download_info:
            await export_button.click()
            
        download = await download_info.value
        
        # Xác định đường dẫn lưu
        file_path = os.path.join(download_dir, f"{ticker}_BCTC_Vietcap.xlsx")
        await download.save_as(file_path)
        print(f"✅ Tải thành công! File lưu tại: {file_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(download_excel("MBB"))
