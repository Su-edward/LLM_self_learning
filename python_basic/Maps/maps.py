import streamlit as st
from streamlit_folium import st_folium
import folium
from json import load
from swarm import Swarm, Agent
from streamlit_autorefresh import st_autorefresh 
from dotenv import load_dotenv
import requests
import os

# 地址類型
places = [
    "accounting", "airport", "amusement_park", "aquarium", "art_gallery", "atm", 
    "bakery", "bank", "bar", "beauty_salon", "bicycle_store", "book_store", 
    "bowling_alley", "bus_station", "cafe", "campground", "car_dealer", "car_rental", 
    "car_repair", "car_wash", "casino", "cemetery", "church", "city_hall", 
    "clothing_store", "convenience_store", "courthouse", "dentist", "department_store", 
    "doctor", "drugstore", "electrician", "electronics_store", "embassy", 
    "fire_station", "florist", "funeral_home", "furniture_store", "gas_station", "gym", 
    "hair_care", "hardware_store", "hindu_temple", "home_goods_store", "hospital", 
    "insurance_agency", "jewelry_store", "laundry", "lawyer", "library", 
    "light_rail_station", "liquor_store", "local_government_office", "locksmith", 
    "lodging", "meal_delivery", "meal_takeaway", "mosque", "movie_rental", 
    "movie_theater", "moving_company", "museum", "night_club", "painter", "park", 
    "parking", "pet_store", "pharmacy", "physiotherapist", "plumber", "police", 
    "post_office", "primary_school", "real_estate_agency", "restaurant", 
    "roofing_contractor", "rv_park", "school", "secondary_school", "shoe_store", 
    "shopping_mall", "spa", "stadium", "storage", "store", "subway_station", 
    "supermarket", "synagogue", "taxi_stand", "tourist_attraction", "train_station", 
    "transit_station", "travel_agency", "university", "veterinary_care", "zoo"
]

# 天氣
def get_weather(latitude: float, longitude: float) -> str:
    """
    使用Open-Meteo API獲取給定座標的當前天氣。

    參數:
    latitude (float): 緯度
    longitude (float): 經度

    返回:
    str: 包含當前溫度和風速的天氣資訊JSON字串
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        current = data['current']
        return str(current)  # 返回JSON字串
    else:
        return '{"error": "無法獲取天氣資料"}'

# 查詢附近地址
def find_place(lat, lon, radius,type):
    
    api_key  = os.getenv('GOOGLEAPI')  # 替換為您自己的Google API密鑰
    # 定義API的URL
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lon}&radius={5000}&type={type}&key={api_key}"
    )
    # 發送GET請求
    response = requests.get(url)
    data = response.json()

    # 檢查API回應狀態
    if data['status'] == 'OK':
        results = data['results']
        places = []
        for place in results:
            name = place['name']
            address = place.get('vicinity', '無地址資訊')
            location = place['geometry']['location']
            places.append({
                '名稱': name,
                '地址': address,
                '經度': location['lat'],
                '緯度': location['lng']
            })
        return place
    else:
        return f"Error fetching data: {data['status']}"

# 運行
def run_weather_query(query: str) -> str:
    messages = [{"role": "user", "content": query}]
    response = client.run(agent=place_agent, messages=messages)
    return response.messages[-1]["content"]


if "lat" not in st.session_state:
    st.session_state['lat'] = 25.0330
if "lng" not in st.session_state:
    st.session_state['lng'] = 121.5654
if "response" not in st.session_state:
    st.session_state['response'] = ""



client = Swarm()
place_agent = Agent(
    name="地址助手",
    instructions=f"""
    你是一個有幫助的地址搜尋助手。當被問到特定位置的天氣時：
    1. 你跟根據提供的經度:{st.session_state['lng']}，緯度: {st.session_state['lat']}，使用get_weather函數獲取天氣資料。
    2. 解析返回的JSON資料，提供一個友好的回覆，包含天氣資訊。如果無法識別該位置，禮貌地通知使用者並建議他們嘗試一個主要城市。
    當被問到特定位置的附近建築或是使用者想做什麼事時：
    1. 跟使用者的問題判斷，使用{places}的內容，判斷使用者想要搜尋的地址類型，不要加入其他內容
    ，只要獲取回答一種{places}中的類型就好。
    2. 使用獲取的類型結合目前經度:{st.session_state['lng']}，目前緯度: {st.session_state['lat']}，使用find_place進行地址的搜尋，根據回傳回來的陣列
    解析返回的JSON資料，提供一個友好的回覆，並使用google地圖根據推薦地址的經緯度以及目前經緯度提供一個路徑規劃的連結分享，如果無法正確，禮貌地通知使用者附近所蒐尋的類型建議無法搜尋。
    """,
    functions=[get_weather,find_place]
)


if __name__ == "__main__":

    # sidebar 說明
    with st.sidebar:
        st.header("天氣顯示功能", divider="rainbow")
        st.write("點選地圖取得經緯度，可詢問取該位置天氣如何，或想在附近做什麼?AI會根據對應經緯度回答建議!")
        st.subheader("", divider="gray")


    # 使用 st_folium 來顯示地圖並接受點擊回傳
    st.header("點擊地圖來顯示經緯度：")
    lat = st.session_state['lat']
    lon = st.session_state['lng']
    # 清除原來的地圖物件，並添加新標記
    m = folium.Map(location=[lat, lon], zoom_start=12)
    folium.Marker(location=[lat, lon], popup=f"Lat: {lat}, Lon: {lon}").add_to(m)
    
    # 更新後再顯示地圖
    output = st_folium(m, height=600, width=800)  # 使用新的key來更新地圖
    # 如果使用者點擊地圖，顯示經緯度並在該點標記
    if output['last_clicked']:
        lat = output['last_clicked']['lat']
        lon = output['last_clicked']['lng']
        st.session_state['lat'] = lat
        st.session_state['lng'] = lon
        st_autorefresh(interval=500, limit=2)
    if st.session_state['lat'] != 25.0330:
        st.write(f"你點擊的位置的經度為: {lon}, 緯度為: {lat}")
        prompt = st.chat_input("請輸入天氣或是附近地點問題")
        if prompt:
            st.session_state['response'] = run_weather_query(prompt)
            st_autorefresh(interval=500, limit=2)
    if st.session_state['response'] !="":
        st.write(st.session_state['response'])
