import os
import sys
import asyncio
from dotenv import load_dotenv
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from crawl4ai import AsyncWebCrawler

async def main():
    print("Scraping Fireant NLG for COA Structure...")
    url = "https://fireant.vn/ma-chung-khoan/NLG"
    
    # We want to use stealth mode if possible
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url=url,
            magic=True,
            simulate_user=True,
            delay_before_return_html=5.0
        )
        
        if result.success:
            print("Successfully fetched Fireant HTML.")
            with open("fireant_raw.md", "w", encoding="utf-8") as f:
                f.write(result.markdown)
            print("Saved to fireant_raw.md")
        else:
            print(f"Failed to fetch. Error: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
