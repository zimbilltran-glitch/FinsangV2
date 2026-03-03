/**
 * BankKeyInfo.jsx — V3 P5.1
 * Sector-aware Key Information box.
 * Shows different metrics based on sector: bank / sec / normal
 *
 * Props:
 *   overview: company_overview row
 *   getRatioValue: fn(itemId) → number|null
 *   getBsLatestValue: fn(itemId) → number|null (from balance_sheet_wide)
 *   sector: 'bank' | 'sec' | 'normal'
 */

function fmt(val, divisor = 1, suffix = '', decimals = 1) {
    if (val == null) return '—'
    const n = val / divisor
    return n.toLocaleString('en-US', {
        maximumFractionDigits: decimals,
        minimumFractionDigits: decimals,
    }) + suffix
}

function InfoRow({ label, value, highlight }) {
    return (
        <div className="key-info-row">
            <span className="key-info-label">{label}</span>
            <span className={`key-info-value ${highlight || ''}`}>{value}</span>
        </div>
    )
}

export default function BankKeyInfo({ overview, getRatioValue, getBsLatestValue, sector = 'normal' }) {
    if (!overview && !getRatioValue) return null

    const nim = overview?.nim
    const deposits = overview?.total_deposits
    const loans = overview?.total_loans
    const ldr = overview?.loan_to_deposit
    const pe = overview?.pe_ratio
    const pb = overview?.pb_ratio
    const roe = overview?.roe
    const divY = overview?.dividend_yield
    const mktCap = overview?.market_cap

    // BS data (in VND đồng)
    const tsnh = getBsLatestValue?.('cdkt_tai_san_ngan_han')
    const tsdh = getBsLatestValue?.('cdkt_tai_san_dai_han')
    const npt = getBsLatestValue?.('cdkt_no_phai_tra')
    const vcsh = getBsLatestValue?.('cdkt_von_chu_so_huu')

    // Calculated
    const totalAssets = tsnh && tsdh ? tsnh + tsdh : null
    const deRatio = npt && vcsh && vcsh !== 0 ? npt / vcsh : null

    const sectionTitle = sector === 'bank' ? 'Thông tin ngân hàng'
        : sector === 'sec' ? 'Thông tin CTCK'
            : 'Thông tin tài chính'

    let metrics = []

    if (sector === 'bank') {
        metrics = [
            { label: 'NIM (Biên lãi ròng)', value: nim != null ? `${nim.toFixed(2)}%` : '—' },
            { label: 'Tổng tiền gửi KH', value: fmt(deposits, 1e12, ' Nghìn Tỷ', 0) },
            { label: 'Tổng cho vay KH', value: fmt(loans, 1e12, ' Nghìn Tỷ', 0) },
            { label: 'LDR (Cho vay/Huy động)', value: ldr != null ? `${(ldr * 100).toFixed(1)}%` : '—', highlight: ldr != null && ldr > 1.1 ? 'val-warn' : '' },
            { label: 'P/B', value: pb != null ? `${pb.toFixed(1)}x` : '—' },
            { label: 'Cổ tức', value: divY != null ? `${divY.toFixed(1)}%` : '—' },
        ]
    } else if (sector === 'sec') {
        metrics = [
            { label: 'P/E', value: pe != null ? `${pe.toFixed(1)}x` : '—' },
            { label: 'P/B', value: pb != null ? `${pb.toFixed(1)}x` : '—' },
            { label: 'ROE', value: roe != null ? `${(roe * 100).toFixed(1)}%` : '—' },
            { label: 'Tổng tài sản', value: fmt(totalAssets, 1e9, ' Tỷ', 0) },
            { label: 'D/E', value: deRatio != null ? `${deRatio.toFixed(2)}x` : '—' },
            { label: 'Cổ tức', value: divY != null ? `${divY.toFixed(1)}%` : '—' },
        ]
    } else {
        metrics = [
            { label: 'P/E', value: pe != null ? `${pe.toFixed(1)}x` : '—' },
            { label: 'P/B', value: pb != null ? `${pb.toFixed(1)}x` : '—' },
            { label: 'D/E (Nợ/Vốn CSH)', value: deRatio != null ? `${deRatio.toFixed(2)}x` : '—', highlight: deRatio != null && deRatio > 2 ? 'val-warn' : '' },
            { label: 'Tổng tài sản', value: fmt(totalAssets, 1e9, ' Tỷ', 0) },
            { label: 'Vốn chủ sở hữu', value: fmt(vcsh, 1e9, ' Tỷ', 0) },
            { label: 'Cổ tức', value: divY != null ? `${divY.toFixed(1)}%` : '—' },
        ]
    }

    return (
        <div className="key-info-card">
            <p className="panel-label">{sectionTitle}</p>
            <div className="key-info-grid">
                {metrics.map((m, i) => (
                    <InfoRow key={i} label={m.label} value={m.value} highlight={m.highlight} />
                ))}
            </div>
        </div>
    )
}
