# Financial Variance Thresholds

When performing Triangulation (Triple-Source Verification), use these thresholds to determine if a discrepancy exists and requires escalation to Source C (The Official Source).

## 1. Zero-Tolerance Thresholds (0.0% Variance Allowed)
These metrics form the fundamental accounting equation. ANY variance between sources instantly triggers Source C verification and signals potential data corruption.
- `total_assets`
- `total_liabilities`
- `total_equity`
- `net_income` (Must match the clean surplus calculation and the bottom line of the P&L)

## 2. Low-Tolerance Thresholds (< 0.5% Variance Allowed)
These are primary aggregations that are rarely restated without a formal 8-K / IR announcement. Discrepancies here usually mean one aggregator (CafeF/Vietstock) missed a minor line-item reclassification.
- `total_revenue`
- `operating_income`
- `operating_cash_flow`

## 3. Moderate-Tolerance Thresholds (< 2.0% Variance Allowed)
Aggregators frequently classify these sub-items differently (e.g., placing a specific tax or lease in SG&A vs COGS). If the variance is under 2%, the script can average the two (or accept Source A) WITHOUT triggering Source C, provided the parent categories (Gross Profit or Operating Income) still reconcile perfectly. 
- `cogs`
- `operating_expenses` (SG&A, R&D)
- Individual current asset/liability line items (e.g., `inventory`, `accounts_receivable`)

## Conflict Resolution Rules
If a discrepancy exceeds the threshold for a specific category:
1. Fetch Source C (The company's official filing on HNX/HOSE/IR Site).
2. If Source C matches Source A, accept Source A.
3. If Source C matches Source B, accept Source B.
4. If Source C is completely different, accept Source C (Weighted Truth Principle).
5. If Source C cannot be acquired or contradicts the fundamental accounting equation, flag the specific line item as `[UNRELIABLE]` in the output payload.
