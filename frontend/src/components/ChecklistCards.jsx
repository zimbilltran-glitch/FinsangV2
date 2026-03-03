/**
 * ChecklistCards.jsx — V3 P2.5 + P5.4
 * Pass/fail checklist cards for the 360 Overview tab.
 * - Expandable cards with narrative descriptions
 * - Icon row summary header (✅❌ strip)
 * - Sector-aware checks (bank/sec/normal)
 *
 * Props:
 *   overview:      company_overview row (may be null)
 *   getRatioValue: fn(itemId) → number|null from financial_ratios_wide
 *   sector:        'bank' | 'sec' | 'normal'
 */
import { useState } from 'react'

function CheckItem({ passed, label, detail, narrative, loading }) {
    const [expanded, setExpanded] = useState(false)

    if (loading) {
        return (
            <div className="check-item check-loading">
                <span className="check-icon">⏳</span>
                <div className="check-text">
                    <span className="check-label">{label}</span>
                </div>
            </div>
        )
    }

    const icon = passed === true ? '✅' : passed === false ? '❌' : '➖'
    const cls = passed === true ? 'check-pass' : passed === false ? 'check-fail' : 'check-neutral'
    const hasNarrative = !!narrative

    return (
        <div
            className={`check-item ${cls} ${hasNarrative ? 'check-expandable' : ''} ${expanded ? 'check-expanded' : ''}`}
            onClick={hasNarrative ? () => setExpanded(e => !e) : undefined}
            style={hasNarrative ? { cursor: 'pointer' } : undefined}
        >
            <span className="check-icon">{icon}</span>
            <div className="check-text">
                <div className="check-label-row">
                    <span className="check-label">{label}</span>
                    {hasNarrative && (
                        <span className="check-expand-arrow">{expanded ? '▾' : '▸'}</span>
                    )}
                </div>
                {detail && <span className="check-detail">{detail}</span>}
                {expanded && narrative && (
                    <div className="check-narrative">{narrative}</div>
                )}
            </div>
        </div>
    )
}

// ── Helper: safe number ───────────────────────────────────────────────────────
function num(v) {
    const n = parseFloat(v)
    return isNaN(n) ? null : n
}

