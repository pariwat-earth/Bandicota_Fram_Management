import sqlite3
from main_calculate.tabular_mathod import get_pedigree_data, is_closely_related, tabular_method
from storages.database_service import get_connection

def get_pair_breeding_by_basic_data():
    """
    ฟังก์ชันหาคู่ผสมทั้งหมดที่เป็นไปได้ตามเกณฑ์พื้นฐาน
    
    Returns:
        dict: {
            'same_farm': [คู่ผสมในฟาร์มเดียวกัน],
            'different_farm': [คู่ผสมต่างฟาร์ม]
        }
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. หาคู่ที่มีปัญหา
        cursor.execute("""
            SELECT father_id, mother_id 
            FROM breeding 
            WHERE breeding_status = 'unsuccess'
            OR breeding_status = 'disorders'
            OR albino_pups > 0
        """)
        problematic_pairs = set((row[0], row[1]) for row in cursor.fetchall())
        
        # 2. หาพี่น้องของลูกเผือก (แก้ไขแล้ว)
        cursor.execute("""
            WITH albino_offspring AS (
                SELECT DISTINCT r.rat_id
                FROM rat r
                JOIN breeding b ON (r.father_id = b.father_id AND r.mother_id = b.mother_id)
                WHERE b.albino_pups > 0
            ),
            problematic_siblings AS (
                SELECT DISTINCT r1.rat_id as sibling1, r2.rat_id as sibling2
                FROM rat r1
                JOIN rat r2 ON (
                    (r1.father_id = r2.father_id AND r1.father_id IS NOT NULL)
                    OR (r1.mother_id = r2.mother_id AND r1.mother_id IS NOT NULL)
                )
                WHERE r1.rat_id != r2.rat_id
                AND (r1.rat_id IN (SELECT rat_id FROM albino_offspring)
                     OR r2.rat_id IN (SELECT rat_id FROM albino_offspring))
            )
            SELECT sibling1, sibling2 FROM problematic_siblings
        """)
        problematic_siblings = set((row[0], row[1]) for row in cursor.fetchall())

        # 3. หาหนูที่ผ่านเกณฑ์พื้นฐาน - แก้ไขให้ไม่รวมหนูที่ตายแล้ว
        cursor.execute("""
            SELECT r.rat_id, r.gender, r.birth_date, r.weight, r.size,
                   f.farm_id, f.farm_name, r.ring_number,
                   CAST(JULIANDAY('now') - JULIANDAY(r.birth_date) AS INTEGER) as age_days
            FROM rat r
            JOIN farm f ON r.farm_id = f.farm_id
            WHERE r.status = 'breeder2'
            -- ไม่รวมหนูที่ตายแล้ว
            AND r.rat_id NOT IN (
                SELECT DISTINCT h1.rat_id
                FROM health h1
                WHERE h1.results = 'dead'
            )
            -- ไม่รวมหนูที่ป่วยอยู่
            AND r.rat_id NOT IN (
                SELECT DISTINCT h2.rat_id
                FROM health h2
                WHERE h2.health_id = (
                    SELECT MAX(h3.health_id) 
                    FROM health h3 
                    WHERE h3.rat_id = h2.rat_id
                )
                AND h2.results IN ('sick', 'recovering', 'monitoring')
            )
            AND CAST(JULIANDAY('now') - JULIANDAY(r.birth_date) AS INTEGER) 
                BETWEEN 90 AND 365
            AND r.rat_id NOT IN (
                SELECT rat_id FROM (
                    SELECT father_id as rat_id
                    FROM breeding
                    WHERE breeding_status = 'success'
                    GROUP BY father_id
                    HAVING COUNT(*) > 6
                    UNION
                    SELECT mother_id
                    FROM breeding
                    WHERE breeding_status = 'success'
                    GROUP BY mother_id
                    HAVING COUNT(*) > 6
                )
            )
            AND r.rat_id NOT IN (
                SELECT rat_id FROM (
                    SELECT father_id as rat_id
                    FROM breeding
                    WHERE breeding_status = 'unsuccess'
                    GROUP BY father_id
                    HAVING COUNT(*) > 5
                    UNION
                    SELECT mother_id
                    FROM breeding
                    WHERE breeding_status = 'unsuccess'
                    GROUP BY mother_id
                    HAVING COUNT(*) > 5
                )
            )
        """)
        
        available_rats = cursor.fetchall()
        males = [r for r in available_rats if r[1] == 'male']
        females = [r for r in available_rats if r[1] == 'female']

        # 4. จับคู่และตรวจสอบเงื่อนไข
        possible_pairs = []
        for male in males:
            male_id = male[0]
            male_size = male[4] if male[4] is not None else 0
            male_ring_number = male[7]
            male_weight = male[3] if male[3] is not None else 0
            male_farm = {'id': male[5], 'name': male[6]}

            for female in females:
                female_id = female[0]
                female_ring_number = female[7]  
                female_size = female[4] if female[4] is not None else 0
                female_weight = female[3] if female[3] is not None else 0
                female_farm = {'id': female[5], 'name': female[6]}

                # ตรวจสอบคู่ที่มีปัญหา
                if (male_id, female_id) in problematic_pairs:
                    continue
                    
                # ตรวจสอบพี่น้องที่มีปัญหา
                if (male_id, female_id) in problematic_siblings or (female_id, male_id) in problematic_siblings:
                    continue

                # ตรวจสอบขนาด (แก้ไขแล้ว)
                if female_size == 0:  # หลีกเลี่ยง division by zero
                    continue
                    
                size_diff_percent = ((male_size - female_size) / female_size) * 100
                if not (-40 <= size_diff_percent <= 100):  # ปรับช่วงให้สมเหตุสมผล
                    continue

                # ตรวจสอบความสัมพันธ์และเลือดชิด (แก้ไขการเรียกใช้)
                male_pedigree = get_pedigree_data(male_id, cursor, generation=5)
                female_pedigree = get_pedigree_data(female_id, cursor, generation=5)
                
                # แก้ไขการเรียกใช้ is_closely_related
                if is_closely_related(male_id, female_id, male_pedigree, female_pedigree, max_gen=3):
                    continue

                combined_pedigree = {**male_pedigree, **female_pedigree}
                R, F = tabular_method(combined_pedigree)
                inbreeding_coef = 0.5 * R.get((male_id, female_id), 0)
                
                if inbreeding_coef > 0.0625:  # > 6.25%
                    continue

                # คู่ที่ผ่านเกณฑ์ทั้งหมด
                pair_info = {
                    'male': {
                        'id': male_id,
                        'ring_number': male_ring_number,
                        'size': male_size,
                        'weight': male_weight,
                        'farm': male_farm
                    },
                    'female': {
                        'id': female_id,
                        'ring_number': female_ring_number,
                        'size': female_size,
                        'weight': female_weight,
                        'farm': female_farm
                    },
                    'inbreeding_coef': inbreeding_coef,
                    'size_diff_percent': size_diff_percent
                }
                
                possible_pairs.append(pair_info)

        # 5. แยกและจัดเรียงคู่ผสม
        same_farm_pairs = [p for p in possible_pairs 
                          if p['male']['farm']['id'] == p['female']['farm']['id']]
        diff_farm_pairs = [p for p in possible_pairs 
                          if p['male']['farm']['id'] != p['female']['farm']['id']]
        
        return {
            'same_farm': same_farm_pairs,
            'different_farm': diff_farm_pairs
        }

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None
        
    finally:
        conn.close()

def get_health_summary(cursor, rat_id):
    """
    ดึงสรุปประวัติสุขภาพของหนู
    
    Returns:
        tuple: (died, total_illness_count, healed_count, illness_before_death)
    """
    cursor.execute("""
        WITH health_records AS (
            SELECT 
                results,
                record_date,
                ROW_NUMBER() OVER (ORDER BY record_date ASC) as seq
            FROM health
            WHERE rat_id = ?
            ORDER BY record_date ASC
        )
        SELECT 
            -- ตรวจว่าตายหรือไม่
            MAX(CASE WHEN results = 'dead' THEN 1 ELSE 0 END) as died,
            -- นับจำนวนครั้งที่ป่วย (sick, recovering, monitoring)
            SUM(CASE WHEN results IN ('sick', 'recovering', 'monitoring') THEN 1 ELSE 0 END) as total_illness,
            -- นับจำนวนครั้งที่หาย
            SUM(CASE WHEN results = 'healed' THEN 1 ELSE 0 END) as healed_count,
            -- นับจำนวนครั้งที่ป่วยก่อนตาย (ถ้าตาย)
            CASE 
                WHEN MAX(CASE WHEN results = 'dead' THEN 1 ELSE 0 END) = 1
                THEN SUM(CASE 
                    WHEN results IN ('sick', 'recovering', 'monitoring') 
                    AND seq < (SELECT MAX(seq) FROM health_records WHERE results = 'dead')
                    THEN 1 ELSE 0 
                END) + 1  -- +1 เพราะครั้งสุดท้ายที่ตายก็นับว่าป่วยด้วย
                ELSE 0
            END as illness_before_death
        FROM health_records
    """, (rat_id,))
    
    result = cursor.fetchone()
    if result and any(result):  # ถ้ามีข้อมูล
        return result
    else:
        return (0, 0, 0, 0)  # ไม่มีประวัติป่วย

def calculate_ancestor_health_score(cursor, male_id, female_id, max_generations=5):
    """
    คำนวณคะแนนสุขภาพจากประวัติการเจ็บป่วยของบรรพบุรุษ (ใช้วิธีใหม่)
    """
    def get_ancestor_health_score(rat_id):
        visited = set()
        queue = [(rat_id, 0)]
        scores = []
        health_details = []
        
        while queue:
            current_id, generation = queue.pop(0)
            
            if current_id in visited or generation >= max_generations:
                continue
                
            visited.add(current_id)
            
            # ดึงข้อมูลสุขภาพ
            died, total_illness, healed_count, illness_before_death = get_health_summary(cursor, current_id)
            
            # คำนวณคะแนน
            if died:
                # ตายจากการป่วย: คะแนนต่ำตามจำนวนครั้งที่ป่วย
                if illness_before_death == 1:
                    score = 20  # ป่วยครั้งเดียวตาย = อ่อนแอมาก
                elif illness_before_death <= 3:
                    score = 10  # ป่วย 2-3 ครั้งตาย = อ่อนแอ
                else:
                    score = 5   # ป่วยหลายครั้งตาย = พยายามรักษาแล้ว
            else:
                # ไม่ตาย: คะแนนตามจำนวนครั้งที่ป่วย
                base_score = max(0, 100 - (total_illness * 10))
                # โบนัสถ้าหายหลายครั้ง (แสดงว่าฟื้นตัวเร็ว)
                bonus = min(20, healed_count * 5)  # โบนัสสูงสุด 20
                score = min(100, base_score + bonus)
            
            scores.append(score)
            health_details.append({
                'rat_id': current_id,
                'died': died,
                'total_illness': total_illness,
                'healed_count': healed_count,
                'illness_before_death': illness_before_death,
                'score': score
            })
            
            # ดึงข้อมูลพ่อแม่
            cursor.execute("""
                SELECT father_id, mother_id
                FROM rat
                WHERE rat_id = ?
            """, (current_id,))
            
            result = cursor.fetchone()
            if result:
                father_id, mother_id = result
                if father_id and father_id not in visited:
                    queue.append((father_id, generation + 1))
                if mother_id and mother_id not in visited:
                    queue.append((mother_id, generation + 1))
        
        avg_score = sum(scores) / len(scores) if scores else 100  # ถ้าไม่มีประวัติ = 100
        return avg_score, health_details

    # คำนวณคะแนนสุขภาพของแต่ละสายพันธุ์
    male_score, male_details = get_ancestor_health_score(male_id)
    female_score, female_details = get_ancestor_health_score(female_id)

    # คำนวณคะแนนเฉลี่ยของคู่
    pair_score = (male_score + female_score) / 2

    return pair_score

def calculate_ancestor_size_score(cursor, male_id, female_id, max_generations=5):
    """
    คำนวณคะแนนน้ำหนักเฉลี่ยของบรรพบุรุษแยกระหว่างตัวผู้และตัวเมีย (แก้ไขแล้ว)
    """
    def get_ancestor_weights(rat_id):
        # ใช้ breadth-first search แทน recursive CTE เพื่อหลีกเลี่ยงปัญหา
        visited = set()
        queue = [(rat_id, 0)]
        weights = []
        
        while queue:
            current_id, generation = queue.pop(0)
            
            if current_id in visited or generation >= max_generations:
                continue
                
            visited.add(current_id)
            
            # ดึงข้อมูลน้ำหนักและพ่อแม่
            cursor.execute("""
                SELECT weight, father_id, mother_id
                FROM rat
                WHERE rat_id = ?
            """, (current_id,))
            
            result = cursor.fetchone()
            if result:
                weight, father_id, mother_id = result
                if weight is not None:
                    weights.append(weight)
                
                # เพิ่มพ่อแม่เข้า queue
                if father_id is not None and father_id not in visited:
                    queue.append((father_id, generation + 1))
                if mother_id is not None and mother_id not in visited:
                    queue.append((mother_id, generation + 1))
        
        return sum(weights) / len(weights) if weights else 0

    # คำนวณน้ำหนักเฉลี่ยแยกสำหรับแต่ละตัว
    male_avg_weight = get_ancestor_weights(male_id)
    female_avg_weight = get_ancestor_weights(female_id)

    # คำนวณคะแนน (เต็ม 100 เมื่อน้ำหนักเฉลี่ยมากกว่าหรือเท่ากับ 1,000 กรัม)
    def weight_to_score(weight):
        return min(100, max(0, (weight / 1000) * 100))

    male_score = weight_to_score(male_avg_weight)
    female_score = weight_to_score(female_avg_weight)

    # คำนวณคะแนนเฉลี่ยของคู่
    pair_score = (male_score + female_score) / 2

    return pair_score

def calculate_ancestor_breeding_score(cursor, male_id, female_id, max_generations=5):
    """
    คำนวณคะแนนประสิทธิภาพการผสมพันธุ์จากจำนวนลูกต่อคอกเฉลี่ยของบรรพบุรุษ (แก้ไขแล้ว)
    """
    def get_ancestor_breeding_data(rat_id):
        # ใช้ breadth-first search
        visited = set()
        queue = [(rat_id, 0)]
        breeding_data = []
        
        while queue:
            current_id, generation = queue.pop(0)
            
            if current_id in visited or generation >= max_generations:
                continue
                
            visited.add(current_id)
            
            # ดึงข้อมูลการผสมและพ่อแม่
            cursor.execute("""
                SELECT DISTINCT b.survived_pups, r.father_id, r.mother_id
                FROM rat r
                LEFT JOIN breeding b ON (b.father_id = r.rat_id OR b.mother_id = r.rat_id)
                    AND b.breeding_status = 'success'
                WHERE r.rat_id = ?
            """, (current_id,))
            
            results = cursor.fetchall()
            for result in results:
                survived_pups, father_id, mother_id = result
                if survived_pups is not None:
                    breeding_data.append(survived_pups)
                
                # เพิ่มพ่อแม่เข้า queue (เฉพาะแถวแรก)
                if generation == 0:  # เพื่อไม่ให้เพิ่ม parent หลายครั้ง
                    if father_id is not None and father_id not in visited:
                        queue.append((father_id, generation + 1))
                    if mother_id is not None and mother_id not in visited:
                        queue.append((mother_id, generation + 1))
        
        return sum(breeding_data) / len(breeding_data) if breeding_data else 0

    # คำนวณจำนวนลูกเฉลี่ยของแต่ละสายพันธุ์
    male_avg_pups = get_ancestor_breeding_data(male_id)
    female_avg_pups = get_ancestor_breeding_data(female_id)

    # คำนวณคะแนน (เต็ม 100 เมื่อมีลูกเฉลี่ยมากกว่าหรือเท่ากับ 10 ตัวต่อคอก)
    def pups_to_score(avg_pups):
        return min(100, max(0, (avg_pups / 10) * 100))

    male_score = pups_to_score(male_avg_pups)
    female_score = pups_to_score(female_avg_pups)

    # คำนวณคะแนนเฉลี่ยของคู่
    pair_score = (male_score + female_score) / 2

    return pair_score

def calculate_lineage_strength_score(cursor, male_id, female_id, max_generations=5):
    """
    คำนวณคะแนนความแข็งแกร่งของสายพันธุ์ (ปรับปรุงให้พิจารณาหลายมิติ)
    """
    def get_lineage_data(rat_id):
        # ใช้ breadth-first search
        visited = set()
        queue = [(rat_id, 0)]
        breeding_data = []
        
        while queue:
            current_id, generation = queue.pop(0)
            
            if current_id in visited or generation >= max_generations:
                continue
                
            visited.add(current_id)
            
            # ดึงข้อมูลการผสมพันธุ์โดยละเอียด
            cursor.execute("""
                SELECT 
                    r.father_id,
                    r.mother_id,
                    -- ข้อมูลการผสมพันธุ์
                    (
                        SELECT COUNT(DISTINCT b.breeding_id)
                        FROM breeding b
                        WHERE (b.father_id = r.rat_id OR b.mother_id = r.rat_id)
                        AND b.breeding_status = 'success'
                    ) as breeding_count,
                    -- จำนวนลูกเกิดทั้งหมด
                    COALESCE((
                        SELECT SUM(b.total_pups)
                        FROM breeding b
                        WHERE (b.father_id = r.rat_id OR b.mother_id = r.rat_id)
                        AND b.breeding_status = 'success'
                    ), 0) as total_born,
                    -- จำนวนลูกรอดทั้งหมด
                    COALESCE((
                        SELECT SUM(b.survived_pups)
                        FROM breeding b
                        WHERE (b.father_id = r.rat_id OR b.mother_id = r.rat_id)
                        AND b.breeding_status = 'success'
                    ), 0) as total_survived,
                    -- จำนวนครั้งที่ลูกตายหมด
                    (
                        SELECT COUNT(*)
                        FROM breeding b
                        WHERE (b.father_id = r.rat_id OR b.mother_id = r.rat_id)
                        AND b.breeding_status = 'success'
                        AND b.survived_pups = 0
                    ) as failed_breedings,
                    -- จำนวนลูกที่เป็น breeder
                    (
                        SELECT COUNT(DISTINCT offspring.rat_id)
                        FROM rat offspring
                        WHERE (offspring.father_id = r.rat_id OR offspring.mother_id = r.rat_id)
                        AND offspring.status IN ('breeder1', 'breeder2')
                    ) as breeder_offspring
                FROM rat r
                WHERE r.rat_id = ?
            """, (current_id,))
            
            result = cursor.fetchone()
            if result:
                father_id, mother_id, breeding_count, total_born, total_survived, failed_breedings, breeder_offspring = result
                
                if breeding_count > 0 and total_born > 0:
                    # คำนวณคะแนนหลายมิติ
                    # 1. อัตราการรอดโดยรวม (30%)
                    survival_rate = total_survived / total_born
                    
                    # 2. ความสม่ำเสมอ (30%) - พิจารณาจากอัตราการล้มเหลว
                    consistency_score = 1 - (failed_breedings / breeding_count)
                    
                    # 3. คุณภาพลูก (25%) - ดูจากอัตราการเป็น breeder
                    breeder_rate = breeder_offspring / total_survived if total_survived > 0 else 0
                    
                    # 4. ประสิทธิภาพการผสม (15%) - ดูจากจำนวนลูกเฉลี่ยต่อครั้ง
                    avg_pups_per_breeding = total_survived / breeding_count
                    efficiency_score = min(1.0, avg_pups_per_breeding / 10)  # สมมติว่า 10 ตัว/ครั้ง = เต็ม
                    
                    # คะแนนรวม
                    score = (
                        survival_rate * 0.30 +
                        consistency_score * 0.30 +
                        breeder_rate * 0.25 +
                        efficiency_score * 0.15
                    ) * 100
                    
                    breeding_data.append({
                        'rat_id': current_id,
                        'score': score,
                        'breeding_count': breeding_count,
                        'survival_rate': survival_rate,
                        'consistency_score': consistency_score
                    })
                
                # เพิ่มพ่อแม่เข้า queue
                if father_id and father_id not in visited:
                    queue.append((father_id, generation + 1))
                if mother_id and mother_id not in visited:
                    queue.append((mother_id, generation + 1))
        
        # คำนวณคะแนนเฉลี่ยจากบรรพบุรุษ
        if breeding_data:
            avg_score = sum(d['score'] for d in breeding_data) / len(breeding_data)
        else:
            avg_score = 50  # ไม่มีข้อมูล = คะแนนกลาง
            
        return avg_score

    # ดึงข้อมูลของแต่ละสายพันธุ์
    male_score = get_lineage_data(male_id)
    female_score = get_lineage_data(female_id)

    # คำนวณคะแนนเฉลี่ยของคู่
    pair_score = (male_score + female_score) / 2

    return pair_score

def get_best_pair_breeding_per_pound(factor_weights=None):
    """
    คัดเลือกคู่ผสมที่ดีที่สุดตาม 4 เกณฑ์จากคู่ผสมที่เป็นไปได้ทั้งหมด (เพิ่ม error handling)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. หาจำนวนบ่อว่าง
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pond 
            WHERE status = 'empty'
        """)
        num_empty_ponds = cursor.fetchone()[0]
        
        if num_empty_ponds == 0:
            return {
                'num_empty_ponds': 0,
                'selected_pairs': [],
                'weights_used': factor_weights,
                'message': 'ไม่มีบ่อว่างสำหรับการผสมพันธุ์'
            }

        # 2. หาคู่ผสมที่เป็นไปได้ทั้งหมด
        all_possible_pairs = get_pair_breeding_by_basic_data()
        if not all_possible_pairs or (not all_possible_pairs['same_farm'] and not all_possible_pairs['different_farm']):
            return {
                'num_empty_ponds': num_empty_ponds,
                'selected_pairs': [],
                'weights_used': factor_weights,
                'message': 'ไม่พบคู่ผสมที่เหมาะสม'
            }

        # 3. คำนวณคะแนนและจัดอันดับ
        scored_pairs = []
        weights = factor_weights or {'size': 25, 'breeding': 25, 'health': 25, 'lineage': 25}
        
        for farm_type in ['same_farm', 'different_farm']:
            for pair in all_possible_pairs[farm_type]:
                try:
                    male_id = pair['male']['id']
                    female_id = pair['female']['id']
                    
                    # คำนวณคะแนนแต่ละด้าน
                    size_score = calculate_ancestor_size_score(cursor, male_id, female_id)
                    breeding_score = calculate_ancestor_breeding_score(cursor, male_id, female_id)
                    health_score = calculate_ancestor_health_score(cursor, male_id, female_id)
                    lineage_score = calculate_lineage_strength_score(cursor, male_id, female_id)
                    
                    # คำนวณคะแนนรวม
                    total_score = (
                        (size_score * weights['size'] / 100) +
                        (breeding_score * weights['breeding'] / 100) +
                        (health_score * weights['health'] / 100) +
                        (lineage_score * weights['lineage'] / 100)
                    )
                    
                    scored_pair = {
                        'pair_info': pair,
                        'total_score': round(total_score, 2),
                        'scores': {
                            'size': round(size_score, 2),
                            'breeding': round(breeding_score, 2),
                            'health': round(health_score, 2),
                            'lineage': round(lineage_score, 2)
                        },
                        'farm_type': farm_type
                    }
                    scored_pairs.append(scored_pair)
                    
                except Exception as e:
                    print(f"Error calculating scores for pair {male_id}-{female_id}: {e}")
                    continue
        
        if not scored_pairs:
            return {
                'num_empty_ponds': num_empty_ponds,
                'selected_pairs': [],
                'weights_used': weights,
                'message': 'ไม่สามารถคำนวณคะแนนคู่ผสมได้'
            }
        
        # 4. จัดเรียงและเลือกคู่ที่ดีที่สุด
        scored_pairs.sort(key=lambda x: (
            -x['total_score'],  # เรียงคะแนนจากมากไปน้อย
            -(x['pair_info']['male']['size'] + x['pair_info']['female']['size'])  # ถ้าคะแนนเท่ากัน ใช้ขนาดรวม
        ))
        
        selected_pairs = scored_pairs[:num_empty_ponds]
        
        return {
            'num_empty_ponds': num_empty_ponds,
            'selected_pairs': selected_pairs,
            'weights_used': weights,
            'total_possible_pairs': len(scored_pairs),
            'message': f'เลือกคู่ผสมได้ {len(selected_pairs)} คู่จาก {len(scored_pairs)} คู่ที่เป็นไปได้'
        }
        
    except Exception as e:
        return {
            'error': f'เกิดข้อผิดพลาด: {str(e)}',
            'num_empty_ponds': 0,
            'selected_pairs': [],
            'weights_used': factor_weights
        }
        
    finally:
        conn.close()

def calculate_inbreeding_coefficient(male_id, female_id):
    """
    คำนวณอัตราเลือดชิดของลูกที่จะเกิดจากคู่ผสม
    
    Args:
        male_id: รหัสหนูตัวผู้
        female_id: รหัสหนูตัวเมีย
    
    Returns:
        float: ค่า inbreeding coefficient (0.0 - 1.0)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. ดึงข้อมูล pedigree ของทั้งสองตัว
        male_pedigree = get_pedigree_data(male_id, cursor, generation=5)
        female_pedigree = get_pedigree_data(female_id, cursor, generation=5)
        
        # 2. รวม pedigree ทั้งสอง
        combined_pedigree = {**male_pedigree, **female_pedigree}
        
        # 3. คำนวณค่า relationship matrix
        R, F = tabular_method(combined_pedigree)
        
        # 4. คำนวณ inbreeding coefficient ของลูก
        inbreeding_coef = 0.5 * R.get((male_id, female_id), 0)
        
        return inbreeding_coef
        
    finally:
        conn.close()