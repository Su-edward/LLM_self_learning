import re
from DBWork.database_manipulate import DB,LLM
import streamlit as st
import pandas as pd
import os
import re





if __name__ == "__main__":
    st.title("成績資訊")

    # 資料庫連結
    database = DB()
    database.connect()

    # 設置篩選條件
    col1,col2,col3 = st.columns([0.3,0.3,0.3])
    with col1:
        selected_name = st.text_input("輸入學生姓名",value="")
    with col2:
        course_names = database.get_class_type()
        course_names.insert(0, "全部")
        selected_course_name = st.selectbox("選擇課程", options=course_names)
    with col3:
        selected_score_range = st.slider(
            "選擇分數區間", 
            min_value=0, max_value=100, 
            value=(0, 100)  # 默認範圍
        )

    grade = database.get_grades( name=selected_name, course_name=selected_course_name,min_score=selected_score_range[0]
                                , max_score=selected_score_range[1])
    grade_df = pd.DataFrame(grade, columns=['學號','姓名','班級', '學科','分數','測驗方式', '學分','日期'])
    st.dataframe(grade_df,use_container_width=True,height=400 )# 確保表格占滿可用空間)


    AI_Assistan = LLM()
    if st.button("AI分析"):
        with st.expander("分析結果"):
            st.write(AI_Assistan.analyze_class_performance(grade))

