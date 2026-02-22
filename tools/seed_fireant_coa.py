import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.fireant_mappings import FIREANT_CDKT, FIREANT_KQKD, FIREANT_LCTT_TRUC_TIEP, FIREANT_LCTT_GIAN_TIEP

try:
    from supabase import create_client, Client
except ImportError:
    print("FAILED: Missing supabase")
    sys.exit(1)

def seed_coa():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("Missing Supabase credentials in .env")
        return

    supabase = create_client(url, key)

    records = []
    
    # 1. CDKT
    for idx, item in enumerate(FIREANT_CDKT):
        record = {
            "report_type": "CDKT",
            "item_id": item["item_id"],
            "item": item["item"],
            "levels": item["levels"],
            "kbsv_id": item["kbsv_id"],
            "row_number": idx + 1
        }
        records.append(record)
        
    # 2. KQKD
    for idx, item in enumerate(FIREANT_KQKD):
        record = {
            "report_type": "KQKD",
            "item_id": item["item_id"],
            "item": item["item"],
            "levels": item["levels"],
            "kbsv_id": item["kbsv_id"],
            "row_number": idx + 1
        }
        records.append(record)

    # 3. LCTT_TT
    for idx, item in enumerate(FIREANT_LCTT_TRUC_TIEP):
        record = {
            "report_type": "LCTT_TT",
            "item_id": item["item_id"],
            "item": item["item"],
            "levels": item["levels"],
            "kbsv_id": item["kbsv_id"],
            "row_number": idx + 1
        }
        records.append(record)
        
    # 4. LCTT_GT
    for idx, item in enumerate(FIREANT_LCTT_GIAN_TIEP):
        record = {
            "report_type": "LCTT_GT", # LCTT_GT maps exactly to KBSV's LCTT
            "item_id": item["item_id"],
            "item": item["item"],
            "levels": item["levels"],
            "kbsv_id": item["kbsv_id"],
            "row_number": idx + 1
        }
        records.append(record)

    try:
        res, count = supabase.table("tt200_coa").upsert(
            records,
            on_conflict="report_type,item_id"
        ).execute()
        print(f"SUCCESS: Seeded {len(records)} Exact Fireant Items into tt200_coa.")
    except Exception as e:
        print(f"FAILED to seed: {e}")

if __name__ == "__main__":
    seed_coa()
