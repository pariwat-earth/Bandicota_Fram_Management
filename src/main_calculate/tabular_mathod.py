import sqlite3
from storages.database_service import get_connection


def get_pedigree_data(rat_id, cursor, generation=5):
    """
    ดึงข้อมูลพันธุ์ประวัติของหนูย้อนหลังตามจำนวน generation ที่กำหนด
    """
    pedigree = {}
    queue = [(rat_id, 0)]
    visited = set()

    while queue:
        current_id, gen = queue.pop(0)
        if current_id in visited or gen >= generation:
            continue
            
        visited.add(current_id)
        
        # ดึงข้อมูลพ่อแม่
        cursor.execute("""
            SELECT father_id, mother_id
            FROM rat
            WHERE rat_id = ?
        """, (current_id,))
        
        result = cursor.fetchone()
        if result:
            father_id, mother_id = result

            #เปลี่ยนค่า NULL เป็น '0' เมื่อนำมาคำนวณ
            pedigree[current_id] = {
                'father': '0' if father_id is None else father_id,
                'mother': '0' if mother_id is None else mother_id,
                'generation': gen  # เพิ่มข้อมูลรุ่น
            }
            
            # ถ้าพ่อแม่ไม่ใช่ NULL และไม่ใช่ '0' ให้ติดตามต่อ
            if father_id is not None:
                queue.append((father_id, gen + 1))
            if mother_id is not None:
                queue.append((mother_id, gen + 1))
        else:
            pedigree[current_id] = {
                'father': '0', 
                'mother': '0',
                'generation': gen
            }
    
    return pedigree


def tabular_method(pedigree):
    """
    คำนวณค่า inbreeding coefficient โดยใช้ tabular method (แก้ไขแล้ว)
    """
    # สร้าง list ของ ancestors ทั้งหมด และเรียงตามรุ่น (generation)
    ancestors = []
    ancestor_gen = {}
    
    for rat_id in pedigree:
        ancestors.append(rat_id)
        ancestor_gen[rat_id] = pedigree[rat_id]['generation']
        
        if pedigree[rat_id]['father'] != '0':
            father_id = pedigree[rat_id]['father']
            if father_id not in ancestor_gen:
                ancestors.append(father_id)
                ancestor_gen[father_id] = pedigree[rat_id]['generation'] + 1
                
        if pedigree[rat_id]['mother'] != '0':
            mother_id = pedigree[rat_id]['mother']
            if mother_id not in ancestor_gen:
                ancestors.append(mother_id)
                ancestor_gen[mother_id] = pedigree[rat_id]['generation'] + 1
    
    # เรียงลำดับตามรุ่น (รุ่นเก่าก่อน)
    ancestors = sorted(set(ancestors), key=lambda x: ancestor_gen.get(x, 0), reverse=True)
    
    # สร้างตาราง coefficient
    F = {}  # inbreeding coefficients
    R = {}  # relationship coefficients
    
    # คำนวณทีละตัว เริ่มจากรุ่นเก่าสุด
    for i, ancestor1 in enumerate(ancestors):
        # คำนวณ inbreeding coefficient
        if ancestor1 in pedigree:
            father = pedigree[ancestor1]['father']
            mother = pedigree[ancestor1]['mother']
            
            if father != '0' and mother != '0':
                F[ancestor1] = 0.5 * R.get((father, mother), 0)
            else:
                F[ancestor1] = 0
        else:
            F[ancestor1] = 0
        
        # คำนวณ relationship coefficient กับตัวเอง
        R[(ancestor1, ancestor1)] = 1 + F[ancestor1]
        
        # คำนวณ relationship coefficient กับ ancestors อื่น
        for j in range(i + 1, len(ancestors)):
            ancestor2 = ancestors[j]
            
            # คำนวณ relationship ระหว่าง ancestor1 และ ancestor2
            if ancestor2 in pedigree:
                father = pedigree[ancestor2]['father']
                mother = pedigree[ancestor2]['mother']
                
                if father != '0' and mother != '0':
                    r_father = R.get((ancestor1, father), 0)
                    r_mother = R.get((ancestor1, mother), 0)
                    r = 0.5 * (r_father + r_mother)
                else:
                    r = 0
            else:
                r = 0
            
            R[(ancestor1, ancestor2)] = R[(ancestor2, ancestor1)] = r
    
    return R, F


