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

def fib_extension_levels(high, low):
    rng = high - low
    return [
        ("高點 − 波幅×0.382", high - rng * 0.382, "黃金分割回檔支撐"),
        ("低點 + 波幅×1.03", low + rng * 1.03, "小幅突破前高，試探新高"),
        ("低點 + 波幅×1.2", low + rng * 1.2, "第一個明顯延伸壓力位"),
        ("低點 + 波幅×1.5", low + rng * 1.5, "關鍵心理整數＋1.5 倍目標壓力"),
    ]

stock_id = st.text_input("請輸入股票代號", value="2330")
mode = st.radio("查詢模式", ["單日查詢", "區間查詢"])

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
            st.write(f"最高價：{res['最高價']:.2f}，最低價：{res['最低價']:.2f}")
            st.markdown("### 🔢 黃金切割率延伸點位")
            df = fib_extension_levels(res["最高價"], res["最低價"])
            st.table(pd.DataFrame(df, columns=["推算方式", "點位", "解讀"]))
        else:
            st.error("查詢失敗，可能是代號錯誤或非交易日")
else:
    start = st.date_input("開始日期")
    end = st.date_input("結束日期")
    if st.button("查詢"):
        res = fetch_range(
            stock_id,
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d")
        )
        if res:
            st.subheader(f"{res['代號']} ({res['市場']})")
            st.write(f"區間：{res['區間起']} ~ {res['區間迄']}")
            st.write(f"收盤價：{res['收盤價']:.2f}")
            st.write(f"最高價：{res['最高價']:.2f}，最低價：{res['最低價']:.2f}")
            st.markdown("### 🔢 黃金切割率延伸點位")
            df = fib_extension_levels(res["最高價"], res["最低價"])
            st.table(pd.DataFrame(df, columns=["推算方式", "點位", "解讀"]))
        else:
            st.error("查詢失敗，可能是代號錯誤或無資料")
