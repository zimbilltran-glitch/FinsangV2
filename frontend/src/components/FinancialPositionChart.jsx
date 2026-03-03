/**
 * FinancialPositionChart.jsx — V3 P5.2
 * Pure SVG stacked horizontal bar chart: Assets vs Liabilities + Equity.
 *
 * Props:
 *   getBsLatestValue: fn(itemId) → number|null (VND đồng)
 */

function fmtTy(val) {
    if (val == null) return '—'
    return (val / 1e9).toLocaleString('en-US', { maximumFractionDigits: 0 }) + ' Tỷ'
}

export default function FinancialPositionChart({ getBsLatestValue, sector }) {
    // Normal companies
    let tsnh = getBsLatestValue?.('cdkt_tai_san_ngan_han') || 0
    let tsdh = getBsLatestValue?.('cdkt_tai_san_dai_han') || 0
    let nnh = getBsLatestValue?.('cdkt_no_ngan_han') || 0
    let ndh = getBsLatestValue?.('cdkt_no_dai_han') || 0
    let vcsh = getBsLatestValue?.('cdkt_von_chu_so_huu') || 0

    // Bank fallback: use bank-specific BS items
    const isBank = sector === 'bank'
    if (isBank || (tsnh === 0 && tsdh === 0)) {
        const bankTotalAssets = getBsLatestValue?.('cdkt_bank_tong_tai_san') || 0
        const bankTotalDebt = getBsLatestValue?.('cdkt_bank_tong_no_phai_tra') || 0
        const bankVCSH = getBsLatestValue?.('cdkt_bank_von_chu_so_huu') || 0
        if (bankTotalAssets > 0) {
            // For banks: show total assets as single bar, debt+VCSH as split bar
            tsnh = bankTotalAssets  // Use total as "current assets" for display
            tsdh = 0
            nnh = bankTotalDebt
            ndh = 0
            vcsh = bankVCSH
        }
    }

    const totalAssets = tsnh + tsdh
    const totalLiabEq = nnh + ndh + vcsh

    if (totalAssets === 0 && totalLiabEq === 0) return null

    const maxVal = Math.max(totalAssets, totalLiabEq)
    if (maxVal === 0) return null

    const W = 500, H = 120, barH = 32, gap = 20
    const y1 = 30, y2 = y1 + barH + gap

    // Assets bar
    const aTsnhW = (tsnh / maxVal) * W
    const aTsdhW = (tsdh / maxVal) * W

    // Liabilities bar
    const lNnhW = (nnh / maxVal) * W
    const lNdhW = (ndh / maxVal) * W
    const lVcshW = (vcsh / maxVal) * W

    return (
        <div className="fp-chart-card">
            <p className="panel-label">Cấu trúc tài sản & nguồn vốn</p>
            <svg viewBox={`0 0 ${W} ${y2 + barH + 30}`} className="fp-chart-svg">
                {/* Assets Bar */}
                <text x="0" y={y1 - 8} className="fp-label">Tài sản</text>
                <rect x="0" y={y1} width={aTsnhW} height={barH} rx="3" fill="#3b82f6" opacity="0.7">
                    <title>TS ngắn hạn: {fmtTy(tsnh)}</title>
                </rect>
                <rect x={aTsnhW} y={y1} width={aTsdhW} height={barH} rx="3" fill="#1d4ed8" opacity="0.8">
                    <title>TS dài hạn: {fmtTy(tsdh)}</title>
                </rect>
                <text x={aTsnhW + aTsdhW + 6} y={y1 + barH / 2 + 4} className="fp-val">{fmtTy(totalAssets)}</text>

                {/* Liabilities + Equity Bar */}
                <text x="0" y={y2 - 8} className="fp-label">Nguồn vốn</text>
                <rect x="0" y={y2} width={lNnhW} height={barH} rx="3" fill="#ef4444" opacity="0.6">
                    <title>Nợ ngắn hạn: {fmtTy(nnh)}</title>
                </rect>
                <rect x={lNnhW} y={y2} width={lNdhW} height={barH} rx="3" fill="#dc2626" opacity="0.7">
                    <title>Nợ dài hạn: {fmtTy(ndh)}</title>
                </rect>
                <rect x={lNnhW + lNdhW} y={y2} width={lVcshW} height={barH} rx="3" fill="#22c55e" opacity="0.7">
                    <title>Vốn CSH: {fmtTy(vcsh)}</title>
                </rect>
                <text x={lNnhW + lNdhW + lVcshW + 6} y={y2 + barH / 2 + 4} className="fp-val">{fmtTy(totalLiabEq)}</text>

                {/* Legend */}
                <g transform={`translate(0, ${y2 + barH + 16})`}>
                    <rect width="10" height="10" fill="#3b82f6" opacity="0.7" rx="2" />
                    <text x="14" y="9" className="fp-legend">TS ngắn hạn</text>
                    <rect x="90" width="10" height="10" fill="#1d4ed8" opacity="0.8" rx="2" />
                    <text x="104" y="9" className="fp-legend">TS dài hạn</text>
                    <rect x="175" width="10" height="10" fill="#ef4444" opacity="0.6" rx="2" />
                    <text x="189" y="9" className="fp-legend">Nợ NH</text>
                    <rect x="240" width="10" height="10" fill="#dc2626" opacity="0.7" rx="2" />
                    <text x="254" y="9" className="fp-legend">Nợ DH</text>
                    <rect x="300" width="10" height="10" fill="#22c55e" opacity="0.7" rx="2" />
                    <text x="314" y="9" className="fp-legend">Vốn CSH</text>
                </g>
            </svg>
        </div>
    )
}
