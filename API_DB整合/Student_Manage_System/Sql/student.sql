CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY, -- 學號
    name VARCHAR(100), -- 姓名
    gender ENUM('男', '女'), -- 性別
    id_card VARCHAR(18), -- 身份證號碼
    email VARCHAR(100), -- 電子郵箱
    class_id INT -- 班級ID，與班級表關聯
);