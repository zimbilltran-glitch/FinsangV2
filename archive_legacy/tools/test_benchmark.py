import os
from dotenv import load_dotenv

def test():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    from supabase import create_client
    supabase = create_client(url, key)
    
    res = supabase.table("balance_sheet_benchmark").select("*").limit(5).execute()
    print("Data in balance_sheet_benchmark limit 5:")
    print(res.data)

if __name__ == "__main__":
    test()
