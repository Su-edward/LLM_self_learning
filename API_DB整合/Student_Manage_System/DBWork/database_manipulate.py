import mysql.connector
import streamlit as st

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
        query = f"SELECT {select_fields} FROM students WHERE 1=1"
        params = []

        # 根據條件篩選
        if name:
            query += " AND name LIKE %s"
            params.append(f"%{name}%")
        if gender and gender!="全部":
            query += " AND gender = %s"
            params.append(gender)
        if student_class:
            query += " AND class_id = %s"
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



