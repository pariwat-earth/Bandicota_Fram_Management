-- Script ปรับข้อมูลเพื่อรองรับหนูนำเข้าใหม่และทำให้จับคู่ได้

-- 1. ยกเลิกการทำให้หนูทั้งฟาร์มเป็นพี่น้องกัน (Rollback)
-- คืนค่า father_id และ mother_id กลับเป็นค่าเดิม

-- รุ่นที่ -2 (คืนค่าให้มาจากคู่ต่างกัน)
UPDATE rat SET father_id = '202409010001', mother_id = '202409010002' WHERE rat_id = '202411010001';
UPDATE rat SET father_id = '202409010003', mother_id = '202409010004' WHERE rat_id = '202411010002';
UPDATE rat SET father_id = '202409010005', mother_id = '202409010006' WHERE rat_id = '202411010003';
UPDATE rat SET father_id = '202409010007', mother_id = '202409010008' WHERE rat_id = '202411010004';
UPDATE rat SET father_id = '202409010009', mother_id = '202409010010' WHERE rat_id = '202411010005';
UPDATE rat SET father_id = '202409010011', mother_id = '202409010012' WHERE rat_id = '202411010006';
UPDATE rat SET father_id = '202409010013', mother_id = '202409010014' WHERE rat_id = '202411010007';
UPDATE rat SET father_id = '202409010015', mother_id = '202409010016' WHERE rat_id = '202411010008';

-- รุ่นที่ -1 (คืนค่าให้แต่ละคู่มีพ่อแม่ต่างกัน)
UPDATE rat SET father_id = '202411010001', mother_id = '202411010002'
WHERE rat_id IN ('202501010001', '202501010002', '202501010003', '202501010004');

UPDATE rat SET father_id = '202411010003', mother_id = '202411010004'
WHERE rat_id IN ('202501010005', '202501010006', '202501010007', '202501010008');

UPDATE rat SET father_id = '202411010005', mother_id = '202411010006'
WHERE rat_id IN ('202501010009', '202501010010', '202501010011', '202501010012');

UPDATE rat SET father_id = '202411010007', mother_id = '202411010008'
WHERE rat_id IN ('202501010013', '202501010014', '202501010015', '202501010016');

-- รุ่นที่ 0 (คืนค่าให้มาจากพ่อแม่คู่ต่างกัน)
UPDATE rat SET father_id = '202501010001', mother_id = '202501010002' WHERE rat_id = '202503010001';
UPDATE rat SET father_id = '202501010003', mother_id = '202501010004' WHERE rat_id = '202503010002';
UPDATE rat SET father_id = '202501010005', mother_id = '202501010006' WHERE rat_id = '202503010003';
UPDATE rat SET father_id = '202501010007', mother_id = '202501010008' WHERE rat_id = '202503010004';
UPDATE rat SET father_id = '202501010009', mother_id = '202501010010' WHERE rat_id = '202503010005';
UPDATE rat SET father_id = '202501010011', mother_id = '202501010012' WHERE rat_id = '202503010006';
UPDATE rat SET father_id = '202501010013', mother_id = '202501010014' WHERE rat_id = '202503010007';
UPDATE rat SET father_id = '202501010015', mother_id = '202501010016' WHERE rat_id = '202503010008';

-- F1 (คืนค่าให้มาจากการผสมจริง)
UPDATE rat SET father_id = '202503010005', mother_id = '202503010002'
WHERE rat_id BETWEEN '202507050001' AND '202507050008';

UPDATE rat SET father_id = '202503010003', mother_id = '202503010006'
WHERE rat_id BETWEEN '202507050009' AND '202507050018';

UPDATE rat SET father_id = '202503010007', mother_id = '202503010004'
WHERE rat_id BETWEEN '202507050019' AND '202507050027';


-- 3. เพิ่มประวัติการผสมของบรรพบุรุษหนูนำเข้าใหม่
INSERT INTO breeding (father_id, mother_id, breeding_date, pond_id, inbreeding_rate, breeding_status, birth_date, total_pups, survived_pups, albino_pups) VALUES
-- ปจ.005 เน้นขนาด
('202512010001', '202512010002', '2025-01-01', 9, 0, 'success', '2025-02-01', 4, 4, 0),
-- ปจ.006 เน้นจำนวนลูก
('202512010003', '202512010004', '2025-01-01', 10, 0, 'success', '2025-02-01', 12, 12, 0),
-- ปจ.007 เน้นสุขภาพ
('202512010005', '202512010006', '2025-01-01', 11, 0, 'success', '2025-02-01', 6, 6, 0),
-- ปจ.008 เน้นความแข็งแกร่ง
('202512010007', '202512010008', '2025-01-01', 12, 0, 'success', '2025-02-01', 8, 8, 0);

-- 4. การจับคู่ที่แนะนำหลังนำเข้าหนูใหม่:
-- คู่ที่ 1: หนู 97 (ปจ.005) × หนู 2 (ปจ.001) = ลูกตัวใหญ่มาก
-- คู่ที่ 2: หนู 3 (ปจ.002) × หนู 98 (ปจ.006) = ลูกเยอะมาก
-- คู่ที่ 3: หนู 99 (ปจ.007) × หนู 6 (ปจ.003) = สุขภาพดีมาก
-- คู่ที่ 4: หนู 7 (ปจ.004) × หนู 100 (ปจ.008) = แข็งแกร่งมาก