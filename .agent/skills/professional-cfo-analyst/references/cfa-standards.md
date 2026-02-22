# CFO & CFA Level 3 Reference Standards

## 1. Accounting Fundamental Hooks (GAAP/IFRS)
- **The Accounting Equation:** `Assets = Liabilities + Shareholders' Equity`
- **Clean Surplus Relationship:** `Retained Earnings (End) = Retained Earnings (Beg) + Net Income - Dividends`
- **Cash Flow Integration:** `Change in Cash (Balance Sheet) = Net Cash from Operating + Investing + Financing Activities`

## 2. Database Schema Rules for Finance
- **Immutability:** Financial ledger entries must be append-only.
- **Precision:** Never use `FLOAT` for financial values. Always use `DECIMAL(19,4)` or integer representations of cents to avoid floating-point arithmetic errors.
- **Auditability:** Every transaction must have `created_at`, `created_by`, and a unique `transaction_id`.

## 3. Financial Visualization UX/UI (IBCS Guidelines)
- **Color Coding:** 
  - Green/Red only for positive/negative variance. 
  - Standard/Actual data: Solid dark grey/black.
  - Budget/Plan data: Outlined (hollow) bars.
  - Forecast: Hatched diagonal lines.
- **Chart Types:**
  - P&L Breakdowns: Waterfall charts.
  - Time-series Trends: Line or column charts.
  - DO NOT use: Pie charts, 3D charts, or unnecessary gauge charts.
- **Scaling:** Charts displaying related metrics must share identical Y-axis scales to prevent visual distortion.
