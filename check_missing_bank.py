import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('sub-projects/V2_Data_Pipeline/golden_schema.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

missing = 0
total = 0
print('--- EMPTY OR MISSING CDKT_BANK MAPPINGS ---')
for fld in schema['fields']:
    if fld['sheet'] == 'CDKT_BANK':
        total += 1
        key = fld.get('vietcap_key')
        if not key or not isinstance(key, dict) or not key.get('bank'):
            print(f"{fld['field_id']:<40} | {fld['vn_name']}")
            missing += 1

print(f"\nMissing {missing}/{total}")
