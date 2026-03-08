import requests
from typing import Optional, Dict, Any
from .base import BaseProvider

class VietcapProvider(BaseProvider):
    """Data provider for Vietcap IQ API."""
    
    BASE_URL = "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{ticker}/financial-statement?section={section}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://trading.vietcap.com.vn/",
        "Origin": "https://trading.vietcap.com.vn",
    }
    
    API_PREFIX = {
        "BALANCE_SHEET":    ["bsa", "bsb", "bss", "bsi"],
        "INCOME_STATEMENT": ["isa", "isb", "iss", "isi"],
        "CASH_FLOW":        ["cfa", "cfb", "cfs", "cfi", "cfs"],
        "NOTE":             ["noa", "nob", "nos", "noi"],
    }

    def fetch_section(self, ticker: str, section: str) -> Optional[Dict[str, Any]]:
        url = self.BASE_URL.format(ticker=ticker.upper(), section=section)
        try:
            r = requests.get(url, headers=self.HEADERS, timeout=20)
            r.raise_for_status()
            data = r.json()
            if not data.get("successful"):
                print(f"    ⚠️  Vietcap API returned unsuccessful: {data.get('msg')}")
                return None
            return data.get("data", {})
        except Exception as e:
            print(f"    ❌ Vietcap fetch error for {section}: {e}")
            return None

    def get_api_value_by_key(self, row: dict, key: str) -> Optional[float]:
        val = row.get(key)
        if val is None and isinstance(row.get("values"), dict):
            val = row["values"].get(key)
        return float(val) if val is not None else None

    def get_api_value(self, row: dict, section: str, sheet_row_idx: int, field_id: str = "") -> Optional[float]:
        """
        Fallback when vietcap_key is empty (e.g. NOTE section, or unmapped KQKD/LCTT).
        Iterates through possible sector prefixes to extract values dynamically.
        """
        best_val = None
        for prefix in self.API_PREFIX.get(section, []):
            key = f"{prefix}{sheet_row_idx}"
            val = row.get(key)
            if val is None and isinstance(row.get("values"), dict):
                val = row["values"].get(key)
            
            if val is not None:
                f_val = float(val)
                if best_val is None or f_val != 0.0:
                    best_val = f_val
                if f_val != 0.0:
                    break
                    
        return best_val

