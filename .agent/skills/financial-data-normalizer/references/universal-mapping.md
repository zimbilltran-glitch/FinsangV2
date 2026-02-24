# Universal Financial Mapping Schema 

Convert all incoming raw strings (regardless of source or language) to these exact `Standard Keys`.

## Balance Sheet (Bảng cân đối kế toán)
| Standard Key | Source Variants (Vietnamese / Alternate English) | Type |
| :--- | :--- | :--- |
| `total_assets` | Tổng tài sản, Total Assets, Total Asset | Asset |
| `current_assets` | Tài sản ngắn hạn, Current Assets, Short-term Assets | Asset |
| `non_current_assets` | Tài sản dài hạn, Tài sản cố định (broadly), Fixed Assets, Non-current Assets | Asset |
| `total_liabilities` | Tổng nợ phải trả, Nợ phải trả, Total Liabilities, Nợ tổng cộng | Liability |
| `current_liabilities` | Nợ ngắn hạn, Current Liabilities, Short-term Liabilities | Liability |
| `non_current_liabilities` | Nợ dài hạn, Long-term Liabilities, Non-current Liab | Liability |
| `total_equity` | Vốn chủ sở hữu, Tổng vốn chủ sở hữu, Shareholders' Equity, Stockholders Equity, Total Equity | Equity |

## Income Statement (Báo cáo kết quả kinh doanh)
| Standard Key | Source Variants | Type |
| :--- | :--- | :--- |
| `total_revenue` | Doanh thu thuần, Tổng doanh thu, Net Revenue, Revenue, Sales | Income |
| `cogs` | Giá vốn hàng bán, Cost of Goods Sold, Cost of Sales, Cost of Revenue | Expense |
| `gross_profit` | Lợi nhuận gộp, Gross Profit, Gross Margin | Income |
| `operating_expenses` | Chi phí hoạt động, Chi phí bán hàng và quản lý doanh nghiệp (SG&A), Operating Expenses, Opex | Expense |
| `operating_income` | Lợi nhuận thuần từ hoạt động kinh doanh, Lợi nhuận hoạt động, Operating Income, EBIT | Income |
| `net_income` | Lợi nhuận sau thuế, Lợi nhuận ròng, Lãi ròng, Net Income, Profit After Tax, PAT | Income |

## Cash Flow Statement (Lưu chuyển tiền tệ)
| Standard Key | Source Variants | Type |
| :--- | :--- | :--- |
| `operating_cash_flow` | Lưu chuyển tiền thuần từ hoạt động kinh doanh, Dòng tiền HĐKD, Operating Cash Flow, OCF, CFO | Cash Flow |
| `investing_cash_flow` | Lưu chuyển tiền thuần từ hoạt động đầu tư, Dòng tiền HĐĐT, Investing Cash Flow, CFI | Cash Flow |
| `financing_cash_flow` | Lưu chuyển tiền thuần từ hoạt động tài chính, Dòng tiền HĐTC, Financing Cash Flow, CFF | Cash Flow |
| `net_change_in_cash` | Lưu chuyển tiền thuần trong kỳ, Tăng/giảm tiền thuần, Net Change in Cash, Change in Cash | Cash Flow |
