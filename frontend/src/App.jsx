import { useEffect, useState, useMemo } from 'react'
import { supabase } from './supabaseClient'
import './App.css'

// ─── CFO Note ──────────────────────────────────────────────────────────────
// DB stores values in Tỷ VND. Display in Triệu VND (×1000) to match Fireant.
// Columns sorted newest → oldest (Simplize / Fireant standard).
// Mini bar chart: newest period bars on LEFT → oldest on RIGHT (newest-first).
// ────────────────────────────────────────────────────────────────────────────

const STOCK_NAMES = {
  'NLG': 'CTCP Đầu tư Nam Long',
  'VND': 'CTCP Chứng khoán VNDirect',
  'SSI': 'CTCP Chứng khoán SSI',
  'FPT': 'CTCP Tập đoàn FPT',
  'HPG': 'CTCP Tập đoàn Hoà Phát',
}

// Normalize legacy period formats: "Q4/2025" → "2025-Q4"
function normalizePeriod(p) {
  if (!p) return p
  const m = p.match(/^Q(\d)\/(\d{4})$/)
  if (m) return `${m[2]}-Q${m[1]}`
  return p
}

// Format period label for display: "2025-Q4" → "Q4/2025"
function formatPeriodLabel(p) {
  if (!p) return p
  const match = p.match(/^(\d{4})-Q(\d)$/)
  if (match) return `Q${match[2]}/${match[1]}`
  if (p.endsWith('-0')) return p.replace('-0', '')
  return p
}

// Number formatter: Tỷ VND × 1000 = Triệu VND, comma thousand separator
function formatNumber(num) {
  if (num === null || num === undefined || num === 0) return '–'
  const inMillions = num * 1000
  // Format: 1,234,567 (comma thousands, dot decimal)
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0,
  }).format(inMillions)
}

// Is this row a major heading that gets uppercase treatment?
function isMajorHeading(row) {
  return (
    row.levels === 0 ||
    row.item.startsWith('TỔNG') ||
    row.item.startsWith('Cộng') ||
    /^[IVX]+\./.test(row.item)
  )
}

export default function App() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [stockName, setStockName] = useState('NLG')
  const [reportType, setReportType] = useState('CDKT')
  const [periods, setPeriods] = useState([])
  const [expandedRows, setExpandedRows] = useState({})

  useEffect(() => {
    async function fetchData() {
      setLoading(true)
      const tableMap = {
        'KQKD': 'income_statement_wide',
        'CDKT': 'balance_sheet_wide',
        'LCTT_TT': 'cash_flow_wide',
        'LCTT_GT': 'cash_flow_wide',
        'CSTO': 'financial_ratios_wide',
      }
      const tableName = tableMap[reportType] || 'balance_sheet_wide'

      const { data: reports, error } = await supabase
        .from(tableName)
        .select('*')
        .eq('stock_name', stockName)
        .order('row_number', { ascending: true })

      if (error) {
        console.error(error)
        setData([]); setPeriods([]); setLoading(false); return
      }
      if (!reports || reports.length === 0) {
        setData([]); setPeriods([]); setLoading(false); return
      }

      let filtered = reports
      if (reportType === 'LCTT_TT') filtered = reports.filter(r => r.item_id?.startsWith('lctttt'))
      if (reportType === 'LCTT_GT') filtered = reports.filter(r => r.item_id?.startsWith('lcttgt'))

      // Normalize period keys inside periods_data
      const normalized = filtered.map(row => {
        const rawPd = row.periods_data || {}
        const pd = {}
        Object.entries(rawPd).forEach(([k, v]) => { pd[normalizePeriod(k)] = v })
        return { ...row, periods_data: pd }
      })

      // Build parent tree
      const processed = normalized.map((row, i) => {
        let parent_id = null
        if (row.levels > 0) {
          for (let j = i - 1; j >= 0; j--) {
            if (normalized[j].levels === row.levels - 1) { parent_id = normalized[j].item_id; break }
          }
        }
        return { ...row, parent_id }
      })

      setData(processed)

      // Collect all unique periods, sort newest → oldest (Z→A)
      const allPeriods = new Set()
      processed.forEach(r => Object.keys(r.periods_data || {}).forEach(p => allPeriods.add(p)))
      const cols = Array.from(allPeriods).sort((a, b) => b.localeCompare(a)).slice(0, 8)
      setPeriods(cols)

      // Auto-expand L0 + L1
      const defaultExpanded = {}
      processed.forEach(r => { if (r.levels <= 1) defaultExpanded[r.item_id] = true })
      setExpandedRows(defaultExpanded)
      setLoading(false)
    }
    fetchData()
  }, [stockName, reportType])

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

  // ── Simplize Mini Bar Chart ────────────────────────────────────────────
  // periods prop is already newest→oldest. Chart displays newest LEFT → oldest RIGHT.
  // Positive bars grow UP from the baseline, negative bars grow DOWN.
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
              {/* Positive half — grows UP from baseline */}
              <div className="bar-pos-area">
                {v >= 0 && <div className="bar-fill pos" style={{ height: `${pct}%` }} />}
              </div>
              {/* Negative half — grows DOWN from baseline */}
              <div className="bar-neg-area">
                {v < 0 && <div className="bar-fill neg" style={{ height: `${pct}%` }} />}
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="brand">
          <span className="brand-icon">⚡</span>
          <span className="brand-name">Finsang Terminal</span>
        </div>
        <span className="ticker-badge">{stockName}:HSX</span>
      </header>

      {/* Company title */}
      <div className="company-bar">
        <span className="company-name">{STOCK_NAMES[stockName]}</span>
        <span className="company-sub">Báo cáo tài chính · Đơn vị: Triệu VND</span>
      </div>

      {/* Controls */}
      <div className="controls">
        <select className="stock-select" value={stockName} onChange={e => setStockName(e.target.value)}>
          {Object.entries(STOCK_NAMES).map(([code, name]) => (
            <option key={code} value={code}>{code} – {name.split(' ').slice(-2).join(' ')}</option>
          ))}
        </select>
      </div>

      {/* Tabs */}
      <div className="tabs">
        {[
          { id: 'CDKT', label: 'Cân đối kế toán' },
          { id: 'KQKD', label: 'Kết quả kinh doanh' },
          { id: 'LCTT_TT', label: 'LCTT trực tiếp' },
          { id: 'LCTT_GT', label: 'LCTT gián tiếp' },
          { id: 'CSTO', label: 'Chỉ số tài chính' },
        ].map(t => (
          <button key={t.id} className={`tab${reportType === t.id ? ' active' : ''}`} onClick={() => setReportType(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="table-wrap">
        {loading ? (
          <div className="state-msg">Đang tải...</div>
        ) : data.length === 0 ? (
          <div className="state-msg">Không có dữ liệu {reportType} cho {stockName}</div>
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
                // Newest-first chart values align with column order
                const chartVals = periods.map(p => row.periods_data?.[p] || 0)
                const major = isMajorHeading(row)
                const displayLabel = major ? row.item.toUpperCase() : row.item

                return (
                  <tr key={row.item_id} className={`fin-row${major ? ' row-major' : ' row-child'} lv${Math.min(row.levels, 4)}`}>
                    <td className="td-item">
                      <div className="item-cell" style={{ paddingLeft: `${6 + row.levels * 16}px` }}>
                        {hasChildren
                          ? <button className="tog" onClick={() => toggle(row.item_id)}>{isOpen ? '▾' : '▸'}</button>
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
    </div>
  )
}
