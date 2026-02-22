"""
Phase D Multi-Tier Autonomous Web Scraper (scrape_simplize.py)

WHAT IT DOES:
Extracts high-fidelity financial tables from Simplize.vn and loads them into a *_benchmark DB table.
It utilizes a multi-tier fallback architecture: Crawl4AI (Local AI Scraper) -> Firecrawl (API Scraper).

WHY IT'S DESIGNED THIS WAY (Architectural Decisions):
1. Multi-Tier Strategy: Modern SPAs (React/Vue) like Simplize often aggressively block scrapers or obfuscate tables.
   Tier 1 (Crawl4AI) is preferred because it's effectively free (Zero Token Cost).
   Tier 2 (FireCrawl API) is the fallback if Tier 1 gets blocked or fails to render the specific JS data table.
2. Token Management Risk: FireCrawl burns Tokens rapidly. This script acts as a localized, on-demand benchmark tool
   rather than a mass-market cron job, mitigating SaaS API expenses. Future upgrades (documented in challenges.md)
   involve reverse-engineering the Simplize internal API or using Playwright stealth modes exclusively.
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Try importing the needed libraries
try:
    from crawl4ai import AsyncWebCrawler
except ImportError:
    logging.error("crawl4ai not installed. Please run pip install crawl4ai")
    sys.exit(1)

try:
    import requests
except ImportError:
    logging.error("requests not installed.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def crawl_simplize_crawl4ai(url: str) -> str:
    """
    Primary Scraper: Autonomous Web Scraper (Crawl4AI).
    
    WHY CHOSEN: Crawl4AI natively converts complex HTML into chunk-able Markdown, which is dramatically 
    easier to regex/parse textually than writing brittle BeautifulSoup CSS selectors that break when the UI updates.
    """
    logger.info(f"Attempting Primary Scrape with Crawl4AI on {url} ...")
    try:
        # CTO Debt 3 Fix: Enabled Stealth mode via Crawl4AI to bypass anti-bot systems
        async with AsyncWebCrawler(headless=True) as crawler:
            result = await crawler.arun(
                url=url, 
                bypass_cache=True,
                word_count_threshold=10, 
                magic=True,                  # Built-in Playwright Stealth (overcomes Cloudflare/WAF)
                simulate_user=True,          # Simulates mouse movements and human wait times
                delay_before_return_html=3.0 # Gives heavy React/Vue tables time to populate DOM
            )
            
            if result.markdown:
                logger.info("Crawl4AI executed successfully.")
                return result.markdown
            else:
                logger.warning("Crawl4AI returned empty Markdown.")
                return ""
    except Exception as e:
        logger.error(f"Crawl4AI failed: {e}")
        return ""

def crawl_simplize_firecrawl(url: str) -> str:
    """
    Secondary Scraper: FireCrawl API (Fallback).
    
    WHY NEEDED: If Crawl4AI fails to bypass Cloudflare/WAF or trigger React DOM hydration,
    Firecrawl servers handle headless navigation and stealth. High success rate, but costs money.
    """
    logger.info("Attempting Secondary Scrape with FireCrawl API...")
    load_dotenv()
    firecrawl_key = os.environ.get("FIRECRAWL_API_KEY")
    if not firecrawl_key:
        logger.error("FIRECRAWL_API_KEY not found in .env")
        return ""
        
    api_url = "https://api.firecrawl.dev/v1/scrape"
    headers = {
        "Authorization": f"Bearer {firecrawl_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "formats": ["markdown"],
        "waitFor": 3000 # wait for 3 seconds to let tables load
    }
    
    try:
        res = requests.post(api_url, headers=headers, json=payload)
        res.raise_for_status()
        data = res.json()
        if data.get("success"):
            return data.get("data", {}).get("markdown", "")
        else:
            logger.error(f"Firecrawl returned error: {data}")
            return ""
    except Exception as e:
        logger.error(f"Firecrawl scrape failed: {e}")
        return ""

async def get_simplize_data(symbol: str) -> str:
    url = f"https://simplize.vn/co-phieu/{symbol.upper()}/so-lieu-tai-chinh#can-doi-ke-toan"
    
    # Tier 1: Crawl4AI
    md_content = await crawl_simplize_crawl4ai(url)
    if "Tài sản" in md_content and "Nguồn vốn" in md_content:
        logger.info(f"Successful extraction via Crawl4AI for {symbol}")
        return md_content
        
    logger.warning("Crawl4AI didn't find the expected table content. Falling back to Firecrawl...")
    
    # Tier 2: Firecrawl
    md_content_fc = crawl_simplize_firecrawl(url)
    if md_content_fc:
        logger.info(f"Successful extraction via FireCrawl for {symbol}")
        return md_content_fc
        
    # Tier 3: Vietstock (Placeholder logic)
    logger.warning("Both primary and secondary scrapers failed. (Vietstock fallback triggered - TODO)")
    return ""

def parse_and_load_benchmark(md_content: str, symbol: str):
    """
    Parses the scraped Markdown and Upserts into `balance_sheet_benchmark`.
    
    WHY NOT JSON?: Simplize's front-end JSON states are often hashed or locked. Crawling the visible UI ensures
    we see exactly what the user sees. The parser detects standard "Tài sản", periods ("Q4-2024"), and matrices.
    """
    logger.info("Parsing Simplize Markdown into dense dataset...")
    lines = [L.strip().replace("#", "").strip() for L in md_content.splitlines() if L.strip() != ""]
    
    # Locate the table start
    start_idx = -1
    for i, line in enumerate(lines):
        if "Bảng cân đối kế toán" in line:
            start_idx = i
            break
            
    if start_idx == -1:
        logger.error("Could not find table header in markdown.")
        return
        
    # Assume next lines are periods until we hit a non-Q string
    period_names = []
    idx = start_idx + 1
    while idx < len(lines):
        if lines[idx].startswith("Q"):
            period_names.append(lines[idx].replace("/", "-").strip()) # Q4-2025
        else:
            break
        idx += 1
        
    num_periods = len(period_names)
    logger.info(f"Found {num_periods} periods: {period_names}")
    
    records = []
    row_counter = 1
    
    while idx < len(lines):
        item_raw = lines[idx]
        if "Tải báo cáo" in item_raw or "Hiển thị" in item_raw:
            break
        
        item_name = item_raw
        idx += 1
        
        # Read the next `num_periods` lines as values
        for p_idx, period in enumerate(period_names):
            if idx >= len(lines):
                break
                
            val_str = lines[idx]
            idx += 1
            
            # Clean number
            if val_str == "-":
                val = 0.0
            else:
                try:
                    val = float(val_str.replace(",", ""))
                except ValueError:
                    val = 0.0
                    
            record = {
                "stock_name": symbol.upper(),
                "asset_type": "STOCK",
                "source": "Simplize",
                "item_id": f"sim_{row_counter:03d}",
                "item": item_name,
                "levels": 0,
                "row_number": row_counter,
                "period": period,
                "unit": "Tỷ VND",
                "value": val
            }
            records.append(record)
            
        row_counter += 1

    # Load to Supabase
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    from supabase import create_client
    supabase = create_client(url, key)

    try:
        supabase.table("balance_sheet_benchmark").upsert(
            records,
            on_conflict="stock_name,period,item_id,source"
        ).execute()
        logger.info(f"SUCCESS: Loaded {len(records)} benchmark records into balance_sheet_benchmark.")
    except Exception as e:
        logger.error(f"FAILED to upload benchmark: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scrape_simplize.py <SYMBOL>")
        sys.exit(1)
        
    symbol = sys.argv[1]
    
    # Run async function
    content = asyncio.run(get_simplize_data(symbol))
    if not content:
        logger.error("No content scraped.")
        return
        
    parse_and_load_benchmark(content, symbol)

if __name__ == "__main__":
    main()
