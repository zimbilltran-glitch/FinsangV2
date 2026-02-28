import json
import sys

def search_schema(keywords):
    with open('sub-projects/Version_2/golden_schema.json', 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    results = {k: [] for k in keywords}
    for field in schema['fields']:
        vn_name = str(field.get('vn_name', '')).lower()
        field_id = str(field.get('field_id', '')).lower()
        
        for kw in keywords:
            if kw.lower() in vn_name or kw.lower() in field_id:
                results[kw].append({
                    'sheet': field.get('sheet'),
                    'field_id': field.get('field_id'),
                    'vn_name': field.get('vn_name')
                })
    
    with open('schema_mapping.txt', 'w', encoding='utf-8') as out:
        for kw, matches in results.items():
            out.write(f"\n--- Keyword: {kw} ---\n")
            for m in matches:
                out.write(f"  [{m['sheet']}] {m['field_id']}: {m['vn_name']}\n")

if __name__ == "__main__":
    keywords = [
        "Tiền và tương đương tiền",
        "Đầu tư ngắn hạn",
        "phải thu",
        "tồn kho",
        "Tài sản cố định",
        "dở dang dài hạn",
        "Tài sản khác",
        "TỔNG CỘNG TÀI SẢN",
        "Vay dài hạn",
        "Vay ngắn hạn",
        "Nợ chiếm dụng",
        "phải trả người bán",
        "người mua trả tiền trước",
        "Vốn góp",
        "Lãi chưa phân phối",
        "Tổng cộng nguồn vốn",
        "Doanh thu chưa thực hiện",
        "Lưu chuyển tiền",
        "Doanh thu thuần",
        "Lợi nhuận của cổ đông",
        "Lợi nhuận sau thuế của công ty mẹ",
        "Lợi nhuận gộp",
        "Chi phí bán hàng",
        "Quản lý doanh nghiệp",
        "Doanh thu hoạt động tài chính",
        "Chi phí tài chính",
        "liên doanh",
        "Thu nhập khác",
        "Cổ phiếu"
    ]
    search_schema(keywords)
