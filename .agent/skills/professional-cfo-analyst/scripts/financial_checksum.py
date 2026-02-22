#!/usr/bin/env python3
import argparse
import pandas as pd
import sys

def check_balance_sheet(df, asset_col, liab_col, equity_col, tolerance=0.01):
    """Verifies that Total Assets = Total Liabilities + Total Equity."""
    df['calculated_assets'] = df[liab_col] + df[equity_col]
    df['variance'] = df[asset_col] - df['calculated_assets']
    
    errors = df[df['variance'].abs() > tolerance]
    if not errors.empty:
        print("❌ CRITICAL: Balance Sheet does not balance in the following rows:")
        print(errors[['date', asset_col, liab_col, equity_col, 'variance']])
        return False
    
    print("✅ Balance Sheet checksum passed.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Financial Data Checksum Validator for CFO Agent.")
    parser.add_argument("--input", required=True, help="Path to the financial CSV file.")
    parser.add_argument("--assets", default="Total Assets", help="Column name for Total Assets.")
    parser.add_argument("--liabilities", default="Total Liabilities", help="Column name for Total Liabilities.")
    parser.add_argument("--equity", default="Total Equity", help="Column name for Total Equity.")
    
    args = parser.parse_args()
    
    try:
        df = pd.read_csv(args.input)
        if 'date' not in df.columns:
            print("Warning: No 'date' column found for reference.")
            
        success = check_balance_sheet(df, args.assets, args.liabilities, args.equity)
        if not success:
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"Error: Could not find file {args.input}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing checksum: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
