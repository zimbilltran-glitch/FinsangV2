/**
 * useOverviewData.js — V3 P2.8 + P7.2
 * Custom hook: Fetch company_overview + stock_ohlcv + BS summary from Supabase.
 * Used by OverviewTab and all sub-components on the 360 tab.
 */
import { useState, useEffect, useMemo } from 'react'
import { supabase } from '../supabaseClient'

// Balance Sheet summary item IDs for Financial Position + D/E History charts
// Non-bank tickers
const BS_SUMMARY_IDS_NORMAL = [
    'cdkt_tai_san_ngan_han',
    'cdkt_tai_san_dai_han',
    'cdkt_no_ngan_han',
    'cdkt_no_dai_han',
    'cdkt_von_chu_so_huu',
    'cdkt_no_phai_tra',
]
// Bank tickers (different BS structure)
const BS_SUMMARY_IDS_BANK = [
    'cdkt_bank_tong_tai_san',
    'cdkt_bank_tong_no_phai_tra',
    'cdkt_bank_von_chu_so_huu',
    'cdkt_bank_no_phai_tra_va_von_chu_so_huu',
]
const BS_ALL_IDS = [...BS_SUMMARY_IDS_NORMAL, ...BS_SUMMARY_IDS_BANK]

export function useOverviewData(ticker) {
    const [overview, setOverview] = useState(null)
    const [ohlcv, setOhlcv] = useState([])
    const [ratios, setRatios] = useState([])
    const [bsRaw, setBsRaw] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        if (!ticker) return
        let cancelled = false

        async function load() {
            setLoading(true)
            setError(null)

            try {
                // 1. company_overview (single row)
                const { data: ovData, error: ovErr } = await supabase
                    .from('company_overview')
                    .select('*')
                    .eq('ticker', ticker)
                    .maybeSingle()
                if (ovErr) throw ovErr

                // 2. OHLCV — latest 365 trading days
                const { data: priceData, error: priceErr } = await supabase
                    .from('stock_ohlcv')
                    .select('time,open,high,low,close,volume')
                    .eq('stock_name', ticker)
                    .gte('time', '2025-01-01')
                    .order('time', { ascending: true })
                    .limit(500)
                if (priceErr) throw priceErr

                // 3. Financial ratios (for Snowflake score display + checklists)
                //    Pull latest annual period from financial_ratios_wide view
                const { data: ratioData, error: ratioErr } = await supabase
                    .from('financial_ratios_wide')
                    .select('item_id,item,periods_data,unit,levels')
                    .eq('stock_name', ticker)
                    .order('row_number', { ascending: true })
                    .limit(200)
                if (ratioErr) throw ratioErr

                // 4. Balance Sheet summary — for Financial Position + D/E History charts
                const { data: bsData, error: bsErr } = await supabase
                    .from('balance_sheet_wide')
                    .select('item_id,item,periods_data')
                    .eq('stock_name', ticker)
                    .in('item_id', BS_ALL_IDS)
                if (bsErr) throw bsErr

                if (!cancelled) {
                    setOverview(ovData)          // null if not yet fetched by backend
                    setOhlcv(priceData || [])
                    setRatios(ratioData || [])
                    setBsRaw(bsData || [])
                }
            } catch (e) {
                if (!cancelled) setError(e.message)
            } finally {
                if (!cancelled) setLoading(false)
            }
        }

        load()
        return () => { cancelled = true }
    }, [ticker])

    // ── Derived helpers ─────────────────────────────────────────────────────

    // Get latest close price from OHLCV
    // vnstock returns prices in 1,000 VND units (close=62 → 62,000 VND)
    const _rawClose = ohlcv.length > 0 ? ohlcv[ohlcv.length - 1]?.close : null
    const latestPrice = _rawClose != null
        ? _rawClose * 1000
        : overview?.current_price ?? null

    // Get price change (last 2 rows) — also in ×1000 VND
    const _rawPrev = ohlcv.length >= 2 ? ohlcv[ohlcv.length - 2].close : null
    const _rawDiff = _rawClose != null && _rawPrev != null ? _rawClose - _rawPrev : null
    const priceChange = _rawDiff != null ? _rawDiff * 1000 : null
    const priceChangePct = _rawDiff != null && _rawPrev != null
        ? (_rawDiff / _rawPrev) * 100
        : null

    // Helper: get latest period value from financial_ratios_wide periods_data
    function getRatioValue(itemId) {
        const row = ratios.find(r => r.item_id === itemId)
        if (!row?.periods_data) return null
        // Get latest annual (4-digit year key), fallback to quarterly
        const keys = Object.keys(row.periods_data).sort().reverse()
        const yearKey = keys.find(k => /^\d{4}$/.test(k))
        const key = yearKey || keys[0]
        return key ? row.periods_data[key] : null
    }

    // ── BS Summary: mapped by item_id → { label, periods_data } ─────────
    const bsSummary = useMemo(() => {
        const map = {}
        bsRaw.forEach(row => {
            map[row.item_id] = {
                label: row.item,
                periods_data: row.periods_data || {},
            }
        })
        return map
    }, [bsRaw])

    // Helper: extract annual series from BS summary for a given item_id
    // Returns sorted array: [{ year: '2020', value: 123456 }, ...]
    function getBsAnnualSeries(itemId) {
        const entry = bsSummary[itemId]
        if (!entry?.periods_data) return []
        return Object.entries(entry.periods_data)
            .filter(([k]) => /^\d{4}$/.test(k))
            .map(([year, value]) => ({ year, value: Number(value) || 0 }))
            .sort((a, b) => a.year.localeCompare(b.year))
    }

    // Helper: get latest annual BS value (in VND đồng)
    function getBsLatestValue(itemId) {
        const series = getBsAnnualSeries(itemId)
        return series.length > 0 ? series[series.length - 1].value : null
    }

    return {
        overview,
        ohlcv,
        ratios,
        loading,
        error,
        latestPrice,
        priceChange,
        priceChangePct,
        getRatioValue,
        bsSummary,
        getBsAnnualSeries,
        getBsLatestValue,
    }
}
