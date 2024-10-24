import streamlit as st
import os
import requests
import yfinance as yf
from bs4 import BeautifulSoup
import re
from swarm import Swarm, Agent
from yahooquery import search  # 新增



            # <i>The Icon</i> 
            # 💬🤖💬⌚🚀👍👇👉👇🏼👋❤️🔥🖥️📱🏮🎬⚡⏰️🤯🎁📈📉✅🔗🎤🤑😕😊🌞📁🖼️🗑️⚙️⬅️🔐📋📸🚫💖👗🔎👾🦠🦾🔧❓
            # ✨💛🔔📚🌍📝🎵⏱️🕵️👨‍💻🐥⌚📰🛒🙏☕📑🧠🕒📅📖🚨🌟▶🐤🌐🎨🔖⭐️😎📊🏠🏛️🚩🟥🔴⚠️💰🎥🎵🎯❌🔺🔻💹🏆
            # </h1>""")
        


# Set page config 
st.set_page_config(layout='wide', page_title="SWARM", page_icon="📚", initial_sidebar_state="collapsed") #expanded #auto




import base64

# 將本地圖片轉換為 base64
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 取得本地圖片的 base64 編碼
img_path = r"D:\Digitimes_AI\APP\Images\back-1-up.png"
img_base64 = get_base64_of_bin_file(img_path)

# 設定背景圖片的CSS，讓圖片靠左並自動放大
page_bg_img = f'''
<style>
.stApp {{
    background-color: white;
}}

.header-section {{
    background: url("data:image/png;base64,{img_base64}") no-repeat left center;
    background-size: cover; /* 圖片自動放大，覆蓋整個區域 */
    height: 70px; /* 可根據需求調整高度 */
    position: relative;
}}


.header-content {{
    position: absolute;
    top: 35%;
    left: 2%;  /* 控制文字靠左顯示 */
    color: white;
    font-size: 2.0em;
    font-weight: bold;
    text-align: left;  /* 文字左對齊 */
    z-index: 10;
}}

</style>
'''

# 將CSS樣式應用到Streamlit應用
st.markdown(page_bg_img, unsafe_allow_html=True)
# 建立背景圖片區域並疊加文字
st.markdown('<div class="header-section"> <div class="header-content"> 🤖 Weather and Stock Information</div></div>', unsafe_allow_html=True)

