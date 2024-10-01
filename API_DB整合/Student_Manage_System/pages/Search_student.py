import re
from DBWork.database_manipulate import DB, Teacher
import streamlit as st
import pandas as pd
import time
import re

@st.dialog("確認刪除")
def Confirm( Db_items : DB, Delete_List:list,Delete_id:list):
    st.dataframe(Delete_List.drop(columns=['選擇']))
    st.write(f"即將刪除的學生ID: {Delete_id}")
    col1,col2 = st.columns([0.5,0.5])
    with col1:
        if st.button("確認刪除"):
            Db_items.delete_students(Delete_id)
            with st.spinner("刪除中"):
                time.sleep(3)
                st.info("刪除成功")
                time.sleep(1)
                st.rerun()
    with col2:
        if st.button("取消刪除"):
            st.rerun()
            

@st.dialog("資料新增")
def Insert(database:DB):
    with st.form("student_form", clear_on_submit=True):
        student_id = st.text_input("學生 ID", placeholder="必須是數字且長度固定為6位數").strip()
        name = st.text_input("姓名", placeholder="輸入學生姓名").strip()
        gender = st.selectbox("性別", ["男", "女"], index=0)
        id_card = st.text_input("身份證號碼", placeholder="必須是10位數").strip()
        email = st.text_input("電子郵件", placeholder="example@domain.com").strip()
        class_id = st.text_input("班級編號", placeholder="1-12").strip()
        password = st.text_input("密碼", type="password", value="123456").strip()


        # 表單提交按鈕
        submitted = st.form_submit_button("新增學生")
        if submitted:
            # 檢查學生 ID 是否為 6 位數字
            if not (student_id.isdigit() and len(student_id) == 6):
                st.error("學生 ID 必須是 6 位數字。")
                time.sleep(2)
                st.rerun()
            # 檢查身份證號碼是否為 10 位數字
            elif not (id_card.isdigit() and len(id_card) == 10):
                st.error("身份證號碼必須是 10 位數字。")
                time.sleep(2)
                st.rerun()
            # 檢查電子郵件格式
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("請輸入有效的電子郵件地址。")
                time.sleep(2)
                st.rerun()
            # 檢查班級編號是否在 1 到 12 之間
            elif not (class_id.isdigit() and 1 <= int(class_id) <= 12):
                st.error("班級編號必須是 1 到 12 之間的數字。")
                time.sleep(2)
                st.rerun()
            # 檢查是否有未填字段
            elif not (student_id and name and gender and id_card and email and class_id and password):
                st.error("請填寫所有必填字段。")
                time.sleep(2)
                st.rerun()
            else:
                # 所有檢查通過後，新增學生
                database.add_student(student_id, name, gender, id_card, email, class_id, password)
                with st.spinner("新增中"):
                    time.sleep(3)
                    st.info("新增成功")
                    time.sleep(1)
                    st.rerun()
            



if __name__ == "__main__":
    st.title("學生資訊")

    # 資料庫連結
    database = DB()
    database.connect()

    # 設置篩選條件
    col1,col2,col3 = st.columns([0.3,0.3,0.3])
    with col1:
        selected_name = st.text_input("輸入學生姓名",value="")
    with col2:
        selected_gender = st.selectbox("選擇性別", options=["全部", "男", "女"])
    with col3:
        selected_student_class = st.text_input("輸入班級號碼",value="")

    # 查詢並顯示學生資料
    student_data = database.students_search(name=selected_name, gender=selected_gender, student_class=selected_student_class)

    # 刪除列表
    delete_student = []
    selected_ids = []
    if student_data:
        student_df = pd.DataFrame(student_data, columns=['ID','姓名', '性別','學號','帳號', '班級','密碼'])
        # 添加一個選擇框到每一行
        student_df.insert(0, '選擇', False)
        # 顯示有選擇框的資料表
        edited_df = st.data_editor(
            student_df,
            hide_index=True,
            column_config={
                "選擇": st.column_config.CheckboxColumn(
                    "選擇",
                    help="選擇要顯示詳細資訊的行",
                    default=False,
                )
            },
            disabled=student_df.columns.drop('選擇'),
            use_container_width=True  # 確保表格占滿可用空間
        )
        # 獲取所有被勾選的行
        selected_ids = edited_df[edited_df['選擇'] == True]['ID'].tolist()
        delete_student = edited_df[edited_df['選擇'] == True]


    col1,col2 = st.columns([0.5,0.5])
    with col1:
        if st.button("新增學生"):
            Insert(database)
    with col2:
        # 顯示刪除按鈕，並執行刪除操作
        if st.button("刪除選中的學生"):
            Confirm(database,delete_student,selected_ids)
    




