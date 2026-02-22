import sys
import os
import json
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.fetch_financials import extract_kbs

def audit_kbsv_items(symbol: str):
    with open('kbsv_items.txt', 'w', encoding='utf-8') as f:
        f.write("==================================================\n")
        f.write(f"🕵️‍♂️ CFO/CTO GAP ANALYSIS: KBSV vs FIREANT for {symbol}\n")
        f.write("==================================================\n")
        
        reports = ["KQKD", "CDKT", "LCTT"]
        for rep in reports:
            f.write(f"\n--- {rep} ---\n")
            head, items = extract_kbs(symbol, rep, "quarter")
            if not items:
                f.write("FAILED TO FETCH\n")
                continue
                
            f.write(f"Total Items Fetched: {len(items)}\n")
            for i, item in enumerate(items):
                lvl_marker = "-" * item.get('Level', 0) if 'Level' in item else ""
                f.write(f"{i+1:02d} | ReportNormID: {item.get('ReportNormID', 'N/A')} | {lvl_marker} {item.get('Name', 'N/A')}\n")
        
if __name__ == "__main__":
    audit_kbsv_items("NLG")
