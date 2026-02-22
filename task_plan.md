# Finsang Task Plan (Blueprint)

## Phases
- [x] Protocol 0 – Initialization
- [x] Phase B – Blueprint (Vision & Logic)
- [x] Phase L – Link (Connectivity)
- [x] Phase A – Architect (3-Layer Build)
- [x] Phase S – Stylize (Refinement & UI)
- [x] Phase T – Trigger (Deployment & Automation)

## Goals
- Build a Vietnam stock data website for fundamental and technical analysis.
- Provide price charts and deep-dive financial charts (asset structure, capital structure like NLG sample).
- Crawl OHLC price data on an hourly schedule (avoid tick data).
- Crawl Financial Statements on a daily (24h) schedule.
- Store all data in a Supabase PostgreSQL database.
- Primary Data Source: KBSV API (reverse-engineered) or vnstock as fallback.
- Build a simple, clean UI first, ready for future branding.

## Non-Goals
- Real-time tick-by-tick trading data.
- Complex initial branding or UI components before logic is set.
- Trade execution or portfolio management (this is purely for research/analysis).

## Assumptions
- We have or can obtain a Supabase project URL and API key.
- The user's VIP API key for vnstock (referenced in older conversations) can be used if needed.
- `vnstock` library can reliably fetch KBSV data.
