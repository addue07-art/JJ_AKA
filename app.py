import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="📊 台股查詢工具", layout="centered")
st.title("📊 台股查詢工具")

# ---------- 資料抓取 ----------
def fetch_range(stock_id, start_date, end_date, single_day=False):
    try:
        if single_day:
            dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            # 若選到週末，向前調到最近交易日
            if dt.weekday() == 5:
                dt -= timedelta(days=1)
            elif dt.weekday() == 6:
                dt -= timedelta(days=2)
            start_date = dt.strftime("%Y-%m-%d")
            end_date = (dt + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            dt_end = datetime.strptime(end_date, "%Y-%m-%d").date()
            end_date = (dt_end + timedelta(days=1)).strftime("%Y-%m-%d")

        for suffix in [".TW", ".TWO"]:
            try:
                df = yf.download(
                    f"{stock_id}{suffix}",
                    start=start_date,
                    end=end_date,
                    auto_adjust=False,
                    progress=False,
                    interval="1d",
                )
            except Exception:
                continue
            if df is None or df.empty:
                continue
            df = df.sort_index()
            last_idx = df.index.max()
            try:
                high = float(df["High"].max())
                low = float(df["Low"].min())
                close = float(df.loc[last_idx, "Close"])
            except Exception:
                continue
            return {
                "市場": f"Yahoo {suffix}",
                "代號": stock_id,
                "區間起": df.index.min().strftime("%Y-%m-%d"),
                "區間迄": df.index.max().strftime("%Y-%m-%d"),
                "最新交易日": last_idx.strftime("%Y-%m-%d"),
                "收盤價": close,
                "最高價": high,
                "最低價": low,
            }
    except Exception as e:
        # 回傳 None 讓呼叫端顯示錯誤
        st.exception(e)
        return None
    return None

# ---------- 推算邏輯 ----------
def fib_extension_levels(high, low, close, apply_limit=False, show_short=False, show_close=False):
    rng = high - low
    limit_up = low * 1.10
    limit_down = high * 0.90
    levels = []

    def annotate(label, value, note, style):
        # Apply limit filter if requested
        if apply_limit:
            if style == "long" and value > limit_up:
                return None
            if style == "short" and value < limit_down:
                return None
            if style == "close" and (value > limit_up or value < limit_down):
                return None

        # Color/style the note
        if style == "custom":
            note = f'<span style="color:orange">{note}</span>'
        elif style == "short":
            note = f'<span style="color:blue">{note}</span>'
        elif style == "close":
            note = f'<span style="color:green">{note}</span>'

        # If not filtering, annotate out-of-limit values
        if not apply_limit:
            if style == "long" and value > limit_up:
                note += ' <span style="color:gray">(超出漲幅限制)</span>'
            if style == "short" and value < limit_down:
                note += ' <span style="color:gray">(超出跌幅限制)</span>'
            if style == "close" and (value > limit_up or value < limit_down):
                note += ' <span style="color:gray">(超出漲跌幅限制)</span>'
        return (label, value, note)

    # 多方延伸（以低點或高點混合）
    long_levels = [
        ("高點 − 波幅×0.382", high - rng * 0.382, "黃金分割回檔支撐", "long"),
        ("低點 + 波幅×1.03", low + rng * 1.03, "小幅突破前高，試探新高", "long"),
        ("低點 + 波幅×1.2", low + rng * 1.2, "第一個明顯延伸壓力位", "long"),
        ("低點 + 波幅×1.5", low + rng * 1.5, "關鍵心理整數＋1.5 倍目標壓力", "long"),
        ("自訂延伸（低點 + 波幅×0.06）", low + rng * 0.06, "微支撐區（自訂）", "custom"),
        ("自訂延伸（低點 + 波幅×0.31）", low + rng * 0.31, "短期反彈目標（自訂）", "custom"),
    ]

    # 空方延伸（以高點往下）
    short_levels = [
        ("高點 − 波幅×0.03", high - rng * 0.03, "微幅跌破，測試支撐", "short"),
        ("高點 − 波幅×0.2", high - rng * 0.2, "第一個空方延伸支撐", "short"),
        ("高點 − 波幅×0.5", high - rng * 0.5, "中段支撐（空方）", "short"),
        ("高點 − 波幅×0.618", high - rng * 0.618, "強支撐，空方延伸目標", "short"),
        ("高點 − 波幅×0.8", high - rng * 0.8, "空方極限支撐", "short"),
    ]

    # 收盤延伸（以收盤為起點，貼近實務）
    close_levels = [
        ("收盤 + 波幅×0.06", close + rng * 0.06, "短線反彈（收盤起點）", "close"),
        ("收盤 + 波幅×0.31", close + rng * 0.31, "中段反彈（收盤起點）", "close"),
        ("收盤 − 波幅×0.06", close - rng * 0.06, "短線回檔（收盤起點）", "close"),
        ("收盤 − 波幅×0.31", close - rng * 0.31, "中段回檔（收盤起點）", "close"),
    ]

    for item in long_levels:
        r = annotate(*item)
        if r:
            levels.append(r)

    if show_short:
        for item in short_levels:
            r = annotate(*item)
            if r:
                levels.append(r)

    if show_close:
        for item in close_levels:
            r = annotate(*item)
            if r:
                levels.append(r)

    return levels

# ---------- 呈現表格 ----------
def render_fib_table(high, low, close, apply_limit, show_short, show_close):
    try:
        rows = fib_extension_levels(high, low, close, apply_limit, show_short, show_close)
        if not rows:
            st.info("沒有符合條件的延伸點位（可能被漲跌幅限制過濾掉）。")
            return
        df = pd.DataFrame(rows, columns=["推算方式", "點位", "解讀"])
        df["點位"] = df["點位"].map(lambda x: f"{x:7.2f}")
        table_md = "| 推算方式 | 點位 | 解讀 |\n|---|---:|---|\n"
        for i in range(len(df)):
            table_md += f"| {df.iloc[i,0]} | {df.iloc[i,1]} | {df.iloc[i,2]} |\n"
        st.markdown("### 🔢 黃金切割率延伸點位")
        st.markdown(table_md, unsafe_allow_html=True)
    except Exception as e:
        st.exception(e)

# ---------- UI 與互動 ----------
stock_id = st.text_input("請輸入股票代號（不含市場代碼）", value="4991")
mode = st.radio("查詢模式", ["單日查詢", "區間查詢"])
col_opts = st.columns(3)
with col_opts[0]:
    apply_limit = st.checkbox("只顯示符合漲跌幅限制的點位", value=False)
with col_opts[1]:
    show_short = st.checkbox("顯示空方切割率", value=False)
with col_opts[2]:
    show_close = st.checkbox("顯示收盤延伸模組", value=True)

# 預設日期
today = datetime.now().date()
default_date = today - timedelta(days=1)

if mode == "單日查詢":
    date = st.date_input("選擇日期", value=default_date)
    if st.button("查詢單日"):
        with st.spinner("查詢中..."):
            res = fetch_range(stock_id, date.strftime("%Y-%m-%d"), date.strftime("%Y-%m-%d"), single_day=True)
            if not res:
                st.error("查詢失敗，可能是代號錯誤、非交易日或資料來源無資料。")
            else:
                st.subheader(f"{res['代號']} ({res['市場']})")
                st.write(f"日期：{res['最新交易日']}")
                st.write(f"收盤價：{res['收盤價']:.2f}")
                st.write(f"最高價：{res['最高價']:.2f}，最低價：{res['最低價']:.2f}")
                render_fib_table(res["最高價"], res["最低價"], res["收盤價"], apply_limit, show_short, show_close)
else:
    start = st.date_input("開始日期", value=default_date - timedelta(days=6))
    end = st.date_input("結束日期", value=default_date)
    if st.button("查詢區間"):
        # 驗證日期順序
        if start > end:
            st.error("開始日期不得晚於結束日期")
        else:
            with st.spinner("查詢中..."):
                res = fetch_range(stock_id, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"), single_day=False)
                if not res:
                    st.error("查詢失敗，可能是代號錯誤或選取區間無資料。")
                else:
                    st.subheader(f"{res['代號']} ({res['市場']})")
                    st.write(f"區間：{res['區間起']} ~ {res['區間迄']}")
                    st.write(f"收盤價：{res['收盤價']:.2f}")
                    st.write(f"最高價：{res['最高價']:.2f}，最低價：{res['最低價']:.2f}")
                    render_fib_table(res["最高價"], res["最低價"], res["收盤價"], apply_limit, show_short, show_close)
