import os, sys, json
from dotenv import load_dotenv
load_dotenv('.env')

from supabase import create_client
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_SERVICE_ROLE_KEY'])

tbl = 'balance_sheet'
batch = [{'stock_name': 'MBB', 'asset_type': 'STOCK', 'source': 'vietcap', 'item_id': 'bsb1', 'item': 'abc', 'levels': 0, 'row_number': 1, 'period': '2024', 'unit': 'tỷ', 'value': 0.0}]
on_conflict = 'stock_name,period,item_id,source'
print("Executing upsert...")
try:
    res = sb.table(tbl).upsert(batch, on_conflict=on_conflict).execute()
    print('SUCCESS:', len(res.data))
except Exception as e:
    print('EXCEPTION:', repr(e))
