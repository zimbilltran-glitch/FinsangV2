# Crawl Configurations & Advanced Usage

## Introduction
The `crawl4ai` framework used in the Autonomous Web Scraper supports numerous advanced configurations. For complex scraping scenarios involving anti-bot mechanisms, authentication, or heavy JS frameworks (React, Vue, etc.), the base script may need to be modified or extended.

## CSS Selectors and JS Execution
- To extract specific elements, use the `css_selector` parameter in the `arun` call:
  ```python
  result = await crawler.arun(url="...", css_selector=".main-article-content")
  ```
- To execute custom JS before extraction (e.g., clicking a "Load More" button):
  ```python
  js_code = "document.querySelector('.load-more-btn').click();"
  result = await crawler.arun(url="...", js=js_code)
  ```

## Session Management & Authentication
- Maintain state across multiple requests (e.g., login flows) by passing a `session_id`.
  ```python
  result = await crawler.arun(url="...", session_id="user_session_123")
  ```
- Pass authentication cookies or localstorage tokens using the `cookies` or `local_storage` parameters if bypassing login pages.

## Anti-Bot By-pass Strategies
- If encountering 403 Forbidden or captchas, toggle headless mode off (if running locally) or cycle user-agent strings.
- Incorporate explicit wait times using `wait_for` string parameters (e.g., waiting for a specific CSS element to become visible).
