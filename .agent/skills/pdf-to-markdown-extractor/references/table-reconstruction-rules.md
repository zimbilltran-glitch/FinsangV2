# Table Reconstruction Rules

PDFs often strip logical table structures, leaving only coordinate-based text fragments. Use these heuristic rules when validating and fixing parsed Markdown tables.

## 1. Column Alignment by Bounding Box X0
If the raw output places text from two separate columns onto the same line (or splits them incorrectly into newlines), check the absolute X0 coordinate (left margin).
- Left-aligned text (like labels "Operating Revenue") will have a consistent, low X0.
- Right-aligned text (like currency figures "12,000") will have a high X0 closely clustering towards the right margins of standard page columns.

## 2. Row Fragment Reassembly (The "Spillover" Rule)
In complex financial PDFs, line items with long names often wrap to the next line without associated numbers:
**Raw Appearance:**
```
Loss on disposal of
Property, Plant & Equip     (540)     (200)
```
**Correction Rule:** If a row has text but NO numerical data to its right, and the *next* row begins with text and HAS numerical data... combine the text strings into a single row before processing the numerical values.
**Corrected Markdown:**
```markdown
| Loss on disposal of Property, Plant & Equip | -540 | -200 |
```

## 3. Detecting Implicit Empty Columns
If a PDF table has an empty cell (e.g., no value for a prior year on a specific line item), naive extraction might shift the current year's value into the prior year's column.
**Rule:** Use the gap spacing. If the gap between the label and the first detected number is larger than the standard column width spacing, insert an explicit `null` or empty ` ` into the first numerical column slot.

## 4. Header Detection
Financial table headers generally span multiple lines. Always treat the first 2-3 rows above a solid line rule (or the first rows containing purely date strings like "Dec 31, 2025") as headers, merging them vertically if necessary to form a single header row for the final Markdown table.
