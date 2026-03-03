"""
Phase A Data Extraction Pipeline (fetch_ohlcv.py)

WHAT IT DOES:
Extracts historical stock price data (Open, High, Low, Close, Volume) using the `vnstock` library,
formats the dates to be compatible with PostgreSQL TIMESTAMPTZ, and upserts it into the `stock_ohlcv` Supabase table.

WHY IT'S DESIGNED THIS WAY (Architectural Decisions):
1. Relying on vnstock Quote: Unlike Financial Reports which are unstable in vnstock, the `Quote` module wrapping KBSV
   is stable and allows injecting a VIP `api_key`. This avoids rate-limiting while pulling massive historical price datasets.
2. Timezone Standardization: Financial time-series data MUST be heavily standardized. We force the timestamp to contain
   a timezone offset (e.g., 'Z' or '+07:00') before pushing to Supabase so that Metabase/Supabase doesn't skew daily candles
   due to server-vs-local timezone mismatch.
3. Idempotent Upserts: The composite key `(stock_name, time)` ensures we can safely re-run scripts without duplicating history.
"""
import os
import sys
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

try:
    from vnstock import Quote
    from supabase import create_client, Client
except ImportError as e:
    print(f"FAILED: Missing dependencies. {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".tmp")

def extract_ohlcv(symbol: str, start_date: str, end_date: str, interval: str = "1D") -> pd.DataFrame:
    """
    Extract OHLCV data using vnstock's Quote module.
    
    WHY THIS SOURCE: KBSV's endpoint for technical data is extremely robust when an API key is provided,
    effectively eliminating pagination and rate-limit issues common in scraping.
    """
    logger.info(f"Extracting OHLCV for {symbol} from {start_date} to {end_date} (interval: {interval})")
    
    api_key = os.environ.get("VNSTOCK_API_KEY")
    if not api_key:
        logger.warning("VNSTOCK_API_KEY is not set. May hit rate limits.")
        
    try:
        quote = Quote(source="kbs", symbol=symbol)
        df = quote.history(start=start_date, end=end_date, interval=interval, api_key=api_key)
        return df if df is not None else pd.DataFrame()
    except Exception as e:
        logger.error(f"Extract failed: {e}")
        return pd.DataFrame()

def transform_ohlcv(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """
    Format DataFrame for Supabase ingestion.
    
    WHY: Converts raw dates to ISO8601 strings with explicit timezones. Postgres requires clear Timestamps
    to prevent "drift" when graphing OHLCV on frontend libraries (like TradingView Lightweight Charts).
    """
    logger.info("Transforming Data...")
    if df.empty:
        return df
        
    # The dataframe from vnstock usually has columns: time, open, high, low, close, volume (all lowercase)
    # Ensure columns match Supabase schema
    expected_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
    
    if 'date' in df.columns and 'time' not in df.columns:
        df = df.rename(columns={'date': 'time'})
        
    for col in expected_cols:
        if col not in df.columns:
            logger.error(f"Missing expected column '{col}' in DataFrame")
            return pd.DataFrame()
            
    # Add stock_name and asset_type columns
    df['stock_name'] = symbol.upper()
    df['asset_type'] = "STOCK"
    df = df[['stock_name', 'asset_type', 'time', 'open', 'high', 'low', 'close', 'volume']]
    
    # Convert time to string format compatible with Postgres TIMESTAMPTZ
    df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%dT%H:%M:%S%z')
    # If no timezone info exists, add Z
    df['time'] = df['time'].apply(lambda x: x + "Z" if "+" not in x and "-" not in x[-6:] else x)
    
    os.makedirs(TMP_DIR, exist_ok=True)
    tmp_file = os.path.join(TMP_DIR, f"{symbol}_ohlcv.csv")
    df.to_csv(tmp_file, index=False, encoding='utf-8')
    logger.info(f"Transformed to {len(df)} rows. Saved tmp: {tmp_file}")
    
    return df

def load_supabase(df: pd.DataFrame):
     """Upsert DataFrame to Supabase."""
     logger.info("Loading into Supabase...")
     if df.empty:
         logger.warning("Empty DataFrame, skipping load.")
         return
         
     url: str = os.environ.get("SUPABASE_URL") or ""
     key: str = os.environ.get("SUPABASE_KEY") or ""
     supabase: Client = create_client(url, key)
     
     records = df.to_dict(orient="records")
     
     try:
         data, count = supabase.table("stock_ohlcv").upsert(
             records, 
             on_conflict="stock_name,time"
         ).execute()
         logger.info(f"SUCCESS: Upserted {len(records)} records to Supabase.")
     except Exception as e:
         logger.error(f"FAILED to upsert: {e}")

def run_etl(symbol: str, start_date: str, end_date: str, interval: str):
    load_dotenv()
    
    # Extract
    df_raw = extract_ohlcv(symbol, start_date, end_date, interval)
    
    # Transform
    df_final = transform_ohlcv(df_raw, symbol)
    
    # Load
    load_supabase(df_final)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, required=True, help="Stock Ticker")
    parser.add_argument("--start", type=str, required=True, help="Start Date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, required=True, help="End Date (YYYY-MM-DD)")
    parser.add_argument("--interval", type=str, default="1D", help="1D, 1W, 1M, 1H")
    args = parser.parse_args()
    
    run_etl(args.symbol, args.start, args.end, args.interval)
