import sys
from pathlib import Path
sys.path.insert(0, r'd:\Project_partial\Finsang\sub-projects\Version_2')
from sync_supabase import get_supabase
sb = get_supabase()

def dump(tk):
    data = sb.table('cash_flow').select('item_id,value').eq('stock_name', tk).eq('period', '2024').execute().data
    with open(f'{tk}_cf.txt', 'w', encoding='utf-8') as f:
        for r in data:
            f.write(f"{r['item_id']}: {r['value']}\n")

dump('FPT')
dump('MBB')
dump('SSI')
