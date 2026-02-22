import os
import sys
import pandas as pd
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
    from vnstock import Quote, Listing
except ImportError as e:
    print(f"FAILED: Missing dependencies. {e}")
    sys.exit(1)

def main():
    load_dotenv()
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    api_key: str = os.environ.get("VNSTOCK_API_KEY")
    
    if not url or not key:
        print("FAILED: Missing SUPABASE_URL or SUPABASE_KEY in .env")
        sys.exit(1)

    try:
        # 1. Test Supabase Connection
        supabase: Client = create_client(url, key)
        print("SUCCESS: Connected to Supabase!")
        
        # 2. Test VNStock KBS call
        print(f"Testing VNStock with VIP API Key: {api_key is not None}")
        
        # Test listing
        listing = Listing(source="kbs")
        vn30_df = listing.symbols_by_group(group_name="VN30", to_df=True)
        if isinstance(vn30_df, pd.DataFrame) and not vn30_df.empty:
            print(f"SUCCESS: VNStock listing(kbs) is working. Found {len(vn30_df)} VN30 items.")
        else:
            print("WARNING: VNStock listing returned empty data.")
            
        # Test quote
        quote = Quote(source="kbs", symbol="VND")
        quote_df = quote.history(start="2025-01-01", end="2025-01-05", interval="1D", api_key=api_key)
        if quote_df is not None and not quote_df.empty:
            print(f"SUCCESS: VNStock quote(kbs) is working.")
            print(quote_df.head(2))
        else:
            print("WARNING: VNStock quote(kbs) returned empty data.")
            
    except Exception as e:
        print(f"FAILED: Handshake exception - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