st.markdown(   #主區域整體  向上移动 _____________________________________________________________________________________
    """
    <style>
    /* 只选择主区域的容器 */
    .block-container {
        margin-top: -70px;  /* 向上移动 10 像素，您可以根据需要调整数值 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.logo(r"D:\Digitimes_AI\APP\Images\Digitimes_log_big.png", icon_image=r"D:\Digitimes_AI\APP\Images\Digitimes_log.png")




#___________________________________________________________________
aa1, aa2, aa3 =st.columns([4,0.8,1])

with aa1 :
    option = st.radio(
        "Choose to query company or city:",
        ( "Company", "City","Others",),horizontal=True
    )

with aa2 :
    slideSearch = r"D:\Digitimes_AI\APP\Images\APP_link_small.png"
    st.image(slideSearch)
with aa3 :
    # st.write("")
    st.write("")
    if st.button("🚀 APP 應用專案平台!", key="app-2"):
        os.system(r"streamlit run D:\Digitimes_AI\APP\Home\App.py")
 #________________________________________________________________________


# Streamlit UI for user input
# st.title("Weather and Stock Information")

api_key_file = 'D:/Digitimes_AI/API_key.txt'

# Read API Key
def read_api_key(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            api_key_line = file.read().strip()
            return api_key_line.split('=', 1)[-1].strip() if '=' in api_key_line else ""
    return ""

api_key = read_api_key(api_key_file)

# Save API Key to environment variables
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key


#########################################################################################################


# Initialize Swarm client
client = Swarm()

# Load OpenWeatherMap API key from environment variable
# https://home.openweathermap.org/api_keys
API_KEY = "856d325aff86bdce566d8adfd797f88d"
if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY environment variable not set")

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# 全球及亞洲主要城市的繁體中文名單
city_list_zh = [
    "紐約", "倫敦", "東京", "巴黎", "悉尼", 
    "上海", "莫斯科", "柏林", "多倫多", "舊金山",
    "北京", "孟買", "香港", "新加坡", "首爾",
    "雅加達", "曼谷", "馬尼拉", "吉隆坡", "台北"
]

# 與中文名單對應的英文城市名單
city_list_en = [
    "New York", "London", "Tokyo", "Paris", "Sydney", 
    "Shanghai", "Moscow", "Berlin", "Toronto", "San Francisco",
    "Beijing", "Mumbai", "Hong Kong", "Singapore", "Seoul",
    "Jakarta", "Bangkok", "Manila", "Kuala Lumpur", "Taipei"
]

# 公司名稱及其對應的 Ticker 代號
company_list_zh = [
    "蘋果", "微軟", "台積電", "三星電子", "英特爾", 
    "英偉達", "超微半導體", "思科", "高通", "博通",
    "ASML", "索尼", "聯發科", "德州儀器", "應用材料",
    "美光科技", "ADI", "日月光", "聯電", "華為",
    "小米", "京東", "騰訊", "阿里巴巴", "百度",
    "Facebook (Meta)", "Google (Alphabet)", "亞馬遜", "甲骨文", "Adobe", "華碩"
]

# 對應的 Ticker 代號，並為非美國公司增加國家代碼
ticker_list = [
    "AAPL", "MSFT", "TSM", "005930.KS", "INTC",
    "NVDA", "AMD", "CSCO", "QCOM", "AVGO",
    "ASML", "SONY", "2454.TW", "TXN", "AMAT",
    "MU", "ADI", "ASX", "2303.TW", "HWT.UL",
    "1810.HK", "JD", "TCEHY", "BABA", "BIDU",
    "META", "GOOGL", "AMZN", "ORCL", "ADBE", "2357.TW"
]

# Function to fetch real weather data
def get_weather(location):
    params = {
        "q": location,
        "appid": API_KEY,
        "units": "metric",
        "lang": "zh_tw"  # 添加語言參數，獲取中文描述
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if response.status_code == 200 and 'main' in data:
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        city_name = data['name']
        return f"{city_name}的天氣為 {weather_description}，氣溫 {temperature}°C。"
    else:
        return f"無法取得 {location} 的天氣資訊。請再試一次。"

# Function to fetch stock price using yfinance
# def get_stock_price(ticker):
#     stock = yf.Ticker(ticker)
#     stock_info = stock.history(period="1d")
#     if not stock_info.empty:
#         latest_price = stock_info['Close'].iloc[-1]
#         return f"{ticker} 的最新股價為 {latest_price:.2f}。"
#     else:
#         return f"無法取得 {ticker} 的股價資訊。"


# 定義取得股價的函數，並以表格形式返回
def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    stock_info = stock.history(period="1mo")
    
    if not stock_info.empty:
        # 只提取收盤價和日期
        stock_info = stock_info[['Close']].reset_index()
        
        # 將日期格式化為 "月-日" 並更新表格
        stock_info['Date'] = stock_info['Date'].dt.strftime('%m-%d')
        
        # 將數據按日期降序排序，確保最近的時間在最左側
        stock_info = stock_info.sort_values(by='Date', ascending=False).reset_index(drop=True)
        
        # 將表格轉置，讓日期作為列標題
        stock_info = stock_info.set_index('Date').transpose()
        
        return stock_info
    else:
        return None




# Function to get ticker by company name
def get_ticker_by_company(company_name):
    if company_name in company_list_zh:
        return ticker_list[company_list_zh.index(company_name)]
    else:
        return None

# Updated find_ticker_online function using yahooquery
def find_ticker_online(company_name):
    result = search(company_name)
    if 'quotes' in result:
        for item in result['quotes']:
            exchange = item.get('exchange')
            quote_type = item.get('quoteType')
            if exchange in ['TAI', 'TAI2', 'HKG', 'NYQ', 'NMS'] and quote_type == 'EQUITY':
                return item['symbol']

    with st.expander("顯示搜尋結果", expanded=False):
        st.write(result)
    return None




# Function to handle non-US companies (e.g., find company in Taiwan)
def handle_non_us_companies(company_name):
    ticker = find_ticker_online(company_name)
    return ticker


# Function to transfer from manager agent to weather agent
def transfer_to_weather_assistant():
    return weather_agent

# Function to transfer from manager agent to stock price agent
def transfer_to_stockprice_assistant():
    return stockprice_agent

# Manager Agent
manager_agent = Agent(
    name="Manager Assistant",
    instructions="You help users by directing them to the right assistant. if stockk price included in the question, then pass to stockprice_agent.",
    functions=[transfer_to_weather_assistant, transfer_to_stockprice_assistant],
)


# Stock Price Agent with company name recognition and online lookup
stockprice_agent = Agent(
    name="Stock Price Assistant",
    instructions="You provide the latest stock price for a given company name or ticker symbol. If the user provides a company name, find the corresponding ticker symbol. If it's not available locally, look it up online. Handle non-US companies by finding their corresponding country code tickers.",
    functions=[get_stock_price, get_ticker_by_company, find_ticker_online, handle_non_us_companies],
)

# Weather Agent
weather_agent = Agent(
    name="Weather Assistant",
    instructions="You provide weather information for a given location using the provided tool",
    functions=[get_weather],
)


###############################################################################
# Adding a selection option for company or city
# option = st.radio(
#     "Choose to query company or city:",
#     ( "Company", "City","None",),horizontal=True
# )

# If user selects company, display the company list to select
if option == "Company":
    selected_company = st.selectbox("請選擇一家公司", company_list_zh)
    query = selected_company

# If user selects city, display the city list to select
elif option == "City":
    selected_city_zh = st.selectbox("請選擇一個城市", city_list_zh)
    query = city_list_en[city_list_zh.index(selected_city_zh)]  # Get the corresponding English name

# If no option selected, allow the user to input directly
else:
    query = st.text_input("Enter a location, company name or ticker symbol")


#################################################################################################
if st.button("Submit",type="primary"):

    if option == "Company":
        ticker = get_ticker_by_company(query)
        if ticker is None:
            ticker = handle_non_us_companies(query)
            if ticker is None:
                ticker = query  # Assume the input is the ticker


        #############################################################
        # 使用 get_stock_price 函數來取得過去一個月的股價
        stock_prices = get_stock_price(ticker)
        
        if stock_prices is not None:
            # 使用 Streamlit 顯示表格，並啟用橫向滾動
            st.write(f"{ticker} 的過去一個月股價：")
            
            # 顯示整個表格，並啟用橫向滾動條
            st.dataframe(stock_prices, width=1200)
        else:
            st.write(f"無法取得 {ticker} 的股價資訊。")



        #############################################################
        response = client.run(
            agent=manager_agent,
            messages=[{"role": "user", "content": f"Get me the stock price of {ticker}."}],
        )
        st.write(response.messages[-1]['content'])

        # 获取公司基本资料
        company_info_response = client.run(
            agent=manager_agent,
            messages=[{"role": "user", "content": f"Provide a 繁體中文 brief overview of the company with the ticker symbol {ticker}."}],
        )
        st.write(company_info_response.messages[-1]['content'])


    elif option == "City":
        response = client.run(
            agent=manager_agent,
            messages=[{"role": "user", "content": f"What's the weather in {query}?"}],
        )
        st.write(response.messages[-1]['content'])

        # 获取公司基本资料
        city_info_response = client.run(
            agent=manager_agent,
            messages=[{"role": "user", "content": f"Provide a 繁體中文 brief overview of the city_{query}, highlight the info of country and population."}],
        )
        st.write(city_info_response.messages[-1]['content'])




    else:
        # Attempt to find ticker by company name
        ticker = get_ticker_by_company(query)
        if ticker is None:
            ticker = handle_non_us_companies(query)
            if ticker is None:
                ticker = query  # Assume the input is the ticker

        # Check if ticker exists and try to get stock price
        if ticker:
            response = client.run(
                agent=manager_agent,
                messages=[{"role": "user", "content": f"Get me the stock price of {ticker}."}],
            )
            st.write(response.messages[-1]['content'])



        else:
            # If still cannot find ticker, try treating input as city name
            response = client.run(
                agent=manager_agent,
                messages=[{"role": "user", "content": f"What's the weather in {query}?"}],
            )
            st.write(response.messages[-1]['content'])










###########################################################
with st.sidebar : # 股票代碼查詢工具

    import streamlit as st
    import requests
    import pandas as pd
    from deep_translator import GoogleTranslator

    def translate_to_english(text):
        try:
            translator = GoogleTranslator(source='zh-TW', target='en')
            translated = translator.translate(text)
            return translated
        except Exception as e:
            st.error(f"翻譯時發生錯誤：{str(e)}")
            return text

    def find_ticker_online(company_name):
        # 檢查是否為中文
        if any('\u4e00' <= char <= '\u9fff' for char in company_name):
            english_name = translate_to_english(company_name)
            st.info(f"已將 '{company_name}' 翻譯為 '{english_name}'")
        else:
            english_name = company_name

        url = f'https://query2.finance.yahoo.com/v1/finance/search?q={english_name}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            
            if 'quotes' in data and data['quotes']:
                results = []
                for item in data['quotes']:
                    if item['quoteType'] == 'EQUITY':
                        results.append({
                            'Symbol': item['symbol'],
                            'Name': item.get('longname', item.get('shortname', 'N/A')),
                            'Exchange': item.get('exchange', 'N/A')
                        })
                return pd.DataFrame(results)
            else:
                return pd.DataFrame()
        except Exception as e:
            st.error(f"查詢時發生錯誤：{str(e)}")
            return pd.DataFrame()

    st.title('股票代碼查詢工具')

    company_name = st.text_input('請輸入公司名稱（中文或英文）：')

    if st.button('查詢'):
        if company_name:
            with st.spinner('正在查詢...'):
                df = find_ticker_online(company_name)
            
            if not df.empty:
                st.success(f'找到 {len(df)} 個結果：')
                st.dataframe(df)
            else:
                st.warning('沒有找到相關的股票資訊。請檢查公司名稱是否正確。')
        else:
            st.warning('請輸入公司名稱。')

    st.markdown("""
    ### 使用說明：
    1. 在輸入框中輸入公司名稱（可以是中文或英文）
    2. 如果輸入的是中文，系統會自動翻譯成英文
    3. 點擊"查詢"按鈕
    4. 系統將顯示相關的股票代碼信息

    注意：某些公司可能找不到資訊或顯示多個結果。請盡量使用準確的公司名稱。翻譯功能可能並不完美，如果查詢結果不準確，可以嘗試直接輸入英文名稱。
    """)

###########################################################


st.sidebar.write("---")
st.sidebar.write("全球氣候查詢 Source:https://home.openweathermap.org/api_keys")



st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("---")


st.subheader("SWARM_Agent 的 LLM 執行框架應用介紹 ! ")

youtube_url = "https://www.youtube.com/watch?v=HF3gLMI18jg"
st.markdown(f'[🎥 點擊觀看影片: OpenAI Swarm Multi Agent Framework: Will it replace CrewAI & AutoGen? ]({youtube_url})')

youtube_url = "https://www.youtube.com/watch?v=npAljHBeKPc"
st.markdown(f"[🎥 點擊觀看影片: Introducing Swarm with Code Examples: OpenAI's Groundbreaking Agent Framework ]({youtube_url})")



