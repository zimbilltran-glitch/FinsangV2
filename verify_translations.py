import os, sys, json
sys.path.insert(0, 'sub-projects/V2_Data_Pipeline')
from dotenv import load_dotenv
load_dotenv('.env', override=True)
os.environ['SUPABASE_KEY'] = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

from sb_client import get_sb
sb = get_sb()

res = sb.table('api_translation_dictionary').select('sector, statement', count='exact').execute()
print(f'Total translations inserted: {len(res.data)}')

aggr = {}
for r in res.data:
    key = f"{r['sector']}_{r['statement']}"
    aggr[key] = aggr.get(key, 0) + 1

for k, v in sorted(aggr.items()):
    print(f'  {k}: {v}')

print('\nSample entries:')
sample = sb.table('api_translation_dictionary').select('*').limit(3).execute()
print(json.dumps(sample.data, indent=2, ensure_ascii=False))
