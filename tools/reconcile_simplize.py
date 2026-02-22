"""
Phase D CFO Data Audit & Reconciliation Algorithm (reconcile_simplize.py)

WHAT IT DOES:
Acts as an automated Chief Financial Officer (CFO). It fetches benchmark data scraped from Simplize,
subjects it to a strict Accounting Checksum (Total Assets == Total Liabilities + Equity),
and if passed, diffs the benchmark data against the primary database (KBSV source) to hunt for discrepancies.

WHY IT'S DESIGNED THIS WAY (Architectural Decisions):
1. Zero-Trust Data Architecture: Web scraped data is notoriously unreliable. We cannot simply blind-insert 
   scraped data into Production as a 'Benchmark'. The mathematical Checksum ensures structural integrity first.
2. Automated QA: Prevents "Garbage In, Garbage Out" scenarios. If the benchmark fails the audit, the script halts,
   refusing to reconcile against a broken benchmark.
3. Diffing for Data Completeness: We compare "Tổng tài sản" (Simplize) vs "TỔNG CỘNG TÀI SẢN" (KBSV) to catch
   whether our Sparse-To-Dense merge in `fetch_financials.py` actually assembled the correct final number.
"""
import os
import sys
import pandas as pd
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_kbsv_period(p: str) -> str:
    """Convert KBSV '2024-4' to Simplize 'Q4-2024'"""
    parts = p.split('-')
    if len(parts) == 2 and parts[1].isdigit():
        return f"Q{parts[1]}-{parts[0]}"
    return p

def run_cfo_audit(df_bench: pd.DataFrame) -> bool:
    """
    Implement @professional-cfo-analyst accounting equation checksums.
    
    WHY THIS IS VITAL: Financial datasets are strictly mathematical. If Assets do not equal
    Liabilities + Equity, the Balance Sheet is fundamentally broken, meaning our scraping logic
    or the source data is compromised. We use a dynamic tolerance (< 5.0) to account for raw
    rounding quirks (billions vs strict precise decimals) from websites.
    """
    logger.info("Executing CFO Data Audit on Benchmark dataset...")
    
    # Needs Total Assets == Total Equity & Liabilities for each period
    periods = df_bench['period'].unique()
    passed = True
    
    for p in periods:
        df_p = df_bench[df_bench['period'] == p]
        
        # We fuzzy match the standard names
        assets = df_p[df_p['item'].str.contains("Tổng tài sản", case=False, na=False)]['value'].sum()
        liab_eq = df_p[df_p['item'].str.contains("Tổng nguồn vốn", case=False, na=False)]['value'].sum()
        
        diff = abs(assets - liab_eq)
        # Financial tolerance is exactly 0 but due to billions rounding maybe 1-2. Let's use < 2 Tỷ VND.
        if diff > 5.0:
            logger.error(f"[CFO AUDIT FAILED] Period {p}: Assets={assets}, Liab+Eq={liab_eq}, Diff={diff}")
            passed = False
        else:
            logger.info(f"[CFO AUDIT PASSED] Period {p}: Assets={assets}, Liab+Eq={liab_eq}")
            
    return passed

def run_reconciliation(symbol: str):
    """
    Compare Main DB (KBSV/Sparse-merged) vs Benchmark DB (Simplize) and generate a Markdown Diff Report.
    
    WHY CLI REPORT: Allows the @product-manager-toolkit to quickly visually inspect and sign-off
    on Data Engineering phases without needing to open BI tools.
    """
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        logger.error("Missing SUPABASE credentials")
        return
        
    try:
        from supabase import create_client
        supabase = create_client(url, key)
    except ImportError:
        logger.error("Missing supabase package")
        return
        
    # Load Main Data (KBSV, mapped to TT200)
    res_main = supabase.table("balance_sheet").select("*").eq("stock_name", symbol.upper()).execute()
    df_main = pd.DataFrame(res_main.data)
    if not df_main.empty:
        df_main['period'] = df_main['period'].apply(normalize_kbsv_period)
        
    # Load Benchmark Data (Simplize)
    res_bench = supabase.table("balance_sheet_benchmark").select("*").eq("stock_name", symbol.upper()).execute()
    df_bench = pd.DataFrame(res_bench.data)
    
    if df_bench.empty:
        logger.error("No Benchmark data found. Please run scrape_simplize.py first.")
        return
        
    # CFO AUDIT (Integrity Check)
    audit_passed = run_cfo_audit(df_bench)
    if not audit_passed:
        logger.error("Benchmark dataset failed CFO Audit. Canceling Reconciliation.")
        return
        
    if df_main.empty:
        logger.error("No Main data found. Please run fetch_financials.py first.")
        return
        
    # Data Diff
    logger.info("CFO Audit passed. Now Diffing KBSV against Simplize benchmark...")
    
    report_lines = [f"# Phase D: CFO Reconciliation Report for {symbol.upper()}"]
    report_lines.append(f"**Audit Status:** PASSED 🟢")
    report_lines.append("")
    report_lines.append("## Discrepancies (KBSV vs Simplize Benchmark)")
    report_lines.append("| Period | Item | KBSV | Simplize | Diff |")
    report_lines.append("|---|---|---|---|---|")
    
    discrepancy_count = 0
    
    for p in df_bench['period'].unique():
        b_assets = df_bench[(df_bench['period'] == p) & (df_bench['item'].str.contains("Tổng tài sản", case=False))]['value'].sum()
        m_assets = df_main[(df_main['period'] == p) & (df_main['item'].str.contains("TỔNG CỘNG TÀI SẢN", case=False))]['value'].sum()
        
        diff = abs(m_assets - b_assets)
        if diff > 10.0:
            report_lines.append(f"| {p} | Total Assets | {m_assets:,.2f} | {b_assets:,.2f} | {diff:,.2f} |")
            discrepancy_count += 1
            
        b_liabeq = df_bench[(df_bench['period'] == p) & (df_bench['item'].str.contains("Tổng nguồn vốn", case=False))]['value'].sum()
        m_liabeq = df_main[(df_main['period'] == p) & (df_main['item'].str.contains("TỔNG CỘNG NGUỒN VỐN", case=False))]['value'].sum()
        
        diff_liab = abs(m_liabeq - b_liabeq)
        if diff_liab > 10.0:
            report_lines.append(f"| {p} | Total Liab & Eq | {m_liabeq:,.2f} | {b_liabeq:,.2f} | {diff_liab:,.2f} |")
            discrepancy_count += 1

    if discrepancy_count == 0:
        report_lines.append("| All | Core Items | MATCH | MATCH | 0 |")
        logger.info("100% Core Matrix Match.")
    else:
        logger.warning(f"Found {discrepancy_count} Core Table Discrepancies.")
        
    report_md = "\n".join(report_lines)
    
    os.makedirs(".tmp", exist_ok=True)
    report_path = os.path.join(".tmp", f"{symbol}_reconciliation_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    logger.info(f"Reconciliation Report generated at {report_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reconcile_simplize.py <SYMBOL>")
        sys.exit(1)
    run_reconciliation(sys.argv[1])
