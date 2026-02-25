import { useEffect, useState, useMemo } from 'react'
import { supabase } from './supabaseClient'
import './App.css'

// ─── V2 Data Source ────────────────────────────────────────────────────────
// Data synced from Version 2 Parquet pipeline (Vietcap API → Parquet → Supabase).
// Wide views pivot rows via jsonb_object_agg(period, value) = periods_data JSONB.
// Values stored in Tỷ VND. Display in Triệu VND (×1000).
// ────────────────────────────────────────────────────────────────────────────

const TICKERS = [
  { code: 'VHC', name: 'CTCP Vĩnh Hoàn', exchange: 'HOSE' },
  { code: 'FPT', name: 'CTCP Tập đoàn FPT', exchange: 'HOSE' },
  { code: 'HPG', name: 'CTCP Tập đoàn Hoà Phát', exchange: 'HOSE' },
]

const REPORT_TABS = [
  { id: 'CDKT', label: 'Cân đối kế toán', table: 'balance_sheet_wide' },
  { id: 'KQKD', label: 'Kết quả kinh doanh', table: 'income_statement_wide' },
  { id: 'LCTT', label: 'Lưu chuyển tiền tệ', table: 'cash_flow_wide' },
  { id: 'CSTC', label: 'Chỉ số tài chính', table: 'financial_ratios_wide' },
]

const PERIOD_FILTERS = [
  { id: 'year', label: 'Năm' },
  { id: 'quarter', label: 'Quý' },
]

// ─── Helpers ──────────────────────────────────────────────────────────────

// Format: Raw VND (đồng) → Triệu VND (÷ 1,000,000)
function formatNumber(num) {
  if (num === null || num === undefined || num === 0) return '–'
  const inMillions = num / 1000000
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
  }).format(inMillions)
}

// Format period for header: "Q4/2024" or "2024" displayed as-is
function formatPeriodLabel(p) {
  if (!p) return p
  return p
}

// Is this a major heading row (bold, uppercase)?
function isMajorHeading(row) {
  return (
    row.levels === 0 ||
    row.item?.startsWith('TỔNG') ||
    row.item?.startsWith('Cộng') ||
    /^[IVX]+\./.test(row.item || '')
  )
}

// ─── App ──────────────────────────────────────────────────────────────────

