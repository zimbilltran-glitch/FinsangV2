---
name: pdf-to-markdown-extractor
description: >
  Extracts and converts complex PDF financial statements into structured Markdown. Handles multi-column layouts, nested tables, and scanned documents. Use when the user uploads a .pdf file or provides a link to a PDF report.
license: MIT
compatibility: antigravity, claude-api
metadata:
  author: finsang-project
  version: 1.0.0
  category: extraction
---

# PDF to Markdown Extractor

## Goal
Extract high-fidelity structured data from complex financial PDF reports. Convert multi-column layouts, fragmented tables, and scanned documents into clean, LLM-ready Markdown that perfectly aligns with the `financial-data-normalizer` schema expectations.

## When to Use This Skill
- User uploads or shares a `.pdf` file containing financial reports, disclosures, or data.
- User requests text/table extraction from a PDF link.
- **Negative Trigger:** Do NOT use this skill for simple raw text extraction of non-financial linear documents where basic PDF readers suffice.

## Workflow (Iterative Refinement)

- [ ] **Step 1 – Parsing:** Execute `python scripts/pdf_engine.py --input <path_to_pdf>` to perform the initial coordinate-based extraction using `pdfplumber` (or similar).
- [ ] **Step 2 – OCR Fallback Validation:** If the parsed text is extremely sparse or missing entirely, the PDF is likely scanned. Trigger an OCR-enhanced extraction path (e.g., passing `--ocr` flag if implemented or instructing the agent to utilize optical tools) to extract image-based text. Store intermediate image crops in `assets/`.
- [ ] **Step 3 – Structural Validation:** Review the extracted Markdown tables. Verify that the tables maintain a consistent number of columns per row. Broken rows or misaligned headers must be detected here. Cross-reference alignment using `references/table-reconstruction-rules.md`.
- [ ] **Step 4 – Fix Alignment & Formatting:** 
    - Reassemble fragmented tables based on positional logic.
    - **CRITICAL FORMATTING INSTRUCTION:** Ensure financial figures enclosed in parentheses (e.g., `(1,234)`) are correctly converted to negative numbers without commas (e.g., `-1234`) in the Markdown output. Normalize all currency representation.
- [ ] **Step 5 – Finalize & Output:** Deliver clean, structured Markdown that is ready to be consumed by the `financial-data-normalizer` skill.

## Rules & Constraints
- **Table Integrity is Paramount:** Never hallucinate missing table cells to make a table fit. If a table column is missing, insert blank space or 'N/A' correctly corresponding to the headers.
- **Negative Number Conversion:** You MUST convert accounting negation `(X)` into mathematical negation `-X`.

## Error Handling
- **Password Protected PDF:** Prompt user for the password; do not attempt to brute force.
- **Misaligned Table Data:** Halt extraction and apply the reconstruction logic from `references/table-reconstruction-rules.md`. Do not pass garbage alignment to the next pipeline step.

## Examples
**Example 1: Parsing Nested Financial Table**
User: "Extract the Balance Sheet from this annual_report.pdf"
Actions:
1. Run parsing script constraint to the Balance Sheet pages.
2. Validate the row and column structures.
3. Detect "(5,400)" under "Net Cash Flow". Convert to "-5400".
4. Finalize the Markdown and output.

## References
- Table Parsing Logic & Re-assembly: `references/table-reconstruction-rules.md`
- PDF Parsing Core Script: `scripts/pdf_engine.py --help`

## Performance Notes
Take your time. Financial tables are fragile. Accuracy in row-column alignment is more important than speed. Do not skip any pages in the report.
