# FINSANG v2.1 — High-Fidelity Financial Intelligence Terminal

**Finsang** is a production-grade financial data ecosystem for Vietnamese public companies. It integrates automated ETL pipelines from Vietcap IQ with high-fidelity React visualization and cloud synchronization.

---

## 🏛️ Project Governance & Master Docs

To ensure engineering consistency and rapid onboarding, use the following master documents:

- 📑 **[Finsang Master Team Guide](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Master_Team_Guide.md)**: **START HERE.** Detailed onboarding, standards, and workflow instructions.
- 🚀 **[Finsang Master Active Roadmap](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Master_Active_Roadmap.md)**: Overall tracker for Finsang's project phases.
- 📜 **[Finsang Master Logs](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Master_Logs.md)**: Historical audit trail and major milestones.
- 🧠 **[Finsang Master Challenges](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Master_Challenges.md)**: Technical hurdles and verified engineering solutions.
- 🔄 **[Finsang Master Changelog](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Master_Changelog.md)**: Changelog and version control tracker.
- 🔍 **[Finsang Master Findings](file:///c:/Users/Admin/OneDrive/Learn%20Anything/Antigravity/1.Project%20Source/Finsang_Master_Findings.md)**: Granular finding reports from audits.

---

## 🏗️ Directory Hierarchy

```text
Finsang/
├── frontend/             # Primary React + Vite visualization (OLED Dark)
├── sub-projects/         # High-level engine components
│   ├── Version_2/        # Core ETL Pipeline (Vietcap API -> encrypted Parquet)
│   ├── Version_1/        # Legacy / Baseline code
│   ├── PDF_TRANS_Pipeline/ # Financial PDF extraction suite
│   ├── V3_SimplyWallSt/  # Simply Wall St 360 Overview Integration
│   └── V4_Chart_Improve/ # Analysis Charts (Recharts Integration)
├── internal-skills/      # Agent capabilities & Automated test suites
├── design-themes/        # UI/UX reference systems (Simply Wall St, Fireant)
├── docs/                 # Granular finding reports & sheet schemas
└── data/                 # (Gitignored) Encrypted financial store
```

---

## 🚦 Status: Phase 4.0 Analysis Charts Integration
Hiện tại dự án đang trong quá trình phát triển Phase 4.0 (V4_Chart_Improve). Tab "Biểu đồ phân tích" mới đang được xây dựng bằng `recharts` để trực quan hoá dữ liệu tài chính cho 3 nhóm ngành (Bank, Sec, Normal), lấy data trực tiếp từ cloud Supabase. Các luồng ETL nền (Version 2) và tính năng 360 Overview (Version 3) đã đi vào ổn định.

*— Developed by the Finsang Engineering Team under CTO Supervision.*

