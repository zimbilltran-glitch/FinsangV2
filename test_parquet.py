import pandas as pd
from pathlib import Path
import io
import sys
import traceback
from dotenv import load_dotenv

load_dotenv('.env')

sys.path.insert(0, str(Path('sub-projects/V2_Data_Pipeline').resolve()))
from pipeline import get_cipher

pq_path = Path('data/MBB/period_type=year/sheet=lctt_bank/MBB.parquet')
print('Does file exist?', pq_path.exists())
print('Absolute path:', pq_path.resolve())

try:
    cipher = get_cipher()
    if cipher:
        with open(pq_path, 'rb') as f:
            encrypted_data = f.read()
        try:
            decrypted_data = cipher.decrypt(encrypted_data)
            df = pd.read_parquet(io.BytesIO(decrypted_data))
        except Exception:
            df = pd.read_parquet(pq_path)
    else:
        df = pd.read_parquet(pq_path)

    print('Total rows:', len(df))
    print('Sample value for lctt_bank_tien_chi_tra_cho_nhan_vien_va_hoat_dong_quan_ly_cong_cu:')
    print(df[df['field_id'] == 'lctt_bank_tien_chi_tra_cho_nhan_vien_va_hoat_dong_quan_ly_cong_cu']['value'].values[:5])
    print('Sample value for lctt_bank_thu_nhap_lai_va_cac_khoan_thu_nhap_tuong_tu_nhan_duoc:')
    print(df[df['field_id'] == 'lctt_bank_thu_nhap_lai_va_cac_khoan_thu_nhap_tuong_tu_nhan_duoc']['value'].values[:5])
except Exception as e:
    traceback.print_exc()
