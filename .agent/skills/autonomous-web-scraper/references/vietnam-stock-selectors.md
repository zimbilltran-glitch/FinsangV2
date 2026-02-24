# Vietnam Stock Data Extract Selectors

## 1. CafeF (cafef.vn)
CafeF contains heavily structured financial tables. Use these selectors to target the core financial reports.

### Bảng cân đối kế toán (Balance Sheet) & Báo cáo kết quả kinh doanh (P&L)
```css
/* Main Data Table */
.table-finance
#tableContent
.cf_table_finance

/* Download Excel Link */
#download-excel-btn
.btn-download-excel
```

### Crawl Instructions for CafeF
- Set `wait_for` parameter to ensure the table is fully loaded before extraction. Example: `wait_for=".table-finance"`

## 2. Vietstock (vietstock.vn)
Vietstock relies extensively on Ajax loading. Explicit wait times and execution instructions are necessary.

### Financial Ratios & Historical Price Tables
```css
/* Financial Ratios Table */
#financial-ratio-table
.table-ratio

/* Historical Prices */
#stock-historical-data
.table-historical
```

### Crawl Instructions for Vietstock
- Due to Ajax loading, set `wait_for` condition heavily. Example: `wait_for="#financial-ratio-table"`
- Consider using an explicit sleep or scrolling execution script if data is paginated:
```python
js_code = "window.scrollTo(0, document.body.scrollHeight);"
```

## 3. General Patterns (Vietnamese IR Pages)
When encountering generic corporate Investor Relations (IR) pages in Vietnam, these standard selectors often match core financial tables.

### Common Identifiers
```css
/* General Data Tables */
.table-responsive
table.data-table
.financial-reports-list

/* Common Download Buttons */
.download-pdf
.btn-export-excel
```

## Integration with SKILL.md
To effectively utilize these selectors, amend the `SKILL.md` Fetch step to conditionally load these specific selectors.
Example Amendment:
- Step 2 Fetch: Execute `python scripts/crawl_engine.py url`. If the url is CafeF or Vietstock, apply the CSS and wait conditions listed in `references/vietnam-stock-selectors.md`.

## Performance Notes
Take your time to verify that these selectors are robust against common website layout shifts. Quality of the data bridge is critical for the Finsang project.
