import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

st.title("Yiahoo財經資料視覺化")
st.sidebar.title("選擇使用股票和年份")
start_year, end_year = st.sidebar.slider(
    'Select the Range of year',
    min_value=2000, max_value=datetime.now().year, value=(2015, 2020)
)

def find_stock(stock, start_y, end_y):
    if stock:
        start_data = f"{start_y}-01-01"
        end_data = f"{end_y}-12-31"
        stock_data = yf.download(stock, start=start_data, end=end_data)
        return stock_data

# 保存已添加股票的列表和数据
if 'stocks' not in st.session_state:
    st.session_state.stocks = []

if 'stock_data_list' not in st.session_state:
    st.session_state.stock_data_list = []

# 用户输入股票代码
stock = st.sidebar.text_input("請輸入股票代碼:如APPL,TSLA,GOOGL....",value='GOOGL')

# 按钮用于添加股票
if st.sidebar.button('新增股票'):
    if stock and stock not in st.session_state.stocks:
        stock_data = find_stock(stock, start_year, end_year)
        
        if not stock_data.empty: # type: ignore
            st.session_state.stocks.append(stock)
            st.session_state.stock_data_list.append(stock_data)
        else:
            st.error(f"查無相關資訊: {stock}")
    elif stock in st.session_state.stocks:
        st.warning(f"股票 {stock} 已經添加過了")

# 绘制图表
if st.session_state.stocks:
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for stock, stock_data in zip(st.session_state.stocks, st.session_state.stock_data_list):
        ax.plot(stock_data.index, stock_data['Close'], label=f'Share price_{stock}')
    
    ax.set_title("Stock Price Chart")
    ax.set_xlabel('Date')
    ax.set_ylabel('Price(US)')
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)
    # 使用 expander 展示各股票的資料
    for stock, stock_data in zip(st.session_state.stocks, st.session_state.stock_data_list):
        with st.expander(f"查看 {stock} 的資料"):
            st.write(stock_data)

else:
    st.write("請輸入股票代碼並點擊新增以查看圖表")