def is_closely_related(male_id, female_id, male_pedigree, female_pedigree, max_gen=3):
    """
    ตรวจสอบว่ามีความสัมพันธ์เครือญาติใกล้ชิดหรือไม่ (แก้ไขแล้ว)
    """
    # ตรวจสอบว่าเป็นตัวเดียวกันหรือไม่
    if male_id == female_id:
        return True
    
    # ตรวจสอบว่าเป็นพี่น้องหรือไม่
    if (male_id in male_pedigree and female_id in female_pedigree):
        male_parents = (male_pedigree[male_id]['father'], male_pedigree[male_id]['mother'])
        female_parents = (female_pedigree[female_id]['father'], female_pedigree[female_id]['mother'])
        
        # ถ้ามีพ่อหรือแม่เดียวกัน = พี่น้อง
        if (male_parents[0] != '0' and male_parents[0] == female_parents[0]) or \
           (male_parents[1] != '0' and male_parents[1] == female_parents[1]):
            return True
    
    # สร้าง set ของบรรพบุรุษ
    def get_ancestors(rat_id, pedigree, max_depth):
        ancestors = set()
        queue = [(rat_id, 0)]
        
        while queue:
            current_id, depth = queue.pop(0)
            if depth >= max_depth or current_id == '0':
                continue
                
            ancestors.add(current_id)
            
            if current_id in pedigree:
                father = pedigree[current_id]['father']
                mother = pedigree[current_id]['mother']
                
                if father != '0':
                    queue.append((father, depth + 1))
                if mother != '0':
                    queue.append((mother, depth + 1))
        
        return ancestors
    
    male_ancestors = get_ancestors(male_id, male_pedigree, max_gen)
    female_ancestors = get_ancestors(female_id, female_pedigree, max_gen)
    
    # ตรวจสอบบรรพบุรุษร่วม
    return bool(male_ancestors & female_ancestors)


def find_breeding_pairs():
    """
    หาคู่หนูที่สามารถผสมพันธุ์กันได้ พร้อมประเมินความเสี่ยงตามเกณฑ์ (แก้ไขแล้ว)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # หาหนูที่พร้อมผสมพันธุ์และไม่ป่วย
        cursor.execute("""
            SELECT r.rat_id, r.gender, r.birth_date, r.weight, r.size
            FROM rat r
            WHERE r.status = 'breeder2'
            AND r.rat_id NOT IN (
                SELECT h.rat_id
                FROM health h
                WHERE h.results <> 'healed'
            )
            ORDER BY r.gender, r.birth_date
        """)
        
        available_rats = cursor.fetchall()
        males = [rat for rat in available_rats if rat[1] == 'male']
        females = [rat for rat in available_rats if rat[1] == 'female']
        
        # หาบ่อว่าง
        cursor.execute("""
            SELECT pond_id
            FROM pond
            WHERE status = 'empty'
            ORDER BY pond_id
        """)
        
        available_ponds = cursor.fetchall()
        if not available_ponds:
            print("ไม่มีบ่อว่างสำหรับการผสมพันธุ์")
            return []
        
        possible_pairs = []
        
        for male in males:
            male_id = male[0]
            male_pedigree = get_pedigree_data(male_id, cursor, generation=5)
            
            for female in females:
                female_id = female[0]
                female_pedigree = get_pedigree_data(female_id, cursor, generation=5)
                
                # ตรวจสอบความสัมพันธ์เครือญาติ
                if is_closely_related(male_id, female_id, male_pedigree, female_pedigree, max_gen=3):
                    continue
                
                # รวม pedigree และคำนวณค่า inbreeding coefficient
                combined_pedigree = {**male_pedigree, **female_pedigree}
                R, F = tabular_method(combined_pedigree)
                
                # คำนวณค่า inbreeding coefficient ของลูก
                theoretical_offspring_F = 0.5 * R.get((male_id, female_id), 0)
                
                # ประเมินความเสี่ยง
                if theoretical_offspring_F < 0.0625:  # < 6.25%
                    risk_level = 'ปลอดภัย'
                elif theoretical_offspring_F <= 0.125:  # 6.25-12.5%
                    risk_level = 'เฝ้าระวัง'
                else:  # > 12.5%
                    continue  # ไม่รวมคู่ที่มีความเสี่ยงสูง
                
                # ตรวจสอบประวัติการผสมพันธุ์
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM breeding
                    WHERE (father_id = ? AND mother_id = ?)
                    AND breeding_status = 'unsuccess'
                """, (male_id, female_id))
                
                if cursor.fetchone()[0] > 0:
                    continue  # ข้ามคู่ที่เคยผสมไม่สำเร็จ
                
                possible_pairs.append({
                    'male_id': male_id,
                    'male_weight': male[3],
                    'male_size': male[4],
                    'female_id': female_id,
                    'female_weight': female[3],
                    'female_size': female[4],
                    'inbreeding_coef': theoretical_offspring_F,
                    'risk_level': risk_level,
                    'pond_id': available_ponds[0][0] if available_ponds else None
                })
        
        # เรียงลำดับตามค่า inbreeding coefficient จากน้อยไปมาก
        possible_pairs.sort(key=lambda x: x['inbreeding_coef'])
        
        return possible_pairs
        
    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return []
    
    finally:
        conn.close()
  