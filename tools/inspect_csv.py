import pandas as pd
import sys

def main():
    df = pd.read_csv(".tmp/NLG_benchmark.csv")
    print(df[['Chỉ tiêu', 'item_id', 'Level']].head(20))
    print(df[['Chỉ tiêu', 'item_id', 'Level']].tail(20))

if __name__ == "__main__":
    main()
