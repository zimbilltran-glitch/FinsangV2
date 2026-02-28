import pandas as pd
import sys

def parse_excel():
    filepath = "Chỉ số tài chính.xlsx"
    out = open("excel_dump.txt", "w", encoding="utf-8")
    try:
        xls = pd.ExcelFile(filepath)
        out.write(f"Sheets found: {xls.sheet_names}\n")
        for sheet in xls.sheet_names:
            out.write(f"\n--- Sheet: {sheet} ---\n")
            df = pd.read_excel(xls, sheet_name=sheet)
            out.write(df.to_string())
            out.write("\nColumns: " + str(df.columns.tolist()) + "\n")
    except Exception as e:
        out.write(f"Error parsing excel: {e}\n")
    out.close()

if __name__ == "__main__":
    parse_excel()
