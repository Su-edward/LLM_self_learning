import pandas as pd
from notion_client import Client
import requests
import streamlit as st
from datetime import datetime, timedelta


token = "" 
database_id = ""
Line_token = ""

# 設定函數
def lineNotifyMessage(Line_token, msg):
    headers = {
        "Authorization": "Bearer " + Line_token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)
    return r.status_code

# 查詢
def getNotionDB(database_id, token):
    notion = Client(auth=token)

    # 取得資料庫中的所有資料
    results = notion.databases.query(database_id).get("results") # type: ignore

    # 將 Notion 資料轉換成 Pandas DataFrame
    data = []
    df = pd.DataFrame(results)

    i=0
    for item in results:
        i+=1
        name_elements = item["properties"]["Name"]["title"]
        name = "".join([element['text']['content'] for element in name_elements if 'text' in element])
        date = item["properties"]["Date"]["date"]["start"] if "Date" in item["properties"] and "date" in item["properties"]["Date"] else None
        message = "".join([element['text']['content'] for element in item["properties"]["Message"]["rich_text"] if 'text' in element]) if "Message" in item["properties"] else ""
        trigger = item["properties"]["Trigger"]["select"]["name"]
        group = item["properties"]["Group"]["select"]["name"]

        # 加入到列表中
        data.append({
            "ID":i,
            "Name": name,
            "Date": date,
            "Message": message,
            "Trigger": trigger,
            "Group" : group
        })
  
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":

    # Streamlit 應用程式
    st.title("Notion 資料進行 Line Notify推播")

    if "Db_state" not in st.session_state:
        st.session_state["Db_state"] = False
    if "Df" not in st.session_state:
        st.session_state["Df"] = ""
    # 使用者輸入 Notion API Token 和 Database ID
    with st.sidebar:
        st.header("請輸入對應資料",divider="rainbow")
        token = st.text_input("Enter your Notion API Token",value=token,type='password')
        database_id = st.text_input("Enter your Notion Database ID",value=database_id,type='password')
        Line_token = st.text_input("Enter your Line notify token",value=Line_token,type='password')

    # 當使用者輸入所有必要資訊後執行
    if st.sidebar.button("讀取資料"):
        if token and database_id:
            try:
                df = getNotionDB(database_id, token)
                st.sidebar.success("資料取得成功!")
                st.dataframe(df, width=800)
                st.session_state["Db_state"] = True
                st.session_state["Df"] = df
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("請提供 Notion API Token 和 Database ID.")

    # 按下按鈕來執行推播
    if st.button("進行通知") and st.session_state["Db_state"]:
        current_date = datetime.now().strftime('%Y-%m-%d')
        previous_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        sent_count = 0

        for index, row in st.session_state["Df"].iterrows():
            # 取得行程時間，只保留年月日
            scheduled_date = datetime.strptime(row['Date'][:10], '%Y-%m-%d').strftime('%Y-%m-%d')

            # 檢查年月日是否匹配，並確認 'Trigger' 為 'Yes'
            if (scheduled_date == current_date or scheduled_date == previous_date) and row['Trigger'] == 'Yes':
                lineNotifyMessage(Line_token, row['Name']+"_"+row['Message'])
                st.success(f"{row['Message']}: 訊息已傳送")
                sent_count += 1
        if sent_count > 0:
            pass
        else:
            st.info("無到期通知訊息")
    else:
        st.info("請輸入正確的 API 資訊，並讀取資料")
