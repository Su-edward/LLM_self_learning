from streamlit_option_menu import option_menu
from DBWork.database_manipulate import DB
from streamlit_autorefresh import st_autorefresh 
import streamlit as st
import pandas as pd
import time
import re



# 彈出輸入框以新增聯絡人
@st.dialog("登入資訊")
def popup_dialog():
    account = st.text_input('Account')
    password = st.text_input('Password')
    if st.button('Submit'):
        st.session_state["account"] =  account
        st.session_state["password"] = password
        st.rerun()


# 定義不同的頁面內容
def homepage():
    with open("home.py", "r", encoding="utf-8") as file:
        exec(file.read())  # 讀取和執行DB.py的內容
def data_management():
    with open("pages/update_DB.py", "r", encoding="utf-8") as file:
        exec(file.read())  
def student_info():
    with open("pages/Search_student.py", "r", encoding="utf-8") as file:
        exec(file.read())  # 讀取和執行DB.py的內容
def report_generation():
    with open("pages/report.py", "r", encoding="utf-8") as file:
        exec(file.read())  # 讀取和執行whisper_txt.py的內容





if __name__ == "__main__":

    with st.sidebar:
        st.title("學生資訊管理系統")
        st.header("教師端操作",divider="rainbow")
        selected = option_menu(None, ["個人資料", "學生查詢", '成績查詢'], 
            icons=['house', 'cloud-upload', "list-task", 'gear'], 
            menu_icon="cast", default_index=0,
            styles={
                "nav-link": {"font-size": "15px"},  # 在這裡調整字體大小
                "icon": {"font-size": "15px"}  # 這裡也可以調整圖標大小
            }
        )
        st.header("",divider="gray")

    # 資料庫連結
    database = DB()
    database.connect()

    if "account" not in st.session_state:
        st.session_state["account"] = None
        st.session_state["password"] = None
        st.session_state["administor"] = None


    if st.session_state["administor"] == None:
        # 確認是否登入成功
        if st.session_state["account"] == None:
            popup_dialog()
        else:
            st.session_state["administor"] = database.check_account(st.session_state["account"], st.session_state["password"])
            if st.session_state["administor"]:
                st.success("登入成功！")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤！")
                st.session_state["administor"] = None
                st.session_state["account"] = None
                st.session_state["password"] = None
                st.rerun()

    else:
        teacher_name = st.session_state["administor"]
        if selected == "個人資料":
            data_management()
        elif selected == "學生查詢":
            student_info()
        else:
            pass

