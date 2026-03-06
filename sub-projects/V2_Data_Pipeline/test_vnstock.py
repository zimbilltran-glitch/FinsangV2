from vnstock3 import Vnstock
import pandas as pd

def test_tcbs(ticker="MBB"):
    try:
        stock = Vnstock().stock(symbol=ticker, source='TCBS')
        df = stock.finance.ratio(period='quarter', lang='vi')
        print(f"[{ticker} - TCBS] Columns:")
        for col in df.columns:
            print(f" - {col}")
    except Exception as e:
        print(f"[{ticker} - TCBS] Error: {e}")

if __name__ == "__main__":
    test_tcbs("MBB")
