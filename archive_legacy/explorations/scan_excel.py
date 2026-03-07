import pandas as pd

df = pd.read_excel(r'data\excel_imports\MBB_BCTC_Vietcap.xlsx', sheet_name='Balance Sheet', header=None)

with open('scan_out.txt', 'w', encoding='utf-8') as f:
    for i in range(15):
        row_data = df.iloc[i].dropna().tolist()
        f.write(f"Row {i}: {row_data}\n")
