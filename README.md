# 🦁 FINSANG V2.0

**Finsang** is a high-performance, deterministic financial data pipeline and terminal viewer. It extracts Vietnamese corporate financial statements (Báo Cáo Tài Chính) seamlessly, normalizes the data into a strict `A = L + E` preserving schema, and serves the analytics via a rapid terminal UI.

## 🚀 Features

*   **B.L.A.S.T. Architecture:**
    *   **[B]**lueprint: Maps raw financial terms to a universal `golden_schema.json` (345 core fields).
    *   **[L]**ink: Extracts data reliably from public API endpoints.
    *   **[A]**rchitect: Transforms and stores data in Hive-partitioned Parquet files for sub-second read speeds.
    *   **[S]**tylize: Beautiful, command-line native viewer using `rich`.
    *   **[T]**rigger: Fully automated via Windows Task Scheduler with cloud observability (Supabase).
*   **CFO Validation Engine:** Strict double-entry accounting identity checks (e.g., *Total Assets = Liabilities + Equity*) to immediately flag anomalous reporting periods.
*   **Derived Metrics Engine:** Automatically calculates Gross Margin, Net Margin, Current Ratios, and Debt/Equity dynamic metrics.

## 📦 Installation & Setup

1. **Clone and Setup Virtual Environment:**
   ```bash
   git clone <repo-url>
   cd finsang
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install pandas pyarrow rich requests python-dotenv supabase
   ```

3. **Configure Environment:**
   Create a `.env` file in the project root:
   ```env
   # Database Logging (Optional - Fails gracefully if missing)
   SUPABASE_URL="your-supabase-url"
   SUPABASE_KEY="your-supabase-anon-key"

   # Pipeline Configuration
   FINSANG_TICKERS=VHC,FPT,VIC,HPG,MWG
   FINSANG_VIEW_PERIODS=8
   ```

## 💻 Usage 

### 1. Terminal UI (Viewer)
Quickly view perfectly formatted financial statements directly in your terminal:

```bash
# View Quarterly Income Statement (KQKD)
python Version_2/viewer.py --ticker VHC --sheet kqkd --period quarter

# View Yearly Balance Sheet (CĐKT)
python Version_2/viewer.py --ticker VHC --sheet cdkt --period year

# View Derived Financial Metrics (Chỉ Số Tài Chính)
python Version_2/viewer.py --ticker VHC --sheet cstc --period year
```

*(Available Sheets: `cdkt` (Balance Sheet), `kqkd` (Income Statement), `lctt` (Cash Flow), `note` (Footnotes), `cstc` (Metrics))*

### 2. Multi-Ticker Pipeline Automation
Run the extraction and normalization pipeline for all your configured tickers:

```bash
# Run for all tickers defined in .env
python Version_2/run_all.py

# Override with specific tickers
python Version_2/run_all.py --tickers REE PNJ
```

### 3. Windows Task Scheduler
Automate your daily/quarterly pulls locally:

```bash
# Register a daily task at 06:00 AM
python Version_2/scheduler.py install --time 06:00

# Check status
python Version_2/scheduler.py status
```

## 🔒 Security & Architecture Notes
*   **Zero Hardcoded Secrets**: All keys are managed externally via `.env`.
*   **Local-First Processing**: Core data is preserved entirely on the user's hard drive (`.parquet` storage), guaranteeing data ownership.
*   **Idempotency & Fallbacks**: Pipeline intelligently manages temporary caches (`.tmp/`) and gracefully falls back if network logging (Supabase) fails. 

---
*Built with ❤️ by the Finsang team.*
