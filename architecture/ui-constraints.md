# UI/UX Constraints & Presentation Rules (Phase S)

## 1. Mục tiêu (Presentation Goal)
Hiển thị dữ liệu tài chính Việt Nam (BCTC, Cân đối kế toán, LCTT) thành một bảng dữ liệu mở rộng theo chiều ngang (Wide Table) giống như định dạng Excel mà nhà phân tích thường quen dùng.
Hiển thị biểu đồ giá cổ phiếu dựa trên dữ liệu OHLCV.

## 2. API & Data Fetching Constraints
Với việc đã dựng View `financial_reports_wide` sử dụng `jsonb_object_agg` trên DB, Frontend **phải (MUST)**:
- Truy vấn trục tiếp vào View `financial_reports_wide` bằng Supabase Javascript Client `supabase.from('financial_reports_wide').select('*')`.
- Sử dụng thuộc tính `periods_data` (chứa 1 object JSON dạng `{"2025-Q1": 100, "2025-Q2": 150}`) để tự động render ra các cột tương ứng trên UI.
- Sort dữ liệu theo trường `row_number` để thứ tự các khoản mục khớp chính xác với chuẩn kế toán.

## 3. UI/UX Aesthetics (Web Design)
Thiết kế của Website **phải (MUST)** tuân theo nguyên tắc "Rich Aesthetics" và "Premium Design":
1. **Tech Stack**: Ưu tiên **Next.js** hoặc **Vite (React)** với **Vanilla CSS** (Tránh Tailwind trừ khi có yêu cầu đặc biệt) để tạo thiết kế "Glassmorphism" hoặc "Dark Mode" hiện đại.
2. **Typography**: Sử dụng custom font cực kì nét và chuyên nghiệp (ví dụ: Google Font `Inter`, `Manrope` hoặc `Outfit`).
3. **Data Grid (Bảng dữ liệu)**: 
   - Không được dùng Native `<table>` rẻ tiền mà không bo góc. 
   - Phải thiết kế Header dính (Sticky Header), cuộn ngang mượt mà cho các Quý.
   - Các dòng dữ liệu cần có Hover state phản hồi tốt.
   - Thụt dòng (Indentation) dựa trên biến `levels` (level 0 thì đậm chữ, level 1 thì thò thụt nhẹ, level 2 lùi sâu hơn).
4. **Màu sắc**: Tránh dùng Xanh/Đỏ/Vàng mặc định, hãy dùng HSL color palette.

## 4. Giai đoạn tiếp theo của Agent
Sau khi hoàn tất Constraints này, Agent sẽ tiến hành Setup một Boilerplate Web App tại thư mục `frontend/` và thử nghiệm gọi dữ liệu từ Supabase View lên UI.
