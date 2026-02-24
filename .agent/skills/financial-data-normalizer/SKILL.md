---
name: financial-data-normalizer
description: >
  Standardizes inconsistent financial terminology and formats into a universal schema. Performs triple-source cross-referencing to ensure data integrity. Use when raw scraped data needs cleaning or validation before CFO auditing.
license: MIT
compatibility: antigravity, claude-api
metadata:
  author: finsang-project
  version: 1.0.0
  category: data-pipeline
---

# Financial Data Normalizer

## Goal
Act as a deterministic middleware bridge between raw web scrapers (like `autonomous-web-scraper`) and the `professional-cfo-analyst` skill. This skill maps inconsistent Vietnamese financial terminology into a single universal schema and enforces a strict triple-source verification protocol to guarantee data integrity before analysis.

## When to Use This Skill
- Raw scraped financial data needs to be cleaned, localized, or mapped to standard English/universal terms.
- There is a need to verify financial data scraped from different sources (e.g., CafeF vs Vietstock).
- **Negative Trigger:** Do NOT use this skill for actual financial analysis or CFO advice; use `professional-cfo-analyst` for that *after* normalization.

## Workflow
- [ ] **Step 1 – Mapping:** Accept raw data (Markdown/CSV/JSON). Convert all raw terminology into the standard keys defined in `references/universal-mapping.md`.
- [ ] **Step 2 – Base Checksum & Validation:** Run `python scripts/standardize_logic.py --action checksum` to evaluate if the basic accounting equation balances (Assets = Liabilities + Equity) on the primary source.
- [ ] **Step 3 – Triple-Source Coordination:**
    - Compare **Source A** (e.g., CafeF) against **Source B** (e.g., Vietstock).
    - If a discrepancy exceeds the variance defined in `references/thresholds.md` (e.g., > 1%), trigger `autonomous-web-scraper` to fetch **Source C** (Official IR page or HNX/HOSE filing).
- [ ] **Step 4 – Resolution & Output:** 
    - Apply Weighted Truth: Prioritize Source C (Official source) in case of conflict.
    - If the accounting equation now balances with the unified data, output the "**Cleaned Payload**".

## Rules & Constraints
- **Universal Schema Only:** Do not pass unmapped, raw Vietnamese terminology to the CFO skill. Translate everything to the universal schema keys first.
- **Strict Verification:** You must not skip Step 3 if Source A and Source B fail to match within the defined threshold.
- **Data Integrity Over Everything:** If the cleaned payload still fails the fundamental accounting equations (Step 2), it is invalid data.

## Error Handling
- **Unreliable Data:** If all three sources conflict beyond the designated threshold and no clear 'Weighted Truth' emerges, mark the dataset as "Unreliable Data" and halt the pipeline. Do NOT pass to the CFO skill.
- **Missing Mapping:** If a raw key is not found in `universal-mapping.md`, flag it as an "Unknown Key" in the output payload and do not guess its category. Ask the user for clarification.

## Examples
**Example 1: Discrepancy Resolution**
User: "Here is Apple's Q3 data from Source A and Source B. Normalize it."
Actions:
1. Map "Doanh thu thuần" (Source A) and "Net Revenue" (Source B) to `total_revenue`.
2. Detect that `total_revenue` differs by 2.5% (> 1% threshold).
3. Invoke `autonomous-web-scraper` to fetch Source C (Official 10-Q filing).
4. Resolve using Source C and output the Cleaned Payload.

## References
- Terminology Dictionary: `references/universal-mapping.md`
- Variance Limits: `references/thresholds.md`
- Core Verification Engine: `scripts/standardize_logic.py --help`

## Performance Notes
Take your time. Code is deterministic; language interpretation isn't. Quality of the data bridge is the foundation of Finsang's integrity. Do not skip the third-source verification if discrepancies exist.
