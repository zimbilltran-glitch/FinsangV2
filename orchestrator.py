"""
Phase T: Central Orchestrator Pipeline
Acts as the main worker script to run the autonomous ETL jobs in sequential order.
Addresses CTO Debt 2: Orchestration.
"""
import os
import sys
import subprocess
import logging
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ORCHESTRATOR] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_step(cmd_list, step_name):
    """Executes a subprocess command inline with streaming output."""
    logger.info(f"--- STARTING {step_name} ---")
    logger.info(f"EXEC: {' '.join(cmd_list)}")
    
    try:
        # Use subprocess.run to stream output directly to console
        res = subprocess.run(cmd_list, check=True)
        logger.info(f"--- SUCCESS: {step_name} ---")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"!!! FAILED: {step_name} (Exit Code: {e.returncode}) !!!")
        return False
    except Exception as e:
        logger.error(f"!!! FATAL ERROR in {step_name}: {e} !!!")
        return False

def orchestrate_pipeline(symbol: str):
    logger.info(f"===========================================================")
    logger.info(f"🚀 INITIATING FULL B.L.A.S.T PIPELINE FOR {symbol.upper()}")
    logger.info(f"===========================================================")
    
    # 1. Fetch OHLCV
    cmd_ohlcv = [sys.executable, "tools/fetch_ohlcv.py", "--symbol", symbol, "--start", "2020-01-01", "--end", "2025-12-31"]
    if not run_step(cmd_ohlcv, "Phase 1: Fetch OHLCV (vnstock)"):
        sys.exit(1)
        
    # 2. Fetch Financials (All 3 types)
    for rep_type in ["KQKD", "CDKT", "LCTT"]:
        cmd_fin = [sys.executable, "tools/fetch_financials.py", "--symbol", symbol, "--type", rep_type, "--period", "quarter"]
        if not run_step(cmd_fin, f"Phase 2: Fetch Financials [{rep_type}] (KBSV -> Dense Merge)"):
            sys.exit(1)
            
    # 3. Precompute CFO Ratios
    cmd_ratios = [sys.executable, "tools/compute_ratios.py", "--symbol", symbol]
    if not run_step(cmd_ratios, "Phase 3: Precomputing Financial Ratios (MOLAP)"):
        sys.exit(1)
        
    # 4. Scrape Simplize Benchmark (Autonomous Web Scraper)
    cmd_scrape = [sys.executable, "tools/scrape_simplize.py", "--symbol", symbol]
    if not run_step(cmd_scrape, "Phase 4: Autonomous Benchmark Scraping (Simplize)"):
        sys.exit(1)
        
    # 5. CFO Zero-Trust Audit & Reconciliation
    cmd_audit = [sys.executable, "tools/reconcile_simplize.py", "--symbol", symbol]
    if not run_step(cmd_audit, "Phase 5: Zero-Trust CFO Audit & Reconciliation"):
        sys.exit(1)
        
    logger.info(f"===========================================================")
    logger.info(f"✅ B.L.A.S.T PIPELINE COMPLETED FLAWLESSLY FOR {symbol.upper()}")
    logger.info(f"===========================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Full Autonomous Data Pipeline")
    parser.add_argument("--symbol", type=str, required=True, help="Stock ticker to process")
    args = parser.parse_args()
    
    # Needs to be run from project source root
    if not os.path.exists("tools/fetch_ohlcv.py"):
        logger.error("Must run orchestrator.py from the Project Source root directory.")
        sys.exit(1)
        
    orchestrate_pipeline(args.symbol.upper())
