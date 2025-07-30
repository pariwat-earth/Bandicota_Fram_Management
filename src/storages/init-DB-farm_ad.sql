-- =================================================================
-- Report Tables Addition to Farm Management Database
-- เพิ่มตารางสำหรับการจัดเก็บข้อมูลรายงาน
-- =================================================================

-- Table: report_cache (แคชข้อมูลรายงาน)
CREATE TABLE IF NOT EXISTS report_cache (
    cache_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type     TEXT NOT NULL,          -- ประเภทรายงาน (breeding_performance, health_statistics, etc.)
    period_type     TEXT,                   -- ประเภทช่วงเวลา (1W, 1M, 3M, 6M, 1Y)
    cache_date      DATE DEFAULT CURRENT_DATE,
    cache_data      TEXT,                   -- JSON ข้อมูลแคช
    expires_at      DATETIME,               -- วันหมดอายุของแคช
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: report_settings (การตั้งค่ารายงาน)
CREATE TABLE IF NOT EXISTS report_settings (
    setting_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_name    TEXT UNIQUE NOT NULL,   -- ชื่อการตั้งค่า
    setting_value   TEXT,                   -- ค่าการตั้งค่า (JSON format)
    description     TEXT,                   -- คำอธิบาย
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: report_history (ประวัติการสร้างรายงาน)
CREATE TABLE IF NOT EXISTS report_history (
    history_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type     TEXT NOT NULL,
    generated_by    TEXT,                   -- ผู้สร้างรายงาน
    generated_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    parameters      TEXT,                   -- พารามิเตอร์ที่ใช้ (JSON format)
    execution_time  REAL,                   -- เวลาที่ใช้ในการสร้าง (milliseconds)
    status          TEXT DEFAULT 'success' CHECK (status IN ('success', 'failed', 'pending'))
);

-- =================================================================
-- INDEXES FOR PERFORMANCE
-- =================================================================

CREATE INDEX IF NOT EXISTS idx_report_cache_type ON report_cache (report_type);
CREATE INDEX IF NOT EXISTS idx_report_cache_date ON report_cache (cache_date);
CREATE INDEX IF NOT EXISTS idx_report_cache_expires ON report_cache (expires_at);
CREATE INDEX IF NOT EXISTS idx_report_settings_name ON report_settings (setting_name);
CREATE INDEX IF NOT EXISTS idx_report_history_type ON report_history (report_type);
CREATE INDEX IF NOT EXISTS idx_report_history_date ON report_history (generated_at);

-- =================================================================
-- TRIGGERS FOR AUTOMATIC CLEANUP
-- =================================================================

-- Trigger: ลบแคชที่หมดอายุอัตโนมัติ
CREATE TRIGGER IF NOT EXISTS cleanup_expired_cache
    AFTER INSERT ON report_cache
    FOR EACH ROW
BEGIN
    DELETE FROM report_cache 
    WHERE expires_at < datetime('now') 
    AND cache_id != NEW.cache_id;
END;

-- Trigger: จำกัดจำนวนประวัติรายงาน (เก็บแค่ 1000 รายการล่าสุด)
CREATE TRIGGER IF NOT EXISTS limit_report_history
    AFTER INSERT ON report_history
    FOR EACH ROW
BEGIN
    DELETE FROM report_history 
    WHERE history_id NOT IN (
        SELECT history_id 
        FROM report_history 
        ORDER BY generated_at DESC 
        LIMIT 1000
    );
END;

-- =================================================================
-- VIEWS FOR EASY DATA ACCESS
-- =================================================================

-- View: รายงานประสิทธิภาพการผสมพันธุ์ (30 วันล่าสุด)
CREATE VIEW IF NOT EXISTS v_breeding_performance_30d AS
SELECT 
    DATE(breeding_date) as breeding_date,
    COUNT(*) as total_breedings,
    SUM(CASE WHEN breeding_status = 'success' THEN 1 ELSE 0 END) as successful_breedings,
    ROUND(
        CAST(SUM(CASE WHEN breeding_status = 'success' THEN 1 ELSE 0 END) AS REAL) / 
        COUNT(*) * 100, 2
    ) as success_rate,
    AVG(CASE WHEN breeding_status = 'success' THEN total_pups ELSE NULL END) as avg_pups,
    AVG(CASE WHEN breeding_status = 'success' THEN albino_pups ELSE NULL END) as avg_albino
FROM breeding
WHERE breeding_date >= date('now', '-30 days')
GROUP BY DATE(breeding_date)
ORDER BY breeding_date DESC;

-- View: สถิติสุขภาพรายวัน (30 วันล่าสุด)
CREATE VIEW IF NOT EXISTS v_health_daily_stats AS
SELECT 
    DATE(record_date) as record_date,
    COUNT(*) as total_records,
    SUM(CASE WHEN results = 'sick' THEN 1 ELSE 0 END) as sick_count,
    SUM(CASE WHEN results = 'recovering' THEN 1 ELSE 0 END) as recovering_count,
    SUM(CASE WHEN results = 'monitoring' THEN 1 ELSE 0 END) as monitoring_count,
    SUM(CASE WHEN results = 'healed' THEN 1 ELSE 0 END) as healed_count
FROM health
WHERE record_date >= date('now', '-30 days')
GROUP BY DATE(record_date)
ORDER BY record_date DESC;

-- View: สรุปข้อมูลฟาร์มรายเดือน
CREATE VIEW IF NOT EXISTS v_monthly_farm_summary AS
SELECT 
    strftime('%Y-%m', breeding_date) as month,
    COUNT(DISTINCT b.breeding_id) as total_breedings,
    SUM(CASE WHEN b.breeding_status = 'success' THEN 1 ELSE 0 END) as successful_breedings,
    SUM(CASE WHEN b.breeding_status = 'success' THEN b.total_pups ELSE 0 END) as total_pups_born,
    SUM(CASE WHEN b.breeding_status = 'success' THEN b.albino_pups ELSE 0 END) as total_albino_pups,
    COUNT(DISTINCT h.health_id) as health_records,
    SUM(CASE WHEN h.results = 'sick' THEN 1 ELSE 0 END) as sick_records
FROM breeding b
LEFT JOIN health h ON DATE(b.breeding_date) = DATE(h.record_date)
WHERE b.breeding_date >= date('now', '-12 months')
GROUP BY strftime('%Y-%m', breeding_date)
ORDER BY month DESC;

-- =================================================================
-- INITIAL DATA
-- =================================================================

-- เพิ่มการตั้งค่าเริ่มต้น
INSERT OR IGNORE INTO report_settings (setting_name, setting_value, description) VALUES
('cache_duration_hours', '24', 'ระยะเวลาแคชรายงาน (ชั่วโมง)'),
('max_chart_points', '50', 'จำนวนจุดข้อมูลสูงสุดในกราฟ'),
('default_period', '1M', 'ช่วงเวลาเริ่มต้นสำหรับรายงาน'),
('enable_auto_refresh', 'true', 'เปิดใช้การรีเฟรชอัตโนมัติ'),
('refresh_interval_minutes', '30', 'ช่วงเวลารีเฟรชอัตโนมัติ (นาที)');

-- เพิ่มข้อมูลตัวอย่างแคช (จะถูกลบเมื่อหมดอายุ)
INSERT OR IGNORE INTO report_cache (report_type, period_type, cache_data, expires_at) VALUES
('breeding_performance', '1M', '{"success_rate": 0, "avg_pups": 0, "total_breedings": 0}', datetime('now', '+24 hours')),
('health_statistics', '1M', '{"healthy_rate": 100, "sick_rate": 0, "total_rats": 0}', datetime('now', '+24 hours'));

-- =================================================================
-- STORED PROCEDURES (Function-like views)
-- =================================================================

-- View: คำนวณอัตราเลือดชิดเฉลี่ย
CREATE VIEW IF NOT EXISTS v_avg_inbreeding_rate AS
SELECT 
    AVG(inbreeding_rate) as avg_inbreeding_rate,
    MIN(inbreeding_rate) as min_inbreeding_rate,
    MAX(inbreeding_rate) as max_inbreeding_rate,
    COUNT(*) as total_breedings
FROM breeding
WHERE breeding_status = 'success' 
AND breeding_date >= date('now', '-12 months');

-- View: ประสิทธิภาพการใช้ทรัพยากร
CREATE VIEW IF NOT EXISTS v_resource_efficiency AS
SELECT 
    (SELECT COUNT(*) FROM pond WHERE status = 'work') as ponds_in_use,
    (SELECT COUNT(*) FROM pond) as total_ponds,
    ROUND(
        CAST((SELECT COUNT(*) FROM pond WHERE status = 'work') AS REAL) / 
        (SELECT COUNT(*) FROM pond) * 100, 2
    ) as pond_usage_rate,
    (SELECT COUNT(*) FROM rat WHERE has_ring = 1) as rings_in_use,
    (SELECT SUM(ring_amount) FROM farm) as total_rings,
    ROUND(
        CAST((SELECT COUNT(*) FROM rat WHERE has_ring = 1) AS REAL) / 
        (SELECT SUM(ring_amount) FROM farm) * 100, 2
    ) as ring_usage_rate;

-- =================================================================
-- MAINTENANCE PROCEDURES
-- =================================================================

-- การทำความสะอาดข้อมูลเก่า (ควรรันเป็นระยะ)
-- DELETE FROM report_cache WHERE expires_at < datetime('now');
-- DELETE FROM report_history WHERE generated_at < datetime('now', '-30 days');

PRAGMA optimize;