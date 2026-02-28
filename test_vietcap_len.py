import sys
sys.path.insert(0, './sub-projects/Version_2')
from providers.vietcap import VietcapProvider

p = VietcapProvider()
data = p.fetch_section('FPT', 'BALANCE_SHEET')

qs = data.get('quarters', [])
ys = data.get('years', [])

print('Quarters available:', len(qs))
if qs: print('Oldest Q:', qs[-1].get('yearReport'), qs[-1].get('lengthReport'))
print('Years available:', len(ys))
if ys: print('Oldest Y:', ys[-1].get('yearReport'))
