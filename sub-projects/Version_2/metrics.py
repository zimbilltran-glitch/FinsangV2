"""
Phase M — Metrics: Derived Ratios Engine
metrics.py — Calculates specialized dynamic financial ratios from Parquet sheets.

Calculates:
  - Gross Margin % (Biên lợi nhuận gộp) = QL_isa5 / QL_isa3 * 100
  - Net Margin %   (Biên lợi nhuận thuần) = QL_isa23 / QL_isa3 * 100
  - Current Ratio  (Hệ số T/T hiện hành) = CD_bsa1 / CD_bsa98
  - D/E Ratio      (Hệ số Nợ/Vốn CSH)     = CD_bsa97 / CD_bsa127

Usage:
  python Version_2/metrics.py --ticker VHC --period year
"""

import argparse
import pandas as pd
from pipeline import load_tab_from_supabase

def calc_metrics(ticker: str, period: str) -> pd.DataFrame:
    """
    Load CDKT, KQKD, LCTT from Supabase, calculate derived metrics for all periods,
    and return them as a DataFrame matching the load_tab format.
    Grouped into 8 sections according to the CFO template.
    """
    try:
        cdkt = load_tab_from_supabase(ticker, period, "cdkt")
        kqkd = load_tab_from_supabase(ticker, period, "kqkd")
        lctt = load_tab_from_supabase(ticker, period, "lctt")
    except Exception as e:
        print(f"  ❌ Cannot load supabase data: {e}")
        return pd.DataFrame()

    if cdkt.empty or kqkd.empty or lctt.empty:
        return pd.DataFrame()

    meta_cols = ["field_id", "vn_name", "unit", "level"]
    # Intersection of periods across all statements to be safe
    cdkt_p = set(c for c in cdkt.columns if c not in meta_cols)
    kqkd_p = set(c for c in kqkd.columns if c not in meta_cols)
    lctt_p = set(c for c in lctt.columns if c not in meta_cols)
    def sort_p(p):
        if str(p).startswith("Q"):
            try: return (int(p[3:]), int(p[1]))
            except: pass
        try: return (int(p), 0)
        except: return (0, 0)

    periods = sorted(list(cdkt_p & kqkd_p & lctt_p), key=sort_p, reverse=True)

    if not periods:
        return pd.DataFrame()

    def get_row(df, fid):
        sub = df[df["field_id"] == fid]
        if sub.empty: return pd.Series(0.0, index=periods)
        return sub.iloc[0]

    def clean_num(val):
        if pd.isna(val) or val is None or val == "": return 0.0
        try: return float(val)
        except (ValueError, TypeError): return 0.0

    rows = []
    
    def add_row(fid, vn_name, unit, level, calc_func):
        row_dict = {"field_id": fid, "vn_name": vn_name, "unit": unit, "level": level}
        for p in periods:
            row_dict[p] = calc_func(p)
        rows.append(row_dict)

    # Pre-fetch required rows
    # CDKT
    tien_tuong_duong = get_row(cdkt, "cdkt_tien_va_tuong_duong_tien")
    dt_ngan_han = get_row(cdkt, "cdkt_dau_tu_ngan_han")
    phai_thu = get_row(cdkt, "cdkt_cac_khoan_phai_thu")
    ton_kho = get_row(cdkt, "cdkt_hang_ton_kho_rong")
    tscd = get_row(cdkt, "cdkt_tai_san_co_dinh")
    ts_dodang = get_row(cdkt, "cdkt_tai_san_do_dang_dai_han")
    tong_ts = get_row(cdkt, "cdkt_tong_cong_tai_san")
    
    vay_dh = get_row(cdkt, "cdkt_vay_dai_han")
    vay_nh = get_row(cdkt, "cdkt_vay_ngan_han")
    phai_tra_nb = get_row(cdkt, "cdkt_phai_tra_nguoi_ban")
    nguoi_mua_tt = get_row(cdkt, "cdkt_nguoi_mua_tra_tien_truoc")
    von_gop = get_row(cdkt, "cdkt_von_gop")
    lai_cpp = get_row(cdkt, "cdkt_lai_chua_phan_phoi")
    tong_nv = get_row(cdkt, "cdkt_tong_cong_nguon_von")
    
    nguoi_mua_tt_nh = get_row(cdkt, "cdkt_nguoi_mua_tra_tien_truoc")
    nguoi_mua_tt_dh = get_row(cdkt, "cdkt_nguoi_mua_tra_tien_truoc_dai_han")
    dt_cth = get_row(cdkt, "cdkt_doanh_thu_chua_thuc_hien")
    dt_cth_nh = get_row(cdkt, "cdkt_doanh_thu_chua_thuc_hien_ngan_han")
    
    co_phieu_pt = get_row(cdkt, "cdkt_co_phieu_pho_thong")
    
    # KQKD
    dt_thuan = get_row(kqkd, "kqkd_doanh_thu_thuan")
    ln_codong_me = get_row(kqkd, "kqkd_loi_nhuan_cua_co_dong_cua_cong_ty_me")
    ln_gop = get_row(kqkd, "kqkd_loi_nhuan_gop")
    cp_ban_hang = get_row(kqkd, "kqkd_chi_phi_ban_hang")
    cp_qldn = get_row(kqkd, "kqkd_chi_phi_quan_ly_doanh_nghiep")
    dt_tc = get_row(kqkd, "kqkd_doanh_thu_hoat_dong_tai_chinh")
    cp_tc = get_row(kqkd, "kqkd_chi_phi_tai_chinh")
    lai_ld = get_row(kqkd, "kqkd_lai_tu_cong_ty_lien_doanh") 
    lai_ld_alt = get_row(kqkd, "kqkd_lai_tu_cong_ty_lien_doanh_1")
    thu_nhap_khac = get_row(kqkd, "kqkd_thu_nhap_khac_rong") 

    # LCTT
    cfo = get_row(lctt, "lctt_luu_chuyen_tien_te_rong_tu_cac_hoat_dong_san_xuat_kinh_")
    cfi = get_row(lctt, "lctt_luu_chuyen_tien_thuan_tu_hoat_dong_dau_tu")
    cff = get_row(lctt, "lctt_luu_chuyen_tien_thuan_tu_hoat_dong_tai_chinh")
    cft = get_row(lctt, "lctt_luu_chuyen_tien_thuan_trong_ky")

    # Group 1: Cấu Trúc Tài Sản
    add_row("g1", "1) Cấu Trúc Tài Sản", "", 0, lambda p: None)
    add_row("g1_1", "Tiền và tương đương tiền", "tỷ đồng", 1, lambda p: clean_num(tien_tuong_duong.get(p, 0)))
    add_row("g1_2", "Đầu tư ngắn hạn", "tỷ đồng", 1, lambda p: clean_num(dt_ngan_han.get(p, 0)))
    add_row("g1_3", "Các khoản phải thu", "tỷ đồng", 1, lambda p: clean_num(phai_thu.get(p, 0)))
    add_row("g1_4", "Hàng tồn kho, ròng", "tỷ đồng", 1, lambda p: clean_num(ton_kho.get(p, 0)))
    add_row("g1_5", "Tài sản cố định", "tỷ đồng", 1, lambda p: clean_num(tscd.get(p, 0)))
    add_row("g1_6", "Tài sản dở dang dài hạn", "tỷ đồng", 1, lambda p: clean_num(ts_dodang.get(p, 0)))
    def calc_ts_khac(p):
        tong = clean_num(tong_ts.get(p, 0))
        components = sum([clean_num(x.get(p, 0)) for x in [tien_tuong_duong, dt_ngan_han, phai_thu, ton_kho, tscd, ts_dodang]])
        return tong - components
    add_row("g1_7", "Tài sản khác (Phần còn lại)", "tỷ đồng", 1, calc_ts_khac)
    add_row("g1_8", "TỔNG CỘNG TÀI SẢN", "tỷ đồng", 0, lambda p: clean_num(tong_ts.get(p, 0)))

    # Group 2: Cấu Trúc Nguồn Vốn
    add_row("g2", "2) Cấu Trúc Nguồn Vốn", "", 0, lambda p: None)
    add_row("g2_1", "Vay dài hạn", "tỷ đồng", 1, lambda p: clean_num(vay_dh.get(p, 0)))
    add_row("g2_2", "Vay ngắn hạn", "tỷ đồng", 1, lambda p: clean_num(vay_nh.get(p, 0)))
    def calc_no_cd(p):
        return clean_num(phai_tra_nb.get(p, 0)) + clean_num(nguoi_mua_tt.get(p, 0))
    add_row("g2_3", "Nợ chiếm dụng (bao gồm a+b)", "tỷ đồng", 1, calc_no_cd)
    add_row("g2_3a", "a) Phải trả người bán", "tỷ đồng", 2, lambda p: clean_num(phai_tra_nb.get(p, 0)))
    add_row("g2_3b", "b) Người mua trả tiền trước", "tỷ đồng", 2, lambda p: clean_num(nguoi_mua_tt.get(p, 0)))
    add_row("g2_4", "Vốn góp", "tỷ đồng", 1, lambda p: clean_num(von_gop.get(p, 0)))
    add_row("g2_5", "Lãi chưa phân phối", "tỷ đồng", 1, lambda p: clean_num(lai_cpp.get(p, 0)))
    def calc_vcsh_khac(p):
        tong = clean_num(tong_nv.get(p, 0))
        components = sum([clean_num(x.get(p, 0)) for x in [vay_dh, vay_nh]]) + calc_no_cd(p) + clean_num(von_gop.get(p, 0)) + clean_num(lai_cpp.get(p, 0))
        return tong - components
    add_row("g2_6", "VCSH khác (Phần còn lại)", "tỷ đồng", 1, calc_vcsh_khac)
    add_row("g2_7", "TỔNG CỘNG NGUỒN VỐN", "tỷ đồng", 0, lambda p: clean_num(tong_nv.get(p, 0)))

    # Group 3: Người mua trả tiền trước & Doanh thu chưa thực hiện
    add_row("g3", "3) Trả tiền trước & Doanh thu chưa thực hiện", "", 0, lambda p: None)
    add_row("g3_1", "Người mua trả tiền trước (a+b)", "tỷ đồng", 1, lambda p: clean_num(nguoi_mua_tt_nh.get(p, 0)) + clean_num(nguoi_mua_tt_dh.get(p, 0)))
    add_row("g3_1a", "a) Người mua trả tiền trước ngắn hạn", "tỷ đồng", 2, lambda p: clean_num(nguoi_mua_tt_nh.get(p, 0)))
    add_row("g3_1b", "b) Người mua trả tiền trước dài hạn", "tỷ đồng", 2, lambda p: clean_num(nguoi_mua_tt_dh.get(p, 0)))
    add_row("g3_2", "Doanh thu chưa thực hiện (c+d)", "tỷ đồng", 1, lambda p: clean_num(dt_cth.get(p, 0)))
    add_row("g3_2c", "c) Doanh thu chưa thực hiện ngắn hạn", "tỷ đồng", 2, lambda p: clean_num(dt_cth_nh.get(p, 0)))
    add_row("g3_2d", "d) Doanh thu chưa thực hiện dài hạn", "tỷ đồng", 2, lambda p: clean_num(dt_cth.get(p, 0)) - clean_num(dt_cth_nh.get(p, 0)))

    # Group 4: Cash Flow
    add_row("g4", "4) Dòng tiền thuần (Cash Flow)", "", 0, lambda p: None)
    add_row("g4_1", "Lưu chuyển tiền từ HĐKD", "tỷ đồng", 1, lambda p: clean_num(cfo.get(p, 0)))
    add_row("g4_2", "Lưu chuyển tiền từ HĐĐT", "tỷ đồng", 1, lambda p: clean_num(cfi.get(p, 0)))
    add_row("g4_3", "Lưu chuyển tiền từ HĐTC", "tỷ đồng", 1, lambda p: clean_num(cff.get(p, 0)))
    add_row("g4_4", "Lưu chuyển tiền thuần trong kỳ", "tỷ đồng", 1, lambda p: clean_num(cft.get(p, 0)))

    # Group 5: Hiệu quả kinh doanh
    add_row("g5", "5) Hiệu quả kinh doanh", "", 0, lambda p: None)
    add_row("g5_1", "Doanh thu thuần", "tỷ đồng", 1, lambda p: clean_num(dt_thuan.get(p, 0)))
    add_row("g5_2", "Lợi nhuận cổ đông công ty mẹ", "tỷ đồng", 1, lambda p: clean_num(ln_codong_me.get(p, 0)))
    add_row("g5_3", "Lợi nhuận gộp", "tỷ đồng", 1, lambda p: clean_num(ln_gop.get(p, 0)))
    def calc_bln_gop(p):
        dtt = clean_num(dt_thuan.get(p, 0))
        return (clean_num(ln_gop.get(p, 0)) / dtt * 100) if dtt != 0 else None
    add_row("g5_4", "% Biên lợi nhuận gộp", "%", 1, calc_bln_gop)
    def calc_bln_me(p):
        dtt = clean_num(dt_thuan.get(p, 0))
        return (clean_num(ln_codong_me.get(p, 0)) / dtt * 100) if dtt != 0 else None
    add_row("g5_5", "% Biên LN cổ đông công ty mẹ", "%", 1, calc_bln_me)

    # Group 6: Cấu trúc Lợi nhuận trước thuế
    add_row("g6", "6) Cấu trúc Lợi nhuận (PBT)", "", 0, lambda p: None)
    def calc_ln_cot_loi(p):
        return clean_num(ln_gop.get(p, 0)) - (clean_num(cp_ban_hang.get(p, 0)) + clean_num(cp_qldn.get(p, 0)))
    add_row("g6_1", "Lợi nhuận cốt lõi (a-b)", "tỷ đồng", 1, calc_ln_cot_loi)
    add_row("g6_1a", "a) Lợi nhuận gộp", "tỷ đồng", 2, lambda p: clean_num(ln_gop.get(p, 0)))
    add_row("g6_1b", "b) Chi phí BH & QLDN", "tỷ đồng", 2, lambda p: clean_num(cp_ban_hang.get(p, 0)) + clean_num(cp_qldn.get(p, 0)))
    add_row("g6_1b1", "b.1 Chi phí bán hàng", "tỷ đồng", 3, lambda p: clean_num(cp_ban_hang.get(p, 0)))
    add_row("g6_1b2", "b.2 Chi phí QLDN", "tỷ đồng", 3, lambda p: clean_num(cp_qldn.get(p, 0)))
    add_row("g6_2", "Lợi nhuận tài chính", "tỷ đồng", 1, lambda p: clean_num(dt_tc.get(p, 0)) - clean_num(cp_tc.get(p, 0)))
    add_row("g6_2a", "Doanh thu HĐ tài chính", "tỷ đồng", 2, lambda p: clean_num(dt_tc.get(p, 0)))
    add_row("g6_2b", "Chi phí tài chính", "tỷ đồng", 2, lambda p: clean_num(cp_tc.get(p, 0)))
    add_row("g6_3", "Lãi/(lỗ) từ công ty liên doanh", "tỷ đồng", 1, lambda p: clean_num(lai_ld.get(p, 0)) or clean_num(lai_ld_alt.get(p, 0)))
    add_row("g6_4", "Thu nhập khác, ròng", "tỷ đồng", 1, lambda p: clean_num(thu_nhap_khac.get(p, 0)))

    # Group 7: Tăng trưởng
    add_row("g7", "7) Tăng trưởng Doanh thu & Lãi ròng", "", 0, lambda p: None)
    def calc_yoy(val_current, val_prev):
        if val_prev and val_prev != 0:
            return ((val_current - val_prev) / abs(val_prev)) * 100
        return None
        
    def get_yoy_period(p):
        if period == "year":
            try: return str(int(p) - 1)
            except: return None
        elif period == "quarter" and len(p) >= 7:
            try:
                q = int(p[1])
                y = int(p[3:])
                return f"Q{q}/{y-1}"
            except: return None
        return None

    def calc_tt_dtt(p):
        prev = get_yoy_period(p)
        if prev in periods:
            return calc_yoy(clean_num(dt_thuan.get(p, 0)), clean_num(dt_thuan.get(prev, 0)))
        return None

    def calc_tt_ln(p):
        prev = get_yoy_period(p)
        if prev in periods:
            return calc_yoy(clean_num(ln_codong_me.get(p, 0)), clean_num(ln_codong_me.get(prev, 0)))
        return None
        
    add_row("g7_1", "Tăng trưởng DTT (YoY)", "%", 1, calc_tt_dtt)
    add_row("g7_2", "Tăng trưởng LN Cổ đông (YoY)", "%", 1, calc_tt_ln)

    # Group 8: EPS và Cổ phiếu
    add_row("g8", "8) Cổ phiếu & Hiệu suất", "", 0, lambda p: None)
    
    def calc_ttm_ln(p):
        if period == "year":
            return clean_num(ln_codong_me.get(p, 0))
        try:
            q = int(p[1])
            y = int(p[3:])
            qs = [p]
            curr_q, curr_y = q, y
            for _ in range(3):
                if curr_q == 1:
                    curr_q = 4
                    curr_y -= 1
                else:
                    curr_q -= 1
                qs.append(f"Q{curr_q}/{curr_y}")
            if all(qid in periods for qid in qs):
                return sum(clean_num(ln_codong_me.get(qid, 0)) for qid in qs)
        except: pass
        return None

    add_row("g8_1", "LN ròng (TTM)", "tỷ đồng", 1, calc_ttm_ln)
    
    def calc_sl_cp(p):
        # Vốn trong DB là VND. Phải chia 10,000 để ra số lượng cổ phiếu.
        return (clean_num(co_phieu_pt.get(p, 0)) / 10000.0)
        
    add_row("g8_2", "Số lượng cổ phiếu", "cổ phiếu", 1, calc_sl_cp)
    
    def calc_eps(p):
        ttm = calc_ttm_ln(p)
        sl_cp = calc_sl_cp(p)
        if ttm is not None and sl_cp and sl_cp != 0:
            # ttm là VND. sl_cp là số cổ phiếu. eps là VND/cp.
            return ttm / sl_cp
        return None
        
    add_row("g8_3", "EPS (TTM)", "đồng/cp", 1, calc_eps)

    result_df = pd.DataFrame(rows)
    cols = ["field_id", "vn_name", "unit", "level"] + periods
    return result_df[cols]

