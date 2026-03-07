import sys, json
sys.path.insert(0, 'sub-projects/V2_Data_Pipeline')
from providers import VietcapProvider

p = VietcapProvider()
payload = p.fetch_section('MBB', 'BALANCE_SHEET')

api_2024 = {}
for yd in payload.get('years', []):
    if yd.get('yearReport') == 2024:
        api_2024 = yd
        break

with open('mbb_2024_api.json', 'w') as f:
    json.dump(api_2024, f, indent=2)

val = 8238447590991.0
print(f"Looking for exactly: {val}")

found = False
for k, v in api_2024.items():
    if isinstance(v, (int, float)):
        print(f"{k}: {v}")
        if abs(v - val) < 1000000:
            print(f"*** FOUND EXACT MATCH: {k} = {v} ***")
            found = True
if not found:
    print("NOT FOUND IN API PAYLOAD!")
