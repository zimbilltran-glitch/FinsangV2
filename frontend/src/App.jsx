import { useEffect, useState, useMemo } from 'react'
import { supabase } from './supabaseClient'
import './App.css'

function App() {
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
        'CSTO': 'financial_ratios_wide'
      };

      const tableName = tableMap[reportType] || 'balance_sheet_wide';

      const { data: reports, error } = await supabase
        .from(tableName)
        .select('*')
        .eq('stock_name', stockName)
        .order('row_number', { ascending: true })

      if (error) {
        console.error(`Lỗi khi tải dữ liệu từ ${tableName}:`, error)
      } else if (reports && reports.length > 0) {

        // Filter specific cash flow types since they share the same view and row numbers interleave
        let filteredReports = reports;
        if (reportType === 'LCTT_TT') {
          filteredReports = reports.filter(r => r.item_id.startsWith('lctttt'));
        } else if (reportType === 'LCTT_GT') {
          filteredReports = reports.filter(r => r.item_id.startsWith('lcttgt'));
        }

        // Parent ID calculation 
        const processed = filteredReports.map((row, index) => {
          let parent_id = null;
          if (row.levels > 0) {
            for (let j = index - 1; j >= 0; j--) {
              if (filteredReports[j].levels === row.levels - 1) {
                parent_id = filteredReports[j].item_id;
                break;
              }
            }
          }
          return { ...row, parent_id };
        });

        setData(processed)

        // Generate columns
        if (processed.length > 0) {
          const samplePeriodsData = processed[0].periods_data || {}
          let cols = Object.keys(samplePeriodsData)
          cols.sort((a, b) => b.localeCompare(a))
          setPeriods(cols)
        }

        setExpandedRows({})
      } else {
        setData([])
        setPeriods([])
      }
      setLoading(false)
    }

    fetchData()
  }, [stockName, reportType])

  const dataMap = useMemo(() => {
    const map = {};
    data.forEach(r => { map[r.item_id] = r; });
    return map;
  }, [data]);

  const isRowVisible = (row) => {
    if (row.levels === 0) return true;
    let currParent = dataMap[row.parent_id];
    while (currParent) {
      if (!expandedRows[currParent.item_id]) return false;
      currParent = dataMap[currParent.parent_id];
    }
    return true;
  };

  const toggleRow = (itemId) => {
    setExpandedRows(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }));
  };

  const MiniBarChart = ({ values }) => {
    if (!values || values.length === 0) return null;
    const maxVal = Math.max(...values.map(Math.abs)) || 1;
    return (
      <div className="mini-bar-container">
        {values.map((v, i) => {
          const heightPct = Math.min(50, Math.max(2, (Math.abs(v) / maxVal) * 50));
          const isNegative = v < 0;
          return (
            <div key={i} className="mini-bar-wrapper" title={v}>
              <div
                className={`mini-bar ${isNegative ? 'negative' : 'positive'}`}
                style={{
                  height: `${heightPct}%`,
                  marginTop: isNegative ? '12px' : 'auto',
                  marginBottom: isNegative ? '0' : '12px',
                }}
              ></div>
            </div>
          )
        })}
      </div>
    )
  }

  const formatNumber = (num) => {
    if (num === null || num === undefined) return '-';
    // Format perfectly to match standard Accounting
    if (num === 0) return '-';
    return new Intl.NumberFormat('en-US', { maximumFractionDigits: 1 }).format(num);
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1><span>⚡</span> Finsang Terminal</h1>
      </header>

      <div className="controls" style={{ display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '10px' }}>
        <select value={stockName} onChange={e => setStockName(e.target.value)} style={{ padding: '8px', borderRadius: '4px' }}>
          <option value="NLG">NLG - Tập đoàn Nam Long</option>
          <option value="VND">VND - VNDirect</option>
          <option value="SSI">SSI - Chứng khoán SSI</option>
          <option value="FPT">FPT - Tập đoàn FPT</option>
          <option value="HPG">HPG - Tập đoàn Hoà Phát</option>
        </select>
      </div>

      <div className="tabs-container" style={{ display: 'flex', gap: '5px', marginBottom: '20px', borderBottom: '1px solid #333', paddingBottom: '0px' }}>
        {[
          { id: 'CDKT', label: 'Cân đối kế toán' },
          { id: 'KQKD', label: 'Kết quả kinh doanh' },
          { id: 'LCTT_TT', label: 'LCTT Trực tiếp' },
          { id: 'LCTT_GT', label: 'LCTT Gián tiếp' },
          { id: 'CSTO', label: 'Chỉ số tài chính' }
        ].map(tab => (
          <button
            key={tab.id}
            className={`tab-button ${reportType === tab.id ? 'active' : ''}`}
            onClick={() => setReportType(tab.id)}
            style={{
              padding: '10px 20px',
              backgroundColor: reportType === tab.id ? '#2a2a2a' : 'transparent',
              color: reportType === tab.id ? '#4ade80' : '#888',
              border: 'none',
              borderBottom: reportType === tab.id ? '2px solid #4ade80' : '2px solid transparent',
              cursor: 'pointer',
              fontWeight: 'bold',
              transition: 'all 0.2s ease'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="table-container">
        {loading ? (
          <div className="loading">Đang tải dữ liệu từ Supabase...</div>
        ) : data.length === 0 ? (
          <div className="loading">Hệ thống ghi nhận API KBSV không trả về dữ liệu {reportType} trực tiếp/chi tiết cho {stockName} (Trị số bằng 0).</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Bảng chỉ số tài chính (Tỷ đồng)</th>
                <th>Biểu đồ (Z-A)</th>
                {periods.map(period => (
                  <th key={period}>{period}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => {
                if (!isRowVisible(row)) return null;

                const hasChildren = index < data.length - 1 && data[index + 1].levels > row.levels;
                const isExpanded = !!expandedRows[row.item_id];
                const chartValues = periods.map(p => row.periods_data[p] || 0);

                const isMajorHeading = row.levels === 0 ||
                  row.item.startsWith('Cộng') ||
                  /^[IVX]+\./.test(row.item);

                return (
                  <tr key={row.item_id} className={`table-row-level-${row.levels} ${isMajorHeading ? 'parent-row' : 'child-row'}`}>
                    <td>
                      <div className="item-name-cell" style={{ paddingLeft: `${row.levels * 20}px` }}>
                        {hasChildren ? (
                          <button
                            className="expand-btn"
                            onClick={() => toggleRow(row.item_id)}
                          >
                            {isExpanded ? '[-]' : '[+]'}
                          </button>
                        ) : (
                          <span className="expand-placeholder"></span>
                        )}
                        <span className="item-label">{row.item}</span>
                      </div>
                    </td>

                    <td className="chart-td">
                      {!hasChildren && row.levels > 0 && <MiniBarChart values={chartValues} />}
                    </td>

                    {periods.map(period => (
                      <td key={period}>
                        {formatNumber(row.periods_data && row.periods_data[period])}
                      </td>
                    ))}
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

export default App


