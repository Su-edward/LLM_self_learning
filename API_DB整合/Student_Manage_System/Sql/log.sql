CREATE TABLE logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY, -- 日誌ID
    admin_id VARCHAR(20), -- 管理員工號
    operation VARCHAR(255), -- 操作內容
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 操作時間
    FOREIGN KEY (admin_id) REFERENCES administrators(admin_id)
