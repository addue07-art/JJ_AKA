import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 自訂頁面
st.set_page_config(page_title="📊 Fib 台股工具", layout="wide")
st.image("https://你的網址/logo.png", width=100)
st.markdown("## 🌟 台股黃金切割分析器", unsafe_allow_html=True)

# Sidebar 輸入
st.sidebar.header("🔧 設定")
stock_id = st.sidebar.text_input("股票代號", value="2330")
mode = st.sidebar.radio("查詢模式", ["單日", "區間"])
if mode == "單日":
    date = st.sidebar.date_input("選擇日期")
else:
    start = st.sidebar.date_input("開始日期")
    end   = st.sidebar.date_input("結束日期")

# 資料擷取與計算（同前）

# 顯示結果
if st.sidebar.button("查詢"):
    # 假設 res 已正確取得
    st.subheader(f"{res['代號']} ({res['市場']})")
    # 三欄 Metric 卡片
    col1, col2, col3 = st.columns(3)
    col1.metric("收盤價", f"{res['收盤價']:.2f}")
    col2.metric("最高價", f"{res['最高價']:.2f}")
    col3.metric("最低價", f"{res['最低價']:.2f}")
    # 折線圖
    hist = yf.download(f"{stock_id}.TW", start=res["區間起"], end=res["區間迄"], progress=False)
    st.line_chart(hist["Close"])
    # 延伸點位表格
    st.markdown("### 🔢 黃金切割延伸點位")
    df = fib_extension_levels(res["最高價"], res["最低價"])
    # 轉成 DataFrame，並格式化兩位小數
    df = pd.DataFrame(df, columns=["方法", "點位", "解讀"])
    df["點位"] = df["點位"].map("{:.2f}".format)
    st.table(df)
