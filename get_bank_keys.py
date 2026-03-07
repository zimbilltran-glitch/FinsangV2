import json

with open('sub-projects/V2_Data_Pipeline/golden_schema.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

with open('bank_keys.txt', 'w', encoding='utf-8') as out:
    for fld in schema['fields']:
        if fld['sheet'] == 'CDKT_BANK' and ('TỔNG' in fld['vn_name'].upper() or 'TÀI SẢN' in fld['vn_name'].upper()):
            out.write(f"{fld['field_id']}: {fld['vn_name']}\n")
