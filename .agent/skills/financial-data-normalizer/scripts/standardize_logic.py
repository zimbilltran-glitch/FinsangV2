#!/usr/bin/env python3
import json
import argparse
import sys

def check_fundamental_equation(data):
    """
    Ensures Assets = Liabilities + Equity with a tiny floating point tolerance.
    Expects data to already be using Standard Keys.
    """
    assets = float(data.get('total_assets', 0))
    liab = float(data.get('total_liabilities', 0))
    equity = float(data.get('total_equity', 0))
    
    variance = abs(assets - (liab + equity))
    
    # Allow small tolerance for rounding artifacts in millions/billions
    if variance > 0.1:  
        return False, f"Equation failed: Assets ({assets}) != Liab ({liab}) + Equity ({equity}). Variance: {variance}"
    return True, "Reconciled"

def compare_sources(source_a, source_b, strict_keys):
    """
    Compares two mapped dictionaries.
    strict_keys defines which keys have a 0.0% variance threshold.
    """
    discrepancies = []
    
    all_keys = set(source_a.keys()).union(set(source_b.keys()))
    
    for key in all_keys:
        val_a = float(source_a.get(key, 0))
        val_b = float(source_b.get(key, 0))
        
        # Avoid division by zero
        if val_a == 0 and val_b == 0:
            continue
            
        difference = abs(val_a - val_b)
        
        # Calculate percentage variance relative to the larger absolute number 
        max_val = max(abs(val_a), abs(val_b))
        pct_variance = (difference / max_val) * 100 if max_val != 0 else 0
        
        if key in strict_keys:
            if difference > 0.1: # absolute difference > 0.1
                discrepancies.append(f"{key}: STRICT threshold failed. A={val_a}, B={val_b}")
        else:
            if pct_variance > 1.0: # generic > 1% threshold for everything else
                 discrepancies.append(f"{key}: 1% threshold failed. Var={pct_variance:.2f}%. A={val_a}, B={val_b}")
                 
    return discrepancies

def main():
    parser = argparse.ArgumentParser(description="Financial Data Normalizer Checksum & Compare Engine")
    parser.add_argument("--action", choices=['checksum', 'compare'], required=True)
    parser.add_argument("--data_a", help="JSON string representing standardized Source A")
    parser.add_argument("--data_b", help="JSON string representing standardized Source B (required for compare)")
    
    args = parser.parse_args()

    # Zero-tolerance keys from thresholds.md
    strict_keys = ['total_assets', 'total_liabilities', 'total_equity', 'net_income']

    if args.action == 'checksum':
        if not args.data_a:
            print("❌ --data_a is required for checksum.", file=sys.stderr)
            sys.exit(1)
            
        try:
            data = json.loads(args.data_a)
            success, msg = check_fundamental_equation(data)
            if success:
                print(f"✅ CHECKSUM PASSED: {msg}")
                sys.exit(0)
            else:
                print(f"❌ CHECKSUM FAILED: {msg}")
                sys.exit(1)
        except json.JSONDecodeError:
            print("❌ Invalid JSON in data_a", file=sys.stderr)
            sys.exit(1)

    elif args.action == 'compare':
        if not args.data_a or not args.data_b:
             print("❌ Both --data_a and --data_b are required for compare.", file=sys.stderr)
             sys.exit(1)
             
        try:
            dict_a = json.loads(args.data_a)
            dict_b = json.loads(args.data_b)
            
            discrepancies = compare_sources(dict_a, dict_b, strict_keys)
            
            if not discrepancies:
                print("✅ SOURCES MATCH within thresholds.")
                sys.exit(0)
            else:
                print("⚠️ DISCREPANCIES DETECTED. TRIGGER SOURCE C:")
                for d in discrepancies:
                    print(f"  - {d}")
                sys.exit(2) # Specific exit code for "needs source c"
                
        except json.JSONDecodeError:
            print("❌ Invalid JSON provided", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
