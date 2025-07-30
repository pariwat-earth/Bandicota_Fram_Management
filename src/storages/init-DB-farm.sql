-- Drop Database IF EXISTS bendicota_DB_farm;
-- CREATE Database bendicota_DB_farm;
-- USE bendicota_DB_farm;

-- =================================================================
-- Farm Management Database Schema
-- =================================================================

-- Drop all tables in reverse dependency order
DROP TABLE IF EXISTS missing_rings;
DROP TABLE IF EXISTS import_history;
DROP TABLE IF EXISTS export_history;
DROP TABLE IF EXISTS health;
DROP TABLE IF EXISTS breeding;
DROP TABLE IF EXISTS rat;
DROP TABLE IF EXISTS pond;
DROP TABLE IF EXISTS hmt_page;
DROP TABLE IF EXISTS farm;

-- =================================================================
-- MAIN TABLES
-- =================================================================

-- Table: farm (ฟาร์ม)
CREATE TABLE farm (
    farm_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    farm_name    VARCHAR(100) UNIQUE NOT NULL,
    location     TEXT,
    latitude     TEXT,
    longtitude   TEXT,
    ponds_amount INTEGER DEFAULT 50,
    ring_amount  INTEGER DEFAULT 100,
    manager_name VARCHAR(100) NOT NULL,
    start_date   DATE NOT NULL,
    farm_type    TEXT NOT NULL CHECK (farm_type IN ('main', 'member'))
);

-- Table: pond (บ่อ)
CREATE TABLE pond (
    pond_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    pond_index  INTEGER,
    farm_id     INTEGER,
    pond_name   TEXT,
    status      TEXT CHECK (status IN ('empty', 'work', 'maintenance')),
    update_date DATE,
    FOREIGN KEY (farm_id) REFERENCES farm (farm_id)
    -- Status values:
    -- empty: ว่าง
    -- work: ใช้งาน
    -- maintenance: ซ่อมบำรุง
);

-- Table: hmt_page (หน้าเว็บ)
CREATE TABLE hmt_page (
    page_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    page_current_name TEXT
);

-- Table: rat (หนู)
CREATE TABLE rat (
    rat_id         VARCHAR(15) PRIMARY KEY,
    father_id      VARCHAR(15),
    mother_id      VARCHAR(15),
    birth_date     DATE,
    gender         TEXT CHECK (gender IN ('male', 'female')),
    weight         DECIMAL(5, 2),
    size           DECIMAL(5, 2),
    breed          VARCHAR(50),
    status         TEXT CHECK (status IN ('breeder1', 'breeder2', 'fertilize', 'dispose')),
    pond_id        INTEGER,
    farm_id        INTEGER,
    has_ring       INTEGER CHECK (has_ring IN (0, 1)),
    ring_number    INTEGER UNIQUE,
    special_traits TEXT,
    FOREIGN KEY (father_id) REFERENCES rat (rat_id),
    FOREIGN KEY (mother_id) REFERENCES rat (rat_id),
    FOREIGN KEY (pond_id) REFERENCES pond (pond_id),
    FOREIGN KEY (farm_id) REFERENCES farm (farm_id),
    UNIQUE (farm_id, ring_number)
    -- Gender values:
    -- male: ผู้
    -- female: เมีย
    -- Status values:
    -- breeder1: กำลังผสม
    -- breeder2: พร้อมผสม
    -- fertilize: ขุน
    -- dispose: จำหน่าย
);

-- =================================================================
-- TRANSACTION TABLES
-- =================================================================

-- Table: breeding (การผสมพันธุ์)
CREATE TABLE breeding (
    breeding_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    father_id       VARCHAR(15),
    mother_id       VARCHAR(15),
    breeding_date   DATE,
    pond_id         INTEGER NOT NULL,
    birth_date      DATE,
    total_pups      INTEGER CHECK (total_pups >= 0),
    survived_pups   INTEGER CHECK (survived_pups >= 0),
    inbreeding_rate DECIMAL(5, 2) CHECK (inbreeding_rate >= 0),
    albino_pups     INTEGER CHECK (albino_pups >= 0),
    breeding_status TEXT CHECK (breeding_status IN ('breeding', 'success', 'unsuccess', 'disorders')),
    separation_date DATE,
    FOREIGN KEY (father_id) REFERENCES rat (rat_id),
    FOREIGN KEY (mother_id) REFERENCES rat (rat_id),
    FOREIGN KEY (pond_id) REFERENCES pond (pond_id)
    -- Status values:
    -- breeding: กำลังผสมพันธุ์
    -- success: สำเร็จ
    -- unsuccess: ล้มเหลว
    -- disorders: ผสมแล้วได้หนูเผือก
);

-- Table: health (สุขภาพ)
CREATE TABLE health (
    health_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    rat_id      VARCHAR(15),
    record_date DATE,
    symptoms    TEXT,
    treatment   TEXT,
    treated_by  VARCHAR(100),
    results     TEXT CHECK (results IN ('sick', 'recovering', 'monitoring', 'healed', 'dead')),
    FOREIGN KEY (rat_id) REFERENCES rat (rat_id)
);

-- =================================================================
-- HISTORY AND UTILITY TABLES
-- =================================================================
-- อัพเดทตาราง export_history ให้มี export_id
DROP TABLE IF EXISTS export_history;
CREATE TABLE export_history (
    export_id   VARCHAR(20) PRIMARY KEY,
    export_date DATETIME,
    file_name   VARCHAR(100),
    file_type   TEXT CHECK (file_type IN ('CSV', 'Backup')),
    status      TEXT CHECK (status IN ('success', 'unsuccess')),
    note        TEXT
);

-- อัพเดทตาราง import_history ให้มี import_id
DROP TABLE IF EXISTS import_history;
CREATE TABLE import_history (
    import_id     VARCHAR(20) PRIMARY KEY,
    import_date   DATETIME,
    file_name     VARCHAR(100),
    status        TEXT CHECK (status IN ('success', 'unsuccess')),
    error_message TEXT
);

-- Table: missing_rings (ห่วงขาที่หาย)
CREATE TABLE missing_rings (
    ring_number INTEGER PRIMARY KEY,
    lost_date   DATE DEFAULT CURRENT_DATE NOT NULL,
    note        TEXT
);

-- =================================================================
-- INDEXES
-- =================================================================

CREATE INDEX IF NOT EXISTS idx_missing_rings_number ON missing_rings (ring_number);
CREATE INDEX IF NOT EXISTS idx_rat_status ON rat (status);
CREATE INDEX IF NOT EXISTS idx_rat_farm ON rat (farm_id);
CREATE INDEX IF NOT EXISTS idx_breeding_status ON breeding (breeding_status);
CREATE INDEX IF NOT EXISTS idx_health_rat ON health (rat_id);
CREATE INDEX IF NOT EXISTS idx_health_results ON health (results);
CREATE INDEX IF NOT EXISTS idx_health_date ON health (record_date);
CREATE INDEX IF NOT EXISTS idx_export_date ON export_history (export_date);
CREATE INDEX IF NOT EXISTS idx_import_date ON import_history (import_date);

-- =================================================================
-- TRIGGERS
-- =================================================================

-- Trigger: ตรวจสอบจำนวนลูกหนู
CREATE TRIGGER check_pups_count
    BEFORE UPDATE ON breeding
    FOR EACH ROW
    WHEN NEW.survived_pups > NEW.total_pups OR NEW.albino_pups > NEW.survived_pups
BEGIN
    SELECT RAISE(ROLLBACK, 'จำนวนลูกหนูไม่ถูกต้อง');
END;