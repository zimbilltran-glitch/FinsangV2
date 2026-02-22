---
name: autonomous-web-scraper
description: >
  Crawls websites using Crawl4AI to extract clean, LLM-ready Markdown. Use when the user provides a URL or asks to 'fetch', 'scrape', or 'research' content from a live webpage. Supports dynamic JS rendering.
license: MIT
compatibility: antigravity, claude-api
metadata:
  author: antigravity-user
  version: 1.0.0
  category: scraping
---

# Autonomous Web Scraper

## Goal
Extract clean, well-structured, LLM-ready Markdown content from live webpages using the Crawl4AI framework, handling dynamic JavaScript rendering effectively.

## When to Use This Skill
- User provides a URL and asks you to read or scrape its content.
- User asks to "fetch", "scrape", or "research" information from a specific live website.
- **Negative Trigger:** Do NOT use for querying internal databases or accessing local file systems unless specifically provided as a local file URL that needs browser rendering.

## Workflow
- [ ] **Step 1 – Init:** Check if the target website heavily relies on dynamic content/JavaScript tags. Prepare an intermediate `.tmp/` directory for data storage if caching or multiple pages are needed.
- [ ] **Step 2 – Fetch:** Execute `python scripts/crawl_engine.py <URL>` to perform the actual crawl. Determine if any advanced configuration from `references/crawl-configurations.md` is needed (e.g., CSS selectors, wait-for conditions).
- [ ] **Step 3 – Clean:** Review the returned Markdown output. Ensure that irrelevant overlay elements have been removed and the text is clean.
- [ ] **Step 4 – Output:** Present the synthesized, clean Markdown to the user or use it to answer the user's specific research question.

## Rules & Constraints
- Always use the provided `scripts/crawl_engine.py` as it sets strict word count thresholds and overlay removal.
- Store any intermediate or large raw data dumps in the `.tmp/` directory to avoid cluttering the workspace.
- Do NOT hallucinate website content if the scrape fails. Clearly report the failure instead.

## Error Handling
- **Timeout/Blocked:** If the site blocks the crawler or times out, suggest using headless configurations outlined in `references/crawl-configurations.md`.
- **Empty Output:** Double-check if the page requires specific JS execution or an explicit wait condition.

## References
- Advanced Crawl Configurations: `references/crawl-configurations.md`
- Core Scraper Script: `scripts/crawl_engine.py --help`

## Performance Notes
Take your time to ensure the Markdown table structures are preserved. Data accuracy is critical for financial analysis. Do not skip validation.
