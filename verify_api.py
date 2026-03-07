import sys, json
sys.path.insert(0, 'sub-projects/V2_Data_Pipeline')
from providers import VietcapProvider

p = VietcapProvider()
payload = p.fetch_section('MBB', 'BALANCE_SHEET')

print('--- ALL API KEYS ---')
keys = set()
for year_data in payload.get('years', []):
    for k in year_data.keys():
        keys.add(k)
        
print(f"Total API elements: {len(keys)}")
for k in sorted(keys):
    if k.startswith('bsb'):
        print(f"Key: {k}")