def main():
    parser = argparse.ArgumentParser(description="Finsang V2.0 — Metrics Engine")
    parser.add_argument("--ticker", required=True, help="Stock ticker (e.g., VHC)")
    parser.add_argument("--period", choices=["year", "quarter"], default="year")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    print(f"\n{'═'*80}")
    print(f"  📈 METRICS ENGINE — {ticker} ({args.period.upper()})")
    print(f"{'═'*80}\n")

    df = calc_metrics(ticker, args.period)
    if df.empty:
        return

    # Print wide display
    periods = [c for c in df.columns if c not in ["field_id", "vn_name", "unit", "level"]]
    print_cols = ["Chỉ tiêu"] + periods[:5]  # View up to 5 most recent periods
    
    header = f"  {print_cols[0]:<25} | " + " | ".join([f"{c:>10}" for c in print_cols[1:]])
    print(header)
    print(f"  {'-'*80}")

    for _, row in df.iterrows():
        val_strs = []
        for p in print_cols[1:]:
            val = row[p]
            if val is None:
                val_strs.append(f"{'—':>10}")
            elif row["unit"] == "%":
                val_strs.append(f"{val:>9.1f}%")
            else:
                val_strs.append(f"{val:>10.2f}")
                
        line = f"  {row['vn_name']:<25} | " + " | ".join(val_strs)
        print(line)

    print(f"\n{'═'*80}\n")

if __name__ == "__main__":
    main()
