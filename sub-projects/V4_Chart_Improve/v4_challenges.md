# 🚧 V4 Challenges & Issues Log

Theo dõi các khó khăn kỹ thuật và hướng giải quyết trong quá trình làm V4, để agent đi sau nắm bắt tình hình.

## 1. Vấn đề Transform Data từ dạng Wide sang Recharts Array
- **Tình trạng**: Pending
- **Chuẩn đoán**: Table `_wide` trả về `{ periods_data: { "Q1.25": 100, "Q4.24": 90 } }` trên 1 Row Item. Trong khi `recharts` yêu cầu mảng các điểm thời gian: `[{ period: 'Q4.24', itemA: 90, itemB: 40 }, ...]`.
- **Giải pháp**: Xây dựng hàm parser tại Hook `useAnalysisChartsData.js` hứng data của các nhóm chỉ tiêu (Income Statement, Balance Sheet...) đảo trục tạo ra mảng array đúng format của Recharts.

## 2. Xử lý Sector Fallback
- **Tình trạng**: Pending
- **Chuẩn đoán**: Tên các mục của Bank, Sec và Normal lệch nhau.
- **Giải pháp**: Dùng Enum / Constant dictionary để ánh xạ `item_id` tương ứng với nhóm ngành, nhặt các row data chính xác mang vào Chart.
