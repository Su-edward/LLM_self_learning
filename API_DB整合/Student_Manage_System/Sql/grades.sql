CREATE TABLE grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY, -- 成績ID
    student_id VARCHAR(20), -- 學號，與學生表關聯
    course_id INT, -- 課程ID，與課程表關聯
    score DECIMAL(5, 2), -- 成績
    exam_method ENUM('考試', '測驗'), -- 考試方式
    credit DECIMAL(3, 1), -- 學分
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);