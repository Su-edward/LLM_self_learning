import mysql.connector
import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv


# 資料庫處理
class DB:
    def __init__(self):
        self.host = 'localhost'          # 連線主機名稱
        self.user = 'root'               # 登入帳號
        self.password = 'edward89618'    # 登入密碼
        self.cursor = None

    def connect(self):
        # 建立MySQL連線
        self.conn = mysql.connector.connect(
            host=self.host,          
            user=self.user,              
            password=self.password  
        )
        self.cursor = self.conn.cursor()       

    def disconnect(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        except:
            pass

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return None

    # 老師身分確認
    def check_account(self, account, password):
        self.cursor.execute("USE student_management_system")
        query = "SELECT * FROM administrators WHERE id_card=%s AND password=%s"
        self.cursor.execute(query, (account, password))
        result = self.cursor.fetchone()
        # 如果有結果，回傳名稱，否則回傳 None
        if result:
            return result[1]  # 回傳查詢到的名稱
        return None

    # 老師個人資料回傳
    def Teacher_info(self, name):
        self.cursor.execute("USE student_management_system")
        query = "SELECT * FROM administrators WHERE name=%s"
        self.cursor.execute(query, (name,))
        result = self.cursor.fetchone()
        # 如果查詢到結果，創建並回傳 Teacher 物件
        if result:
            return Teacher(*result)  # 使用解包符號 * 直接傳入結果
        return None

    # 更新資料庫中的 Teacher 資訊
    def Teacher_update(self,teacher):
        query = """
        UPDATE administrators
        SET name=%s, gender=%s, id_card=%s, email=%s, password=%s
        WHERE admin_id=%s
        """
        self.cursor.execute(query, (
            teacher.name,
            teacher.gender,
            teacher.id_card,
            teacher.email,
            teacher.password,
            teacher.admin_id
        ))
        self.conn.commit()  # 提交更改

    # 增加
    def add_student(self, student_id, name, gender, id_card, email, class_id, password):
        # 檢查是否已經有相同的 student_id
        check_query = "SELECT * FROM students WHERE student_id = %s"
        self.cursor.execute(check_query, (student_id,))
        existing_student = self.cursor.fetchone()

        if existing_student:
            st.error(f"學生 ID {student_id} 已經存在，請使用其他 ID。")
            st.rerun()
            return

        # 插入新的學生記錄
        insert_query = """
        INSERT INTO students (student_id, name, gender, id_card, email, class_id, password)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(insert_query, (student_id, name, gender, id_card, email, class_id, password))
            self.conn.commit()  # 提交變更
        except Exception as e:
            self.conn.rollback()  # 發生錯誤時回滾變更

    # 查詢學生資料，根據條件篩選，無條件時回傳所有資料
    def students_search(self, name=None, gender=None, student_class=None, select_fields="*"):
        self.cursor.execute("USE student_management_system")
        query = f"""
        SELECT students.student_id , students.name , students.gender , 
            students.id_card , students.email , classes.class_name , 
            students.password 
        FROM students 
        JOIN classes ON students.class_id = classes.class_id
        WHERE 1=1
        """
        params = []

        # 根據條件篩選
        if name:
            query += " AND name LIKE %s"
            params.append(f"%{name}%")
        if gender and gender!="全部":
            query += " AND gender = %s"
            params.append(gender)
        if student_class and student_class!="全部":
            query += " AND classes.class_name = %s"
            params.append(student_class)

        # 執行SQL語句
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    # 刪除學生資料   
    def delete_students(self, ids):
        if not ids:
            return
        try:
            # 刪除 grades 表中與學生相關的記錄
            query_grades = "DELETE FROM grades WHERE student_id IN (%s)" % ','.join(['%s'] * len(ids))
            self.cursor.execute(query_grades, tuple(ids))

            # 刪除 students 表中的記錄
            query_students = "DELETE FROM students WHERE student_id IN (%s)" % ','.join(['%s'] * len(ids))
            self.cursor.execute(query_students, tuple(ids))

            self.conn.commit()  # 提交變更
        except Exception as e:

            self.conn.rollback()  # 如果發生錯誤，回滾變更

    # 查詢學生及其成績的聯合表
    def get_grades(self, name=None, course_name=None,class_name = None, min_score=None, max_score=None):
        self.cursor.execute("USE student_management_system")
        
        # 基本查詢語句，將 students 和 grades 表進行 JOIN
        query = """
            SELECT s.student_id, s.name,cl.class_name,
                c.course_name,  g.score, g.exam_method, g.credit, g.exam_date 
            FROM students AS s
            JOIN grades AS g ON s.student_id = g.student_id
            JOIN courses AS c ON g.course_id = c.course_id
            JOIN classes AS cl ON s.class_id = cl.class_id
            WHERE 1=1
        """
        
        params = []

        # 根據條件進行篩選
        if name:
            query += " AND s.name LIKE %s"
            params.append(f"%{name}%")
        
        if course_name and course_name != "全部":
            query += " AND c.course_name = %s"
            params.append(course_name)
        if class_name:
            query += " AND cl.class_name LIKE %s"
            params.append(f"%{class_name}%")

        if min_score:
            query += " AND g.score >= %s"
            params.append(min_score)
        
        if max_score:
            query += " AND g.score <= %s"
            params.append(max_score)

        # 執行 SQL 語句
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    # 查詢所有學科類型（課程名稱）
    def get_class_type(self):
        self.cursor.execute("USE student_management_system")
        
        # 正確的 SQL 語句來查詢 course_name
        query = "SELECT course_name FROM courses"
        # 執行查詢
        self.cursor.execute(query)
        # 獲取所有結果而不是單一結果
        result = self.cursor.fetchall()
        # 如果有結果，回傳結果
        if result:
            return [course[0] for course in result]  # 提取出純文本（course_name）
        return None  # 如果沒有結果，返回 None


    # 查詢所有班級
    def get_class(self):
        self.cursor.execute("USE student_management_system")
        
        # 正確的 SQL 語句來查詢 course_name
        query = "SELECT class_name FROM classes"
        # 執行查詢
        self.cursor.execute(query)
        # 獲取所有結果而不是單一結果
        result = self.cursor.fetchall()
        # 如果有結果，回傳結果
        if result:
            return [course[0] for course in result]  # 提取出純文本（course_name）
        return None  # 如果沒有結果，返回 None

# 老師類別
class Teacher:
    def __init__(self, admin_id, name, gender, id_card, email, password):
        self.admin_id = admin_id
        self.name = name
        self.gender = gender
        self.id_card = id_card
        self.email = email
        self.password = password

    # 返回一個字串，當使用str(teacher)
    def __str__(self):
        return f"{self.name}"

    def get_details(self):
        return {
            'admin_id': self.admin_id,
            'name': self.name,
            'gender': self.gender,
            'id_card': self.id_card,
            'email': self.email,
            'password': self.password
        }
    # 更新 Teacher 實例的屬性
    def update_info(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)


# 大語言
class LLM:
    def __init__(self):
        self.api_key = "你的Openai_Key"
    def analyze_student_scores(self,data):

        client = OpenAI(api_key=self.api_key)
        prompt = f"""以下是學生的成績數據，每行記錄一個學生的學號、姓名、班級、科目名稱、分數、評分方式、學分和考試日期。
        請你依據這些成績數據，分析每位學生的學業表現，並給出建議。特別關注分數低於60分的科目，
        指出需要改進的地方並給出具體學習建議：\n\n{data}\n\n請根據每位學生的表現給出合理的分析和建議，
        並總結他們的學習強項與弱項。不要加入額外的語句，只需逐條列出每位學生的分析結果。"""

        # 調用 OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": "你是一個專業的教育顧問，負責為學生提供成績分析和學習建議。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回 GPT 模型的分析結果
        return response.choices[0].message.content
    def analyze_class_performance(self,data):
        client = OpenAI(api_key=self.api_key)
        prompt = f"""以下是某個班級學生的成績數據，每行記錄一個學生的學號、姓名、班級、科目名稱、分數、評分方式、
        學分和考試日期。請根據這些數據，對整個班級的學業表現進行分析，總結班級的強項科目與弱項科目，並給出改善弱項
        的建議：\n\n{data}\n\n請提供班級整體表現的分析報告，包含強弱項科目的總結和建議。"""

        # 調用 OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": "你是一個負責分析班級整體學業表現的教育顧問。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回 GPT 模型的分析結果
        return response.choices[0].message.content
    

    def analyze_specific_subject_performance(self, score_distribution_data):
        client = OpenAI(api_key=self.api_key)
        prompt = f"以下是某個學科的成績分佈數據，包含不同分數區間的學生數量。請根據這些數據分析該學科的學生表現，並給出具體建議，特別關注分數低於60分的學生，分析他們需要在哪些方面進行改進。數據如下：\n\n{score_distribution_data}\n\n請根據這些數據給出分析，並對學生成績分佈和學習建議做出總結。"

        # 調用 OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {"role": "system", "content": "你是一個專業的教育顧問，負責分析學科成績分佈和提供學習建議。"},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 返回 GPT 模型的分析結果
        return response.choices[0].message.content
