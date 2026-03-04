/**
 * DebtEquityHistoryChart.jsx — V3 P5.3
 * Pure SVG dual line+area chart: Debt vs Equity over 5-8 years.
 *
 * Props:
 *   getBsAnnualSeries: fn(itemId) → [{ year, value }, ...]
 */

function fmtTy(val) {
    if (val == null) return '—'
    return (val / 1e9).toLocaleString('en-US', { maximumFractionDigits: 0 })
}

export default function DebtEquityHistoryChart({ getBsAnnualSeries, sector }) {
    // Try normal IDs first, fallback to bank IDs
    let debtSeries = getBsAnnualSeries?.('cdkt_no_phai_tra') || []
    let equitySeries = getBsAnnualSeries?.('cdkt_von_chu_so_huu') || []

    if (sector === 'bank' || debtSeries.length === 0) {
        const bankDebt = getBsAnnualSeries?.('cdkt_bank_tong_no_phai_tra') || getBsAnnualSeries?.('cdkt_bank_no_phai_tra') || []
        const bankEq = getBsAnnualSeries?.('cdkt_bank_von_chu_so_huu') || []
        if (bankDebt.length > 0) debtSeries = bankDebt
        if (bankEq.length > 0) equitySeries = bankEq
    }

    // Sec fallback
    if (sector === 'sec' || debtSeries.length === 0) {
        const secDebt = getBsAnnualSeries?.('cdkt_sec_no_phai_tra') || []
        const secEq = getBsAnnualSeries?.('cdkt_sec_von_chu_so_huu_1') || getBsAnnualSeries?.('cdkt_sec_von_chu_so_huu') || []
        if (secDebt.length > 0) debtSeries = secDebt
        if (secEq.length > 0) equitySeries = secEq
    }

    if (debtSeries.length === 0 && equitySeries.length === 0) return null

    // Merge years
    const allYears = [...new Set([...debtSeries.map(d => d.year), ...equitySeries.map(d => d.year)])]
        .sort()
        .slice(-8) // Latest 8 years

    if (allYears.length < 2) return null

    const debtMap = {}; debtSeries.forEach(d => { debtMap[d.year] = d.value })
    const eqMap = {}; equitySeries.forEach(d => { eqMap[d.year] = d.value })

    const debtVals = allYears.map(y => debtMap[y] || 0)
    const eqVals = allYears.map(y => eqMap[y] || 0)
    const allVals = [...debtVals, ...eqVals]
    const maxVal = Math.max(...allVals)
    const minVal = 0

    const W = 500, H = 200
    const padL = 60, padR = 20, padT = 20, padB = 40
    const chartW = W - padL - padR
    const chartH = H - padT - padB
    const n = allYears.length

    const xScale = (i) => padL + (i / (n - 1)) * chartW
    const yScale = (v) => padT + chartH - (((v - minVal) / (maxVal - minVal || 1)) * chartH)

    // Build path strings
    const debtPoints = debtVals.map((v, i) => `${xScale(i)},${yScale(v)}`)
    const eqPoints = eqVals.map((v, i) => `${xScale(i)},${yScale(v)}`)

    const debtLine = `M${debtPoints.join('L')}`
    const eqLine = `M${eqPoints.join('L')}`

    // Area fills
    const baseline = yScale(0)
    const debtArea = `${debtLine}L${xScale(n - 1)},${baseline}L${xScale(0)},${baseline}Z`
    const eqArea = `${eqLine}L${xScale(n - 1)},${baseline}L${xScale(0)},${baseline}Z`

    // Y-axis ticks (4 ticks)
    const yTicks = [0, 0.25, 0.5, 0.75, 1].map(pct => {
        const val = minVal + pct * (maxVal - minVal)
        return { y: yScale(val), label: fmtTy(val) }
    })

    return (
        <div className="de-history-card">
            <p className="panel-label">Lịch sử Nợ & Vốn chủ sở hữu (Tỷ VND)</p>
            <svg viewBox={`0 0 ${W} ${H}`} className="de-chart-svg">
                {/* Grid lines */}
                {yTicks.map((t, i) => (
                    <g key={i}>
                        <line x1={padL} x2={W - padR} y1={t.y} y2={t.y} stroke="rgba(255,255,255,0.06)" />
                        <text x={padL - 6} y={t.y + 3} textAnchor="end" className="de-axis-label">{t.label}</text>
                    </g>
                ))}

                {/* Area fills */}
                <path d={debtArea} fill="#ef4444" opacity="0.12" />
                <path d={eqArea} fill="#3b82f6" opacity="0.12" />

                {/* Lines */}
                <path d={debtLine} fill="none" stroke="#ef4444" strokeWidth="2" strokeLinejoin="round" />
                <path d={eqLine} fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinejoin="round" />

                {/* Data points */}
                {debtVals.map((v, i) => (
                    <circle key={`d${i}`} cx={xScale(i)} cy={yScale(v)} r="3" fill="#ef4444">
                        <title>{allYears[i]}: Nợ {fmtTy(v)} Tỷ</title>
                    </circle>
                ))}
                {eqVals.map((v, i) => (
                    <circle key={`e${i}`} cx={xScale(i)} cy={yScale(v)} r="3" fill="#3b82f6">
                        <title>{allYears[i]}: VCSH {fmtTy(v)} Tỷ</title>
                    </circle>
                ))}

                {/* X-axis labels */}
                {allYears.map((yr, i) => (
                    <text key={yr} x={xScale(i)} y={H - 10} textAnchor="middle" className="de-axis-label">{yr}</text>
                ))}

                {/* Legend */}
                <g transform={`translate(${padL}, ${H - 4})`}>
                    <line x1="0" x2="16" y1="0" y2="0" stroke="#ef4444" strokeWidth="2" />
                    <text x="20" y="4" className="de-legend-text">Nợ phải trả</text>
                    <line x1="110" x2="126" y1="0" y2="0" stroke="#3b82f6" strokeWidth="2" />
                    <text x="130" y="4" className="de-legend-text">Vốn CSH</text>
                </g>
            </svg>
        </div>
    )
}
