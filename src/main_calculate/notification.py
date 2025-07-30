import sqlite3
from storages.database_service import get_connection


def show_expire_rat():
    """
    หาคู่ผสมพันธุ์ที่ต้องดำเนินการแยกตาม 3 กรณี:
    1. คู่ที่ประสิทธิภาพลดลง -> แยกคู่
    2. คู่ที่ไม่ยอมผสมพันธุ์ -> แยกคู่ + กำจัดตามเงื่อนไข
    3. คู่ที่ผสมพันธุ์สำเร็จมาก -> แยกคู่ + กำจัดตามเงื่อนไข
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # หาคู่ที่กำลังผสมพันธุ์อยู่
        cursor.execute(
            """
            SELECT 
                b.breeding_id,
                b.father_id,
                b.mother_id,
                b.breeding_date,
                f.gender as father_gender,
                f.has_ring as father_has_ring,
                f.ring_number as father_ring_number,
                f.farm_id as father_farm_id,
                m.gender as mother_gender,
                m.has_ring as mother_has_ring,
                m.ring_number as mother_ring_number,
                m.farm_id as mother_farm_id,
                -- นับจำนวนครั้งที่ผสมสำเร็จของแต่ละตัว
                (SELECT COUNT(*) FROM breeding b2 WHERE b2.father_id = b.father_id AND b2.breeding_status = 'success') as father_success_count,
                (SELECT COUNT(*) FROM breeding b3 WHERE b3.mother_id = b.mother_id AND b3.breeding_status = 'success') as mother_success_count,
                -- นับจำนวนครั้งที่ผสมไม่สำเร็จของแต่ละตัว
                (SELECT COUNT(*) FROM breeding b4 WHERE (b4.father_id = b.father_id OR b4.mother_id = b.father_id) AND b4.breeding_status = 'unsuccess') as father_unsuccess_count,
                (SELECT COUNT(*) FROM breeding b5 WHERE (b5.father_id = b.mother_id OR b5.mother_id = b.mother_id) AND b5.breeding_status = 'unsuccess') as mother_unsuccess_count
            FROM breeding b
            JOIN rat f ON b.father_id = f.rat_id
            JOIN rat m ON b.mother_id = m.rat_id
            WHERE b.breeding_status = 'breeding'
              AND f.status IN ('breeder1', 'breeder2')
              AND m.status IN ('breeder1', 'breeder2')
        """
        )
        active_breeding_pairs = cursor.fetchall()

        # วิเคราะห์ประสิทธิภาพของแต่ละคู่
        breeding_pairs_to_update = []

        for pair_data in active_breeding_pairs:
            (
                breeding_id,
                father_id,
                mother_id,
                breeding_date,
                father_gender,
                father_has_ring,
                father_ring_number,
                father_farm_id,
                mother_gender,
                mother_has_ring,
                mother_ring_number,
                mother_farm_id,
                father_success_count,
                mother_success_count,
                father_unsuccess_count,
                mother_unsuccess_count,
            ) = pair_data

            # ตรวจสอบเงื่อนไขต่างๆ
            category = None
            reason = ""
            father_action = "to_breeder2"  # default
            mother_action = "to_breeder2"  # default
            priority = 3

            # 1. ตรวจสอบไม่ยอมผสมพันธุ์ (ด่วนที่สุด)
            if father_unsuccess_count > 5 or mother_unsuccess_count > 5:
                category = "unsuccessful_breeding"
                reason = f"ไม่ยอมผสมพันธุ์"
                if father_unsuccess_count > 5:
                    father_action = "to_fertilize"
                    reason += f" (พ่อ: {father_unsuccess_count} ครั้ง)"
                if mother_unsuccess_count > 5:
                    mother_action = "to_fertilize"
                    reason += f" (แม่: {mother_unsuccess_count} ครั้ง)"
                priority = 1

            # 2. ตรวจสอบผสมพันธุ์สำเร็จมาก
            elif father_success_count > 7 or mother_success_count > 7:
                category = "over_successful_breeding"
                reason = f"ผสมพันธุ์สำเร็จครบกำหนด"
                if father_success_count > 7:
                    father_action = "to_fertilize"
                    reason += f" (พ่อ: {father_success_count} ครั้ง)"
                if mother_success_count > 7:
                    mother_action = "to_fertilize"
                    reason += f" (แม่: {mother_success_count} ครั้ง)"
                priority = 3

            # 3. ตรวจสอบประสิทธิภาพลดลง (ต้องมีประวัติการผสม >= 3 ครั้ง)
            else:
                # ตรวจสอบแนวโน้มของพ่อ
                cursor.execute(
                    """
                    WITH breeding_trend AS (
                        SELECT 
                            b.survived_pups,
                            ROW_NUMBER() OVER (ORDER BY b.breeding_date) as breeding_order,
                            LAG(b.survived_pups) OVER (ORDER BY b.breeding_date) as prev_pups
                        FROM breeding b
                        WHERE (b.father_id = ? OR b.mother_id = ?) 
                          AND b.breeding_status = 'success' 
                          AND b.survived_pups IS NOT NULL
                    )
                    SELECT 
                        COUNT(*) as total_breedings,
                        AVG(survived_pups) as overall_avg,
                        SUM(CASE WHEN prev_pups IS NOT NULL AND survived_pups < prev_pups THEN 1 ELSE 0 END) * 100.0 / 
                        NULLIF(COUNT(CASE WHEN prev_pups IS NOT NULL THEN 1 END), 0) as decline_percentage
                    FROM breeding_trend
                    WHERE breeding_order >= 2
                """,
                    (father_id, father_id),
                )

                father_trend = cursor.fetchone()

                # ตรวจสอบแนวโน้มของแม่
                cursor.execute(
                    """
                    WITH breeding_trend AS (
                        SELECT 
                            b.survived_pups,
                            ROW_NUMBER() OVER (ORDER BY b.breeding_date) as breeding_order,
                            LAG(b.survived_pups) OVER (ORDER BY b.breeding_date) as prev_pups
                        FROM breeding b
                        WHERE (b.father_id = ? OR b.mother_id = ?) 
                          AND b.breeding_status = 'success' 
                          AND b.survived_pups IS NOT NULL
                    )
                    SELECT 
                        COUNT(*) as total_breedings,
                        AVG(survived_pups) as overall_avg,
                        SUM(CASE WHEN prev_pups IS NOT NULL AND survived_pups < prev_pups THEN 1 ELSE 0 END) * 100.0 / 
                        NULLIF(COUNT(CASE WHEN prev_pups IS NOT NULL THEN 1 END), 0) as decline_percentage
                    FROM breeding_trend
                    WHERE breeding_order >= 2
                """,
                    (mother_id, mother_id),
                )

                mother_trend = cursor.fetchone()

                # ตรวจสอบว่ามีประสิทธิภาพลดลงหรือไม่
                father_declining = False
                mother_declining = False

                if father_trend and father_trend[0] >= 3:
                    if (
                        father_trend[2]
                        and father_trend[2] >= 70
                        and father_trend[1]
                        and father_trend[1] <= 4
                    ):
                        father_declining = True

                if mother_trend and mother_trend[0] >= 3:
                    if (
                        mother_trend[2]
                        and mother_trend[2] >= 70
                        and mother_trend[1]
                        and mother_trend[1] <= 4
                    ):
                        mother_declining = True

                if father_declining or mother_declining:
                    category = "declining_performance"
                    reason = "ประสิทธิภาพลดลง"
                    detail_parts = []
                    if father_declining:
                        detail_parts.append(
                            f"พ่อ: เฉลี่ย {round(father_trend[1], 1) if father_trend[1] else 0} ตัว"
                        )
                    if mother_declining:
                        detail_parts.append(
                            f"แม่: เฉลี่ย {round(mother_trend[1], 1) if mother_trend[1] else 0} ตัว"
                        )
                    reason += f" ({', '.join(detail_parts)})"
                    priority = 2

            # เพิ่มเข้าในรายการถ้าเข้าเงื่อนไขใดเงื่อนไขหนึ่ง
            if category:
                breeding_pairs_to_update.append(
                    {
                        "breeding_id": breeding_id,
                        "father_id": father_id,
                        "mother_id": mother_id,
                        "father_gender": father_gender,
                        "mother_gender": mother_gender,
                        "father_has_ring": father_has_ring,
                        "father_ring_number": father_ring_number,
                        "mother_has_ring": mother_has_ring,
                        "mother_ring_number": mother_ring_number,
                        "father_farm_id": father_farm_id,
                        "mother_farm_id": mother_farm_id,
                        "category": category,
                        "reason": reason,
                        "father_action": father_action,
                        "mother_action": mother_action,
                        "priority": priority,
                        "father_success_count": father_success_count,
                        "mother_success_count": mother_success_count,
                        "father_unsuccess_count": father_unsuccess_count,
                        "mother_unsuccess_count": mother_unsuccess_count,
                    }
                )

        # เรียงตาม priority
        breeding_pairs_to_update.sort(key=lambda x: x["priority"])

        # นับจำนวนแต่ละประเภท
        declining_count = len(
            [
                p
                for p in breeding_pairs_to_update
                if p["category"] == "declining_performance"
            ]
        )
        unsuccessful_count = len(
            [
                p
                for p in breeding_pairs_to_update
                if p["category"] == "unsuccessful_breeding"
            ]
        )
        successful_count = len(
            [
                p
                for p in breeding_pairs_to_update
                if p["category"] == "over_successful_breeding"
            ]
        )

        return {
            "success": True,
            "data": breeding_pairs_to_update,
            "total_count": len(breeding_pairs_to_update),
            "declining_count": declining_count,
            "unsuccessful_count": unsuccessful_count,
            "successful_count": successful_count,
        }

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในฐานข้อมูล: {e}")
        return {"success": False, "error": str(e), "data": []}
    finally:
        conn.close()


def process_expire_rats(breeding_pairs_to_update):
    """
    ดำเนินการกับคู่ผสมพันธุ์ที่หมดอายุแบบอัตโนมัติตามเงื่อนไข
    """
    if not breeding_pairs_to_update:
        return {"success": False, "message": "ไม่มีข้อมูลคู่ผสมพันธุ์ที่ต้องประมวลผล"}

    conn = get_connection()
    cursor = conn.cursor()

    try:
        conn.execute("BEGIN TRANSACTION")

        separated_count = 0
        disposed_count = 0
        rings_freed = []
        processed_pairs = []

        for pair in breeding_pairs_to_update:
            breeding_id = pair["breeding_id"]
            father_id = pair["father_id"]
            mother_id = pair["mother_id"]
            father_action = pair["father_action"]
            mother_action = pair["mother_action"]

            # 1. แยกคู่เสมอ (เปลี่ยน breeding status เป็น unsuccess)
            cursor.execute(
                """
                UPDATE breeding 
                SET breeding_status = 'unsuccess',
                    separation_date = DATE('now')
                WHERE breeding_id = ?
            """,
                (breeding_id,),
            )

            separated_count += 1

            # 2. จัดการหนูพ่อ
            if father_action == "to_fertilize":
                # ดึงข้อมูลห่วงขาก่อนกำจัด
                cursor.execute(
                    """
                    SELECT has_ring, ring_number 
                    FROM rat 
                    WHERE rat_id = ?
                """,
                    (father_id,),
                )

                rat_data = cursor.fetchone()
                ring_number = None
                if rat_data and rat_data[0] == 1 and rat_data[1]:
                    ring_number = rat_data[1]

                # กำจัดหนูพ่อ
                cursor.execute(
                    """
                    UPDATE rat 
                    SET status = 'fertilize',
                        has_ring = 0,
                        ring_number = NULL,
                        pond_id = NULL
                    WHERE rat_id = ?
                """,
                    (father_id,),
                )

                # เพิ่มห่วงขาเข้า missing_rings
                if ring_number:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO missing_rings (ring_number, lost_date, note)
                        VALUES (?, DATE('now'), ?)
                    """,
                        (ring_number, f"กำจัดจากหนู {father_id} - {pair['reason']}"),
                    )
                    rings_freed.append(ring_number)

                disposed_count += 1
            else:
                # เปลี่ยนเป็น breeder2
                cursor.execute(
                    """
                    UPDATE rat 
                    SET status = 'breeder2'
                    WHERE rat_id = ?
                """,
                    (father_id,),
                )

            # 3. จัดการหนูแม่
            if mother_action == "to_fertilize":
                # ดึงข้อมูลห่วงขาก่อนกำจัด
                cursor.execute(
                    """
                    SELECT has_ring, ring_number 
                    FROM rat 
                    WHERE rat_id = ?
                """,
                    (mother_id,),
                )

                rat_data = cursor.fetchone()
                ring_number = None
                if rat_data and rat_data[0] == 1 and rat_data[1]:
                    ring_number = rat_data[1]

                # กำจัดหนูแม่
                cursor.execute(
                    """
                    UPDATE rat 
                    SET status = 'fertilize',
                        has_ring = 0,
                        ring_number = NULL,
                        pond_id = NULL
                    WHERE rat_id = ?
                """,
                    (mother_id,),
                )

                # เพิ่มห่วงขาเข้า missing_rings
                if ring_number:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO missing_rings (ring_number, lost_date, note)
                        VALUES (?, DATE('now'), ?)
                    """,
                        (ring_number, f"กำจัดจากหนู {mother_id} - {pair['reason']}"),
                    )
                    rings_freed.append(ring_number)

                disposed_count += 1
            else:
                # เปลี่ยนเป็น breeder2
                cursor.execute(
                    """
                    UPDATE rat 
                    SET status = 'breeder2'
                    WHERE rat_id = ?
                """,
                    (mother_id,),
                )

            processed_pairs.append(
                {
                    "breeding_id": breeding_id,
                    "father_id": father_id,
                    "mother_id": mother_id,
                    "category": pair["category"],
                    "reason": pair["reason"],
                    "father_action": father_action,
                    "mother_action": mother_action,
                }
            )

        conn.commit()

        return {
            "success": True,
            "separated_count": separated_count,
            "disposed_count": disposed_count,
            "rings_freed": rings_freed,
            "processed_pairs": processed_pairs,
            "message": f"ประมวลผลเสร็จสิ้น: แยกคู่ {separated_count} คู่, กำจัด {disposed_count} ตัว",
        }

    except sqlite3.Error as e:
        conn.rollback()
        return {"success": False, "error": str(e), "message": f"เกิดข้อผิดพลาด: {e}"}
    finally:
        conn.close()


def get_expire_rat_notifications():
    """
    แปลงข้อมูลคู่ผสมพันธุ์ที่หมดอายุเป็น notification format
    """
    expire_result = show_expire_rat()

    if not expire_result.get("success", False):
        return []

    notifications = []
    pairs_data = expire_result.get("data", [])

    for pair in pairs_data:
        # กำหนดสีและประเภทตามหมวดหมู่
        if pair["category"] == "unsuccessful_breeding":
            notification_type = "emergency"
            color = "Red"
        elif pair["category"] == "declining_performance":
            notification_type = "warning"
            color = "ft.Colors.ORANGE_700"
        else:  # over_successful_breeding
            notification_type = "normal"
            color = "Neo_Mint"

        # ข้อมูลพื้นฐาน
        father_gender_text = "เมีย" if pair.get("father_gender") == "female" else "ผู้"
        mother_gender_text = "เมีย" if pair.get("mother_gender") == "female" else "ผู้"

        father_ring_info = (
            f"ห่วงขา: {pair['father_ring_number']}"
            if pair.get("father_ring_number")
            else "ไม่มีห่วงขา"
        )
        mother_ring_info = (
            f"ห่วงขา: {pair['mother_ring_number']}"
            if pair.get("mother_ring_number")
            else "ไม่มีห่วงขา"
        )

        # สร้างข้อความแจ้งเตือน
        topic = f"การผสมพันธุ์ ID: {pair['breeding_id']}"

        # รายละเอียดหนูแต่ละตัว
        father_detail = (
            f"พ่อพันธุ์: {father_ring_info}"
        )
        mother_detail = (
            f"แม่พันธุ์: {mother_ring_info}"
        )

        content = f"{father_detail} | {mother_detail}\nสาเหตุ: {pair['reason']}"

        # กำหนดการดำเนินการ
        actions = []
        if pair["father_action"] == "to_fertilize":
            actions.append(f"กำจัด {pair['father_id']}")
        if pair["mother_action"] == "to_fertilize":
            actions.append(f"กำจัด {pair['mother_id']}")

        if actions:
            action_text = f"แยกคู่ + {', '.join(actions)}"
        else:
            action_text = "แยกคู่"

        notifications.append(
            {
                "type": notification_type,
                "topic": topic,
                "content": content,
                "color": color,
                "source": "expire_breeding_pair",
                "action_text": action_text,
                "pair_data": pair,
            }
        )

    return notifications


def process_all_expire_rats():
    """
    ดำเนินการกับคู่ผสมพันธุ์ที่หมดอายุทั้งหมดแบบอัตโนมัติ
    """
    expire_result = show_expire_rat()

    if not expire_result.get("success", False):
        return {"success": False, "message": "ไม่สามารถดึงข้อมูลคู่ผสมพันธุ์ที่หมดอายุได้"}

    pairs_data = expire_result.get("data", [])
    if not pairs_data:
        return {"success": True, "message": "ไม่มีคู่ผสมพันธุ์ที่ต้องดำเนินการ"}

    # ดำเนินการกับคู่ผสมพันธุ์ทั้งหมดแบบอัตโนมัติ
    result = process_expire_rats(pairs_data)
    return result


def handle_single_expire_rat(pair_data):
    """
    จัดการการดำเนินการกับคู่ผสมพันธุ์ตัวเดียว
    """
    if not pair_data:
        return {"success": False, "message": "ไม่มีข้อมูลคู่ผสมพันธุ์"}

    try:
        result = process_expire_rats([pair_data])
        return result
    except Exception as e:
        return {"success": False, "message": str(e)}
