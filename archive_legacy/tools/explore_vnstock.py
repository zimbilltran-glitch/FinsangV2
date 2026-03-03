import os
from dotenv import load_dotenv
import pandas as pd
from vnstock import FinancialReport

def test_vnstock_financials():
    load_dotenv()
    api_key = os.environ.get("VNSTOCK_API_KEY")
    
    print("Testing vnstock FinancialReport (KBS source)...")
    try:
        # report_type: IncomeStatement, BalanceSheet, CashFlow
        report = FinancialReport(source="kbs", symbol="HPG")
        
        # income_statement
        df = report.income_statement(period="quarter", api_key=api_key)
        
        if df is not None and not df.empty:
            print("\nSUCCESS! Got Dataframe. Columns:")
            print(df.columns.tolist())
            print("\nFirst 3 rows:")
            print(df.head(3))
        else:
            print("WARNING: df is empty or None")
    except Exception as e:
        print(f"FAILED: error: {e}")

if __name__ == "__main__":
    test_vnstock_financials()
