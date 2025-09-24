import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="📊 台股查詢工具", layout="centered")
st.title("📊 台股查詢工具")

def fetch_range(stock_id, start_date, end_date, single_day=False):
    if single_day:
        dt = datetime.strptime(start_date, "%Y-%m-%d").date()
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
                auto_adjust=True,
                progress=False,
                interval="1d",
            )
            if df.empty:
                continue
            df = df.sort_index()
            last_idx = df.index.max()
            high = float(df["High"].max())
            low = float(df["Low"].min())
            close = float(df.loc[last_idx, "Close"])
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
        except:
            continue
    return None

def fib_extension_levels(high, low, close, apply_limit=False, show_short=False, show_close=False):
    rng = high - low
    limit_up = low * 1.10
    limit_down = high * 0.90
    levels = []

    def annotate(label, value, note, style):
        if apply_limit:
            if style == "long" and value > limit_up:
                return None
            if style == "short" and value < limit_down:
                return None
            if style == "close" and (value > limit_up or value < limit_down):
                return None
        if style == "custom":
            note = f'<span style="color:orange">{note}</span>'
        elif style == "short":
            note = f'<span style="color:blue">{note}</span>'
        elif style == "close":
            note = f'<span style="color:green">{note}</span>'
        if not apply_limit:
            if style == "long" and value > limit_up:
                note += ' <span style="color:gray">(超出漲幅限制)</span>'
            if style == "short" and value < limit_down:
                note += ' <span style="color:gray">(超出跌幅限制)</span>'
            if style == "close" and (value > limit_up or value < limit_down):
                note += ' <span style="color:gray">(超出漲跌幅限制)</span>'
        return (label, value, note)

    long_levels = [
        ("高點 − 波幅×0.382", high - rng * 0.382, "黃金分割回檔支撐", "long"),
        ("低點 + 波幅×1.03", low + rng * 1.03, "小幅突破前高，試探新高", "long"),
        ("低點 + 波幅×1.2", low + rng * 1.2, "第一個明顯延伸壓力位", "long"),
        ("低點 + 波幅×1.5", low + rng * 1.5, "關鍵心理整數＋1.5 倍目標壓力", "long"),
        ("自訂延伸（低點 + 波幅×0.06）", low + rng * 0.06, "微支撐區（自訂）", "custom"),
        ("自訂延伸（低點 + 波幅×0.31）", low + rng * 0.31, "短期反彈目標（自訂）", "custom"),
    ]

    short_levels = [
        ("高點 − 波幅×0.03", high - rng * 0.03, "微幅跌破，測試支撐", "short"),
        ("高點 − 波幅×0.2", high - rng * 0.2, "第一個空方延伸支撐", "short"),
        ("高點 − 波幅×0.5", high - rng * 0.5, "中段支撐（空方）", "short"),
        ("高點 − 波幅×0.618", high - rng * 0.618, "強支撐，空方延伸目標", "short"),
        ("高點 − 波幅×0.8", high - rng * 0.8, "空方極限支撐", "short"),
    ]

    close_levels = [
        ("收盤 + 波幅×0.06", close + rng * 0.06, "短線反彈（收盤起點）", "close"),
        ("收盤 + 波幅×0.31", close + rng * 0.31, "中段反彈（收盤起點）", "close"),
        ("收盤 − 波幅×0.06", close - rng * 0.06, "短線回檔（收盤起點）", "close"),
        ("收盤 − 波幅×0.31", close - rng * 0.31, "中段回檔（收盤起點）", "close"),
    ]

    for item in long_levels:
        result = annotate(*item)
        if result:
            levels.append(result)

    if show_short:
        for item in short_levels:
            result = annotate(*item)
            if result:
                levels.append(result)

    if show_close:
        for item in close_levels:
            result = annotate(*item)
            if result:
                levels.append(result)

    return levels

def render_fib_table(high, low, close, apply_limit, show_short, show_close):
    df = fib_extension_levels(high, low, close, apply_limit, show_short, show_close)
    df = pd.DataFrame(df, columns=["推算方式", "點位", "解讀"])
    df["點位"] = df["點位"].map(lambda x: f"{x:7.2f}")
    table_md = "| 推算方式 | 點位 | 解讀 |\n|---|---:|---|\n"
    for i in range(len(df)):
        table_md += f"| {df.iloc[i,0]} | {df.iloc[i,1]} | {df.iloc[i,2]} |\n"
    st.markdown("### 🔢 黃金切割率延伸點位")
    st.markdown(table_md, unsafe_allow_html=True)

stock_id = st.text_input("請輸入股票代號", value="2330")
mode = st.radio("查詢模式", ["單日查詢", "區間查詢"])
apply_limit = st.checkbox("只顯示符合漲跌幅限制的點位", value=False)
show_short = st.checkbox("顯示空方切割率", value=False)
show_close = st.checkbox("顯示收盤延伸模組", value=True)

if mode == "單日查詢":
    date = st.date_input("請選擇日期")
    if st.button("查詢"):
        res = fetch_range(
            stock_id,
            date.strftime("%Y-%m-%d"),
            date.strftime("%Y-%m-%d"),
            single_day=True
        )
        if res:
            st.subheader(f"{res['代號']} ({res['市場']})")
            st.write(f"日期：{res['最新交易日']}")
            st.write(f"收盤價：{res['收盤價']:.2f}")
            st.write(f"最高價：{res['最高價']:.2f}
