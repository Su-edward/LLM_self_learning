CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY, -- 課程ID
    course_name VARCHAR(100), -- 課程名稱
    course_type ENUM('專業必修課', '通識課'), -- 課程性質
    department VARCHAR(100) -- 開課學院
);