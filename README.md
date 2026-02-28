# FINSANG v2.1 — High-Fidelity Financial Intelligence Terminal

**Finsang** is a production-grade financial data ecosystem for Vietnamese public companies. It integrates automated ETL pipelines from Vietcap IQ with high-fidelity React visualization and cloud synchronization.

---

## 🏛️ Project Governance & Master Docs

To ensure engineering consistency and rapid onboarding, use the following master documents:

- 📑 **[Finsang Team Guide](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Team_Guide.md)**: **START HERE.** Detailed onboarding, standards, and workflow instructions.
- 📜 **[Master Logs](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Master_Logs.md)**: Historical audit trail and major milestones.
- 🧠 **[Master Challenges](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Master_Challenges.md)**: Technical hurdles and verified engineering solutions.
- 🔄 **[Update Timeline](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Updates.md)**: Changelog and version control tracker.

---

## 🏗️ Directory Hierarchy

```text
Finsang/
├── frontend/             # Primary React + Vite visualization (OLED Dark)
├── sub-projects/         # High-level engine components
│   ├── Version_2/        # Core ETL Pipeline (Vietcap API -> encrypted Parquet)
│   ├── Version_1/        # Legacy / Baseline code
│   └── PDF_TRANS_Pipeline/ # Financial PDF extraction suite
├── internal-skills/      # Agent capabilities & Automated test suites
├── design-themes/        # UI/UX reference systems (Simply Wall St, Fireant)
├── docs/                 # Granular finding reports & sheet schemas
└── data/                 # (Gitignored) Encrypted financial store
```

---

## 🚦 Status: Phase 2.2 Enrichment & UI Polish
Actively running background extraction (`vn30_enrichment.py`) to scrape and synchronize up to 10 years of data (8 Years + 32 Quarters) for the entire VN30 basket. Both React and Streamlit interfaces have been optimized for temporal sorting (Z-A) and focused Balance Sheet viewing (removed generic charts).

*— Developed by the Finsang Engineering Team under CTO Supervision.*

