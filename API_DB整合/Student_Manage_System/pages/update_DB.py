from DBWork.database_manipulate import DB, Teacher
from streamlit_autorefresh import st_autorefresh 
import streamlit as st
import time



@st.dialog("確認更新")
def Confirm( Db_items : DB, Teacher_item:Teacher):
    col1,col2 = st.columns([0.5,0.5])
    with col1:
        if st.button("更新確認"):
            Db_items.Teacher_update(Teacher_item)
            st.session_state["administor"] = str(Teacher_item)
            with st.spinner("更新中"):
                time.sleep(3)
                st.rerun()
    with col2:
        if st.button("取消更新"):
            Teacher_item = database.Teacher_info(teacher_name)
            with st.spinner("取消"):
                st.rerun()

if __name__ == "__main__":

    st.title("老師個人資訊")

    teacher_name = st.session_state["administor"]
    # 資料庫連結
    database = DB()
    database.connect()

    # 資料取得
    teacher = database.Teacher_info(teacher_name)
    Teacher_info = teacher.get_details()


    # 顯示資料庫內容
    st.text(f"ID號:{Teacher_info['admin_id']}")
    Name = st.text_input('名稱:', value=Teacher_info['name'])
    Gender = st.selectbox('性別:', options=['男', '女'], index=0 if Teacher_info['gender'] == '男' else 1)
    Account = st.text_input('帳號:', value=Teacher_info['id_card'])
    Passward = st.text_input('密碼:', value=Teacher_info['password'], type="password")
    Email = st.text_input('電子信箱:', value=Teacher_info['email'])

    if st.button("修改資訊"):
        # 更新 teacher 實例中的屬性
        teacher.update_info(name=Name,gender=Gender,id_card=Account,password=Passward, email=Email)
        Confirm(database, teacher)