export default function App() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [ticker, setTicker] = useState('VHC')
  const [reportType, setReportType] = useState('CDKT')
  const [periodFilter, setPeriodFilter] = useState('year')
  const [periods, setPeriods] = useState([])
  const [expandedRows, setExpandedRows] = useState({})

  const currentTicker = TICKERS.find(t => t.code === ticker) || TICKERS[0]
  const currentTab = REPORT_TABS.find(t => t.id === reportType) || REPORT_TABS[0]

  useEffect(() => {
    async function fetchData() {
      setLoading(true)

      const { data: reports, error } = await supabase
        .from(currentTab.table)
        .select('*')
        .eq('stock_name', ticker)
        .order('row_number', { ascending: true })

      if (error) {
        console.error('Supabase error:', error)
        setData([]); setPeriods([]); setLoading(false); return
      }
      if (!reports || reports.length === 0) {
        setData([]); setPeriods([]); setLoading(false); return
      }

      // Build parent tree for expand/collapse
      const processed = reports.map((row, i) => {
        let parent_id = null
        if (row.levels > 0) {
          for (let j = i - 1; j >= 0; j--) {
            if (reports[j].levels === row.levels - 1) {
              parent_id = reports[j].item_id; break
            }
          }
        }
        return { ...row, parent_id }
      })

      setData(processed)

      // Collect period columns from periods_data, filter by year/quarter
      const allPeriods = new Set()
      processed.forEach(r => {
        Object.keys(r.periods_data || {}).forEach(p => allPeriods.add(p))
      })

      let filteredPeriods = Array.from(allPeriods)
      if (periodFilter === 'year') {
        filteredPeriods = filteredPeriods.filter(p => /^\d{4}$/.test(p))
      } else {
        filteredPeriods = filteredPeriods.filter(p => /^Q\d\/\d{4}$/.test(p))
      }

      // Sort newest → oldest
      const cols = filteredPeriods.sort((a, b) => b.localeCompare(a)).slice(0, 8)
      setPeriods(cols)

      // Auto-expand L0 + L1
      const defaultExpanded = {}
      processed.forEach(r => { if (r.levels <= 1) defaultExpanded[r.item_id] = true })
      setExpandedRows(defaultExpanded)
      setLoading(false)
    }
    fetchData()
  }, [ticker, reportType, periodFilter])

  const dataMap = useMemo(() => {
    const m = {}; data.forEach(r => { m[r.item_id] = r }); return m
  }, [data])

  const isVisible = (row) => {
    if (row.levels === 0) return true
    let curr = dataMap[row.parent_id]
    while (curr) {
      if (!expandedRows[curr.item_id]) return false
      curr = dataMap[curr.parent_id]
    }
    return true
  }

  const toggle = (id) => setExpandedRows(p => ({ ...p, [id]: !p[id] }))

  // ── Mini Bar Chart ─────────────────────────────────────────────────────
  const MiniBarChart = ({ values }) => {
    if (!values || values.length === 0) return <span className="no-chart">–</span>
    const maxVal = Math.max(...values.map(Math.abs)) || 1
    const hasNeg = values.some(v => v < 0)
    return (
      <div className={`mini-bar-container${hasNeg ? ' mixed' : ''}`}>
        {values.map((v, i) => {
          const pct = Math.min(90, Math.max(4, (Math.abs(v) / maxVal) * 90))
          return (
            <div key={i} className="bar-col" title={formatNumber(v)}>
              <div className="bar-pos-area">
                {v >= 0 && <div className="bar-fill pos" style={{ height: `${pct}%` }} />}
              </div>
              <div className="bar-neg-area">
                {v < 0 && <div className="bar-fill neg" style={{ height: `${pct}%` }} />}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  // ── Stat summary cards ─────────────────────────────────────────────────
  const statSummary = useMemo(() => {
    if (!data.length || !periods.length) return null
    const latestPeriod = periods[0]
    const rowCount = data.length
    const filledCount = data.filter(r => r.periods_data?.[latestPeriod] != null).length
    const coverage = rowCount > 0 ? Math.round((filledCount / rowCount) * 100) : 0
    return { latestPeriod, rowCount, filledCount, coverage }
  }, [data, periods])

  return (
    <div className="app">
      {/* ═══ Header ═══ */}
      <header className="app-header">
        <div className="brand">
          <svg className="brand-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          <span className="brand-name">Finsang Terminal</span>
          <span className="brand-version">v2.0</span>
        </div>
        <div className="header-right">
          <span className="data-source">Vietcap Data</span>
          <span className="ticker-badge">{ticker}:{currentTicker.exchange}</span>
        </div>
      </header>

      {/* ═══ Company Info Bar ═══ */}
      <div className="company-bar">
        <div className="company-info">
          <span className="company-name">{currentTicker.name}</span>
          <span className="company-sub">Báo cáo tài chính · Đơn vị: Triệu VND</span>
        </div>
        <select
          id="ticker-select"
          className="stock-select"
          value={ticker}
          onChange={e => setTicker(e.target.value)}
        >
          {TICKERS.map(t => (
            <option key={t.code} value={t.code}>{t.code} – {t.name}</option>
          ))}
        </select>
      </div>

      {/* ═══ Report Tabs ═══ */}
      <div className="tabs-row">
        <div className="tabs" role="tablist">
          {REPORT_TABS.map(t => (
            <button
              key={t.id}
              id={`tab-${t.id}`}
              role="tab"
              aria-selected={reportType === t.id}
              className={`tab${reportType === t.id ? ' active' : ''}`}
              onClick={() => setReportType(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="period-toggle" role="radiogroup" aria-label="Period filter">
          {PERIOD_FILTERS.map(pf => (
            <button
              key={pf.id}
              id={`period-${pf.id}`}
              role="radio"
              aria-checked={periodFilter === pf.id}
              className={`period-btn${periodFilter === pf.id ? ' active' : ''}`}
              onClick={() => setPeriodFilter(pf.id)}
            >
              {pf.label}
            </button>
          ))}
        </div>
      </div>

      {/* ═══ Stats Bar ═══ */}
      {statSummary && !loading && (
        <div className="stats-bar">
          <div className="stat-chip">
            <span className="stat-label">Kỳ mới nhất</span>
            <span className="stat-value">{statSummary.latestPeriod}</span>
          </div>
          <div className="stat-chip">
            <span className="stat-label">Dòng dữ liệu</span>
            <span className="stat-value">{statSummary.filledCount}/{statSummary.rowCount}</span>
          </div>
          <div className="stat-chip">
            <span className="stat-label">Coverage</span>
            <span className={`stat-value ${statSummary.coverage >= 80 ? 'stat-good' : 'stat-warn'}`}>
              {statSummary.coverage}%
            </span>
          </div>
        </div>
      )}

      {/* ═══ Data Table ═══ */}
      <div className="table-wrap">
        {loading ? (
          <div className="state-msg">
            <div className="loader" />
            <span>Đang tải dữ liệu...</span>
          </div>
        ) : data.length === 0 ? (
          <div className="state-msg">
            <span>Không có dữ liệu {currentTab.label} cho {ticker}</span>
          </div>
        ) : (
          <table className="fin-table">
            <thead>
              <tr>
                <th className="th-item">Chỉ tiêu</th>
                <th className="th-chart" />
                {periods.map(p => <th key={p} className="th-val">{formatPeriodLabel(p)}</th>)}
              </tr>
            </thead>
            <tbody>
              {data.map((row, idx) => {
                if (!isVisible(row)) return null
                const hasChildren = idx < data.length - 1 && data[idx + 1].levels > row.levels
                const isOpen = !!expandedRows[row.item_id]
                const chartVals = periods.map(p => row.periods_data?.[p] || 0)
                const major = isMajorHeading(row)
                const displayLabel = major ? (row.item || '').toUpperCase() : (row.item || '')

                return (
                  <tr
                    key={row.item_id || idx}
                    className={`fin-row${major ? ' row-major' : ' row-child'} lv${Math.min(row.levels, 4)}`}
                  >
                    <td className="td-item">
                      <div className="item-cell" style={{ paddingLeft: `${6 + row.levels * 16}px` }}>
                        {hasChildren
                          ? <button className="tog" onClick={() => toggle(row.item_id)} aria-label="Toggle expand">
                            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                              {isOpen
                                ? <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="1.5" fill="none" />
                                : <path d="M4 2L8 6L4 10" stroke="currentColor" strokeWidth="1.5" fill="none" />
                              }
                            </svg>
                          </button>
                          : <span className="tog-ph" />
                        }
                        <span className={`label${major ? ' label-major' : ''}`}>{displayLabel}</span>
                      </div>
                    </td>
                    <td className="td-chart">
                      {!major && <MiniBarChart values={chartVals} />}
                    </td>
                    {periods.map(p => {
                      const v = row.periods_data?.[p]
                      return (
                        <td key={p} className={`td-val${v < 0 ? ' neg' : ''}`}>
                          {formatNumber(v)}
                        </td>
                      )
                    })}
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* ═══ Footer ═══ */}
      <footer className="app-footer">
        <span>Finsang Terminal v2.0 · Powered by Vietcap Data Pipeline</span>
        <span className="footer-source">Source: Version 2 B.L.A.S.T Framework</span>
      </footer>
    </div>
  )
}
