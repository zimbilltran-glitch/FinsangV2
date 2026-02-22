#!/usr/bin/env python3
import asyncio
import argparse
import sys

# Ensure crawl4ai is installed: pip install crawl4ai
from crawl4ai import AsyncWebCrawler

async def arun(url: str):
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url=url,
            word_count_threshold=10,
            remove_overlay_elements=True,
            bypass_cache=True
        )
        if result.success:
            return result.markdown
        else:
            raise Exception(f"Failed to crawl {url}: {result.error_message}")

def main():
    parser = argparse.ArgumentParser(description="Async Web Scraper using Crawl4AI.")
    parser.add_argument("url", help="The URL to scrape.")
    args = parser.parse_args()

    try:
        markdown_result = asyncio.run(arun(args.url))
        print(markdown_result)
    except Exception as e:
        print(f"Error scraping url: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
