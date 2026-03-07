import sys, json, math
from pathlib import Path
sys.path.insert(0, 'sub-projects/V2_Data_Pipeline')
from providers import VietcapProvider

p = VietcapProvider()
payload = p.fetch_section('MBB', 'BALANCE_SHEET')

api_2024 = {}
for yd in payload.get('years', []):
    if yd.get('yearReport') == 2024:
        for k, v in yd.items():
            if isinstance(v, (int, float)):
                api_2024[k] = v
        break

with open('sub-projects/V2_Data_Pipeline/golden_schema.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

print("--- UNMAPPED BANK CDKT ---")
for fld in schema['fields']:
    if fld['sheet'] == 'CDKT_BANK' and not (fld.get('vietcap_key') or {}).get('bank'):
        val_2024 = fld.get('sample_values', {}).get('year:2024')
        if val_2024 is not None:
            possible_keys = []
            for k, v in api_2024.items():
                if math.isfinite(v) and math.isfinite(val_2024):
                    if v == 0 and val_2024 == 0:
                        possible_keys.append(k)
                    elif v != 0 and val_2024 != 0:
                        diff = abs(v - val_2024) / max(abs(v), abs(val_2024))
                        if diff < 0.001:
                            possible_keys.append(k)
            print(f"{fld['field_id']:<40} | 2024 Val: {val_2024} | Match API: {possible_keys}")
