from dotenv import load_dotenv
load_dotenv()
import sys
sys.path.insert(0, './sub-projects/Version_2')

from pipeline import load_tab_from_supabase
from metrics import calc_metrics

try:
    cdkt = load_tab_from_supabase('VHC', 'quarter', 'cdkt')
    print("CDKT shape:", cdkt.shape)
    kqkd = load_tab_from_supabase('VHC', 'quarter', 'kqkd')
    print("KQKD shape:", kqkd.shape)
    lctt = load_tab_from_supabase('VHC', 'quarter', 'lctt')
    print("LCTT shape:", lctt.shape)

    df = calc_metrics('VHC', 'quarter')
    print("Metrics shape:", df.shape)
    if df.empty:
        print("Empty DF from calc_metrics")
    else:
        print(df.head(10).to_string())
except Exception as e:
    print(f"ERROR: {e}")