// ── Build checks per sector ───────────────────────────────────────────────────
function buildChecks(overview, getRatioValue, sector) {
    const pe = num(overview?.pe_ratio)
    const pb = num(overview?.pb_ratio)
    const divY = num(overview?.dividend_yield)
    const mktCap = num(overview?.market_cap)

    // Ratios from financial_ratios_wide (item_id from metrics.py)
    const revGrowth = getRatioValue('g7_1')   // % YoY revenue growth
    const lnGrowth = getRatioValue('g7_2')   // % YoY net profit growth
    const ocf = getRatioValue('g4_1')         // LCTT từ HĐKD

    // Snowflake scores (if available)
    const scoreHealth = num(overview?.score_health)
    const scoreFuture = num(overview?.score_future)

    // Bank specific
    const nim = num(overview?.nim)
    const ldr = num(overview?.loan_to_deposit)

    const SECTOR_PE = { bank: 12, sec: 14, normal: 16 }
    const benchPE = SECTOR_PE[sector] ?? 16

    if (sector === 'bank') {
        return [
            {
                label: 'P/B thấp hơn trung bình ngành',
                passed: pb != null ? pb < 1.5 : null,
                detail: pb != null ? `P/B = ${pb.toFixed(1)}x (chuẩn: < 1.5x)` : null,
                narrative: 'Ngân hàng thường được định giá qua P/B. Dưới 1.5x cho thấy cổ phiếu đang giao dịch gần giá trị sổ sách.',
            },
            {
                label: 'NIM (Biên lãi ròng) > 3%',
                passed: nim != null ? nim > 3 : null,
                detail: nim != null ? `NIM = ${nim.toFixed(2)}%` : null,
                narrative: 'NIM đo lường hiệu quả cho vay. NIM > 3% cho thấy ngân hàng có biên lợi nhuận lãi thuần khỏe mạnh.',
            },
            {
                label: 'Lợi nhuận tăng trưởng',
                passed: lnGrowth != null ? lnGrowth > 0 : null,
                detail: lnGrowth != null ? `Tăng trưởng LN: ${lnGrowth > 0 ? '+' : ''}${lnGrowth?.toFixed(1)}% YoY` : null,
                narrative: 'Lợi nhuận ròng tăng trưởng dương cho thấy hoạt động kinh doanh ngân hàng đang mở rộng.',
            },
            {
                label: 'Tỷ lệ cho vay/huy động hợp lý',
                passed: ldr != null ? ldr < 1.1 : null,
                detail: ldr != null ? `LDR = ${(ldr * 100).toFixed(1)}%` : null,
                narrative: 'LDR dưới 110% cho thấy ngân hàng không quá mạo hiểm trong cho vay so với nguồn huy động.',
            },
            {
                label: 'Sức khỏe tài chính tốt',
                passed: scoreHealth != null ? scoreHealth >= 3 : null,
                detail: scoreHealth != null ? `Điểm sức khỏe: ${scoreHealth.toFixed(1)}/5` : null,
                narrative: 'Điểm sức khỏe từ 3/5 trở lên phản ánh bảng cân đối vững chắc.',
            },
            {
                label: 'Cổ tức ổn định',
                passed: divY != null ? divY > 0 : null,
                detail: divY != null ? `Tỷ suất cổ tức: ${divY.toFixed(1)}%` : null,
                narrative: 'Cổ tức dương cho thấy ngân hàng có khả năng sinh lời đủ để chia sẻ cho cổ đông.',
            },
        ]
    }

    if (sector === 'sec') {
        return [
            {
                label: 'P/E thấp hơn trung bình ngành',
                passed: pe != null ? pe < benchPE : null,
                detail: pe != null ? `P/E = ${pe.toFixed(1)}x (chuẩn: ${benchPE}x)` : null,
                narrative: 'P/E dưới mức trung bình ngành chứng khoán (14x) cho thấy định giá hấp dẫn.',
            },
            {
                label: 'Doanh thu tăng trưởng',
                passed: revGrowth != null ? revGrowth > 0 : null,
                detail: revGrowth != null ? `Tăng trưởng DT: ${revGrowth > 0 ? '+' : ''}${revGrowth?.toFixed(1)}% YoY` : null,
                narrative: 'Doanh thu tăng trưởng cho thấy thị phần môi giới hoặc tự doanh đang mở rộng.',
            },
            {
                label: 'Lợi nhuận tăng trưởng',
                passed: lnGrowth != null ? lnGrowth > 0 : null,
                detail: lnGrowth != null ? `Tăng trưởng LN: ${lnGrowth > 0 ? '+' : ''}${lnGrowth?.toFixed(1)}% YoY` : null,
                narrative: 'Lợi nhuận ròng tăng cho thấy quản lý chi phí tốt và hoạt động kinh doanh hiệu quả.',
            },
            {
                label: 'Triển vọng tăng trưởng tốt',
                passed: scoreFuture != null ? scoreFuture >= 3 : null,
                detail: scoreFuture != null ? `Điểm tương lai: ${scoreFuture.toFixed(1)}/5` : null,
                narrative: 'Điểm triển vọng từ 3/5 trở lên báo hiệu kỳ vọng tăng trưởng tích cực.',
            },
        ]
    }

    // Normal (non-financial)
    return [
        {
            label: 'P/E thấp hơn trung bình ngành',
            passed: pe != null ? pe < benchPE : null,
            detail: pe != null ? `P/E = ${pe.toFixed(1)}x (chuẩn VN30: ${benchPE}x)` : null,
            narrative: 'P/E dưới mức trung bình VN30 cho thấy cổ phiếu có thể đang được định giá hấp dẫn.',
        },
        {
            label: 'Doanh thu tăng trưởng',
            passed: revGrowth != null ? revGrowth > 0 : null,
            detail: revGrowth != null ? `${revGrowth > 0 ? '+' : ''}${revGrowth?.toFixed(1)}% YoY` : null,
            narrative: 'Doanh thu tăng trưởng dương phản ánh khả năng mở rộng thị trường và tăng sức cạnh tranh.',
        },
        {
            label: 'Lợi nhuận tăng trưởng',
            passed: lnGrowth != null ? lnGrowth > 0 : null,
            detail: lnGrowth != null ? `${lnGrowth > 0 ? '+' : ''}${lnGrowth?.toFixed(1)}% YoY` : null,
            narrative: 'Tăng trưởng lợi nhuận cho thấy doanh nghiệp đang kiểm soát chi phí tốt và cải thiện biên lợi nhuận.',
        },
        {
            label: 'Dòng tiền hoạt động dương',
            passed: ocf != null ? ocf > 0 : null,
            detail: ocf != null
                ? `LCTT HĐKD: ${ocf > 0 ? '+' : ''}${(ocf / 1_000_000_000).toFixed(0)} Tỷ VND`
                : null,
            narrative: 'Dòng tiền hoạt động dương cho thấy doanh nghiệp tạo ra tiền thật từ kinh doanh, không chỉ lợi nhuận trên sổ sách.',
        },
        {
            label: 'Cổ tức có thanh toán',
            passed: divY != null ? divY > 0 : null,
            detail: divY != null ? `Tỷ suất cổ tức: ${divY.toFixed(1)}%` : null,
            narrative: 'Cổ tức dương cho thấy ban lãnh đạo cam kết chia sẻ lợi nhuận với cổ đông.',
        },
        {
            label: 'Sức khỏe tài chính tốt',
            passed: scoreHealth != null ? scoreHealth >= 3 : null,
            detail: scoreHealth != null ? `Điểm sức khỏe: ${scoreHealth.toFixed(1)}/5` : null,
            narrative: 'Điểm sức khỏe tài chính phản ánh tổng hợp các yếu tố: nợ, thanh khoản, khả năng thanh toán.',
        },
    ]
}

// ── Icon Row Summary ──────────────────────────────────────────────────────────
function IconRow({ checks }) {
    return (
        <div className="checklist-icon-row">
            {checks.map((c, i) => (
                <span
                    key={i}
                    className={`icon-dot ${c.passed === true ? 'dot-pass' : c.passed === false ? 'dot-fail' : 'dot-neutral'}`}
                    title={c.label}
                />
            ))}
        </div>
    )
}

// ── Main component ────────────────────────────────────────────────────────────
export default function ChecklistCards({ overview, getRatioValue, sector = 'normal', loading = false }) {
    const checks = overview || !loading
        ? buildChecks(overview, getRatioValue, sector)
        : Array.from({ length: 6 }, (_, i) => ({ label: `Đang tải kiểm tra ${i + 1}...` }))

    const passed = checks.filter(c => c.passed === true).length
    const total = checks.filter(c => c.passed != null).length

    return (
        <div className="checklist-section">
            <div className="checklist-header">
                <div className="checklist-header-left">
                    <span className="checklist-title">Kiểm tra sức khỏe tài chính</span>
                    {total > 0 && (
                        <span className="checklist-score">
                            {passed}/{total} đạt
                        </span>
                    )}
                </div>
                {total > 0 && <IconRow checks={checks} />}
            </div>
            <div className="checklist-grid">
                {checks.map((c, i) => (
                    <CheckItem key={i} {...c} loading={loading && !overview} />
                ))}
            </div>
        </div>
    )
}
