#!/usr/bin/env python3
import argparse
import sys
import re
import os

try:
    import pdfplumber
except ImportError:
    print("❌ pdfplumber is not installed. Please try: pip install pdfplumber")
    sys.exit(1)

def format_accounting_numbers(text):
    """
    Converts accounting format (1,234.50) to strict negative floats -1234.50
    Removes commas from positive numbers as well.
    """
    if not text:
        return text
    
    # Catch (number) format
    neg_match = re.match(r'^\(([\d,\.]+)\)$', text.strip())
    if neg_match:
        val = neg_match.group(1).replace(',', '')
        return f"-{val}"
    
    # Clean standard numbers
    if re.match(r'^-?[\d,\.]+$', text.strip()):
        return text.strip().replace(',', '')
        
    return text.strip()

def extract_tables_from_pdf(pdf_path, pages=None):
    """
    Extracts tabular data using pdfplumber's built-in table extraction.
    Returns tables as a list of rows represented by markdown-friendly structures.
    """
    output = []
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
        
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            target_pages = [int(p)-1 for p in pages.split(',')] if pages else range(total_pages)
            
            for i in target_pages:
                if i >= total_pages or i < 0:
                    continue
                    
                page = pdf.pages[i]
                tables = page.extract_tables()
                
                if tables:
                    output.append(f"## Page {i+1} Tables")
                    for table_idx, table in enumerate(tables):
                        output.append(f"### Table {table_idx + 1}")
                        for row in table:
                            # Clean and format the cells
                            cleaned_row = [format_accounting_numbers(cell) if cell else "" for cell in row]
                            # Simple markdown table generation string
                            row_str = "| " + " | ".join(cleaned_row) + " |"
                            output.append(row_str)
                        output.append("\n")
                else:
                     output.append(f"## Page {i+1}\nNo tabular structured detected (Possible scanned page). Consider OCR.\n")

    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        sys.exit(1)
        
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="Deterministic PDF Table Extractor")
    parser.add_argument("--input", required=True, help="Path to the source PDF.")
    parser.add_argument("--pages", required=False, help="Comma separated pages to extract (e.g., '1,2,5'). Default is all.")
    parser.add_argument("--ocr", action="store_true", help="Flag to indicate OCR processing is required (placeholder).")
    
    args = parser.parse_args()
    
    if args.ocr:
        # Placeholder for extended OCR logic integrating tools like Tesseract or Marker
        print("⚠️ --ocr flag detected. OCR integration logic will execute here in full implementation.")
        
    result = extract_tables_from_pdf(args.input, args.pages)
    print(result)

if __name__ == "__main__":
    main()
