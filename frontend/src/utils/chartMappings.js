/**
 * chartMappings.js
 * Mappings between chart series and Supabase item_ids.
 * Categorized by SECTOR (normal, bank, sec).
 */

export const NORMAL_CHART_MAPPINGS = {
    income_performance: {
        'Doanh thu thuần': 'kqkd_doanh_thu_thuan',
        'Lãi ròng': 'kqkd_loi_nhuan_sau_thuy_thu_nhap_doanh_nghiep',
        'Biên LN gộp': 'cstc_gross_margin',
        'Biên lãi ròng': 'cstc_net_margin',
    },
    growth: {
        'Tăng trưởng DTT (%)': 'g7_1',
        'Tăng trưởng Lãi ròng (%)': 'g7_2',
    },
    asset_structure: {
        'Tiền & Tương đương': 'cdkt_tien_va_cac_khoan_tuong_duong_tien',
        'Đầu tư ngắn hạn': 'cdkt_dau_tu_tai_chinh_ngan_han',
        'Phải thu': 'cdkt_cac_khoan_phai_thu_ngan_han',
        'Hàng tồn kho': 'cdkt_hang_ton_kho',
        'TS cố định': 'cdkt_tai_san_co_dinh',
        'TS dở dang': 'cdkt_tai_san_do_dang_dai_han',
        'TS khác': 'cdkt_tai_san_ngan_han_khac',
    },
    capital_structure: {
        'Vay ngắn hạn': 'cdkt_vay_va_no_thue_tai_chinh_ngan_han',
        'Vay dài hạn': 'cdkt_vay_va_no_thue_tai_chinh_dai_han',
        'Phải trả người bán': 'cdkt_phai_tra_nguoi_ban_ngan_han',
        'Người mua trả tiền trước': 'cdkt_nguoi_mua_tra_tien_truoc_ngan_han',
        'Vốn góp': 'cdkt_von_gop_cua_chu_so_huu',
        'Lãi chưa phân phối': 'cdkt_loi_nhuan_sau_thue_chua_phan_phoi',
        'Cổ phiếu quỹ': 'cdkt_co_phieu_quy',
    }
};

export const BANK_CHART_MAPPINGS = {
    income_performance: {
        'Tổng thu nhập': 'bank_4_1',
        'Lãi ròng': 'bank_4_5',
        'NIM (%)': 'bank_4_6',
    },
    credit_growth: {
        'Cho vay khách hàng': 'cdkt_bank_cho_vay_khach_hang',
        'Tiền gửi khách hàng': 'cdkt_bank_tien_gui_cua_khach_hang',
        'g(TOI) (%)': 'g7_1',
        'g(Lãi ròng) (%)': 'g7_2',
    },
    efficiency: {
        'ROE (%)': 'cstc_roe',
        'ROA (%)': 'cstc_roa',
        'COF (%)': 'bank_4_8',
    },
    asset_structure: {
        'Tiền & Tiền gửi NHNN': 'cdkt_bank_tien_mat_vang_bac_da_quy',
        'Cho vay khách hàng': 'cdkt_bank_cho_vay_khach_hang',
        'Chứng khoán ĐT': 'cdkt_bank_chung_khoan_dau_tu',
        'TS cố định': 'cdkt_bank_tai_san_co_dinh',
        'Tài sản khác': 'cdkt_bank_tai_san_co_khac',
    },
    npl_structure: {
        'Tỷ lệ nợ xấu (%)': 'bank_4_10',
        'NPL': 'bank_4_10',
    }
};

export const SEC_CHART_MAPPINGS = {
    income_performance: {
        'Tổng doanh thu': 'kqkd_sec_doanh_thu_hoat_dong',
        'Lãi ròng': 'kqkd_sec_loi_nhuan_sau_thue_phan_bo_cho_chu_so_huu',
        'Biên lãi ròng (%)': 'cstc_net_margin',
    },
    revenue_structure: {
        'Môi giới': 'kqkd_sec_doanh_thu_nghiep_vu_moi_gioi_chung_khoan',
        'Tự doanh (FVTPL)': 'kqkd_sec_lai_tu_cac_tai_san_tai_chinh_ghi_nhan_thong_qua_lailo',
        'Cho vay (Margin)': 'kqkd_sec_lai_tu_cac_khoan_cho_vay_va_phai_thu',
    },
    growth: {
        'ROE': 'cstc_roe',
        'ROA': 'cstc_roa',
        'LCTT KD': 'lctt_sec_luu_chuyen_tien_thuan_tu_hoat_dong_kinh_doanh',
    },
    asset_structure: {
        'FVTPL': 'cdkt_sec_tai_san_tai_chinh_ghi_nhan_thong_qua_lai_lo_fvtpl',
        'Margin (Cho vay)': 'cdkt_sec_cac_khoan_cho_vay_1',
        'Tiền & Tương đương': 'cdkt_sec_tien_va_cac_khoan_tuong_duong_tien',
    },
    capital_structure: {
        'Vay nợ ngắn hạn': 'cdkt_sec_vay_va_no_thue_tai_chinh_ngan_han',
        'Vay nợ dài hạn': 'cdkt_sec_vay_va_no_thue_tai_chinh_dai_han',
        'VCSH': 'cdkt_sec_von_chu_so_huu_1',
        'LN chưa pp': 'cdkt_sec_loi_nhuan_sau_thue_chua_phan_phoi_1',
    }
};

export const SECTOR_MAPPINGS = {
    normal: NORMAL_CHART_MAPPINGS,
    bank: BANK_CHART_MAPPINGS,
    sec: SEC_CHART_MAPPINGS,
};
