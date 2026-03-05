import sys
from pathlib import Path
sys.path.insert(0, r'd:\Project_partial\Finsang\sub-projects\Version_2')
from sync_supabase import get_supabase
sb = get_supabase()

def p(tk, period='2024'):
    print(f"\n--- {tk} CF Data ---")
    data = sb.table('cash_flow').select('item_id,value').eq('stock_name', tk).eq('period', period).execute().data
    for r in data:
        print(f"{r['item_id']}: {r['value']}")

p('FPT')
p('MBB')
p('SSI')
