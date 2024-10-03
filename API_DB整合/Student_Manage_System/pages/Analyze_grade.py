from matplotlib import font_manager
from DBWork.database_manipulate import DB, LLM
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import re


if __name__ == "__main__":
    # 設置字體文件路徑
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 修改中文字體
    plt.rcParams['axes.unicode_minus'] = False  # 顯示負號

    st.title("成績資訊")

    # 資料庫連結
    database = DB()
    database.connect()

    target = st.selectbox("分析目標",["科目","班級"])



    if target=="科目":
        course_names = database.get_class_type()
        selected_course_name = st.selectbox("選擇課程", options=course_names)
        grade = database.get_grades(  course_name=selected_course_name)
        grade_df = pd.DataFrame(grade, columns=['學號','姓名','班級', '學科','分數','測驗方式', '學分','日期'])


        with st.expander("原始成績"):
            st.dataframe(grade_df)

        # 分數區間劃分
        score_ranges = [0, 60, 70, 80, 90, 100]
        # 計算每個區間的學生數量
        score_categories = pd.cut(grade_df['分數'], bins=score_ranges)
        score_counts = grade_df.groupby(score_categories).size()

        # 繪製圖表
        fig, ax = plt.subplots()
        score_counts.plot(kind='bar', color='blue', ax=ax, width=0.2) 

        # 設定標題和軸標籤
        ax.set_title(f"{selected_course_name} 成績分佈")
        ax.set_xlabel("分數區間")
        ax.set_ylabel("人數")
        # 修正 x 軸標籤的方向
        plt.xticks(rotation=0)  # 使 x 軸標籤不旋轉
        # 顯示圖表
        st.pyplot(fig)
    
        AI_Assistan = LLM()
        if st.button("AI分析"):
            with st.expander("分析結果"):
                st.write(AI_Assistan.analyze_specific_subject_performance(grade))

    elif target =="班級":
        class_names = database.get_class()
        selected_class_name = st.selectbox("選擇班級", options=class_names)
        grade = database.get_grades(  class_name=selected_class_name)
        grade_df = pd.DataFrame(grade, columns=['學號','姓名','班級', '科目','分數','測驗方式', '學分','日期'])
        with st.expander("原始成績"):
            st.dataframe(grade_df)

        # 計算每個科目的最高分、最低分、平均分、標準差
        grouped_stats = grade_df.groupby('科目')['分數'].agg(['max', 'min', 'mean', 'median']).reset_index()


        # 繪製圖表
        fig, ax = plt.subplots()

        x = range(len(grouped_stats['科目']))  # x 軸的科目數量
        widths = 0.15  

        # 繪製各個統計值的柱狀圖
        ax.bar([i - 2*0.15 for i in x], grouped_stats['max'], width=0.15, label='最高分', color='blue')
        ax.bar([i - 0.15 for i in x], grouped_stats['min'], width=0.15, label='最低分', color='red')
        ax.bar(x, grouped_stats['mean'], width=0.15, label='平均分', color='gray')
        ax.bar([i + 0.15 for i in x], grouped_stats['median'], width=0.15, label='中位數', color='green')
        # ax.bar([i + 2*0.15 for i in x], grouped_stats['std'], width=0.15, label='標準差', color='orange')

        # 設定圖表標題和軸標籤
        ax.set_title(f"{selected_class_name} 班級成績統計")
        ax.set_xlabel("科目")
        ax.set_ylabel("分數")

        # 設置 x 軸刻度標籤
        ax.set_xticks(x)
        ax.set_xticklabels(grouped_stats['科目'], rotation=45, ha='right')

        # 調整圖例位置，將圖例移到圖表外面
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

        # 調整圖表布局，以確保圖表和圖例不重疊
        plt.tight_layout()

        # 顯示圖表
        st.pyplot(fig)

        AI_Assistan = LLM()
        if st.button("AI分析"):
            with st.expander("分析結果"):
                st.write(AI_Assistan.analyze_class_performance(grade))

    else:
        grade = database.get_grades(  course_name=selected_course_name)
        grade_df = pd.DataFrame(grade, columns=['學號','姓名','班級', '學科','分數','測驗方式', '學分','日期'])
        st.dataframe(grade_df,use_container_width=True )# 確保表格占滿可用空間)

    database.disconnect()
