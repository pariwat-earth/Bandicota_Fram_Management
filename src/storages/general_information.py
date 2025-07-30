import flet as ft
from datetime import date, datetime
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Tuple

from storages.database_service import add_rat_information, get_connection


def get_managername():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ดึงชื่อผู้จัดการจากตาราง manager
        cursor.execute(
            "SELECT manager_name FROM farm WHERE farm_id = (SELECT farm_id FROM farm WHERE farm_type = 'main' LIMIT 1)"
        )
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return "ผู้จัดการฟาร์ม"
    except sqlite3.Error as e:
        print(f"Error in get_managername: {e}")
        # ถ้าเกิดข้อผิดพลาด ให้คืนค่าชื่อเริ่มต้น
        return "ผู้จัดการฟาร์ม"
    finally:
        # ปิดการเชื่อมต่อกับฐานข้อมูล
        conn.close()


def get_farm_name():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ดึงชื่อฟาร์มจากตาราง farm
        cursor.execute(
            "SELECT farm_name FROM farm WHERE farm_id = (SELECT farm_id FROM farm WHERE farm_type = 'main' LIMIT 1)"
        )
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return "ฟาร์มหนูพุกใหญ่"
    except sqlite3.Error as e:
        print(f"Error in get_farm_name: {e}")
        # ถ้าเกิดข้อผิดพลาด ให้คืนค่าชื่อเริ่มต้น
        return "ฟาร์มหลัก"
    finally:
        # ปิดการเชื่อมต่อกับฐานข้อมูล
        conn.close()


def get_amount_rat():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        count_query = "SELECT COUNT(*) FROM rat"

        cursor.execute(count_query)

        rat_count = cursor.fetchone()[0]

        return rat_count

    except sqlite3.Error as e:
        print(f"Error in get_amount_rat: {e}")
        return 0

    finally:
        # ปิดการเชื่อมต่อกับฐานข้อมูล
        conn.close()


def get_breeding_rat():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        count_query = "SELECT COUNT(*) FROM rat WHERE status = 'breeder1'"

        cursor.execute(count_query)

        breeding_rat_count = cursor.fetchone()[0]

        return breeding_rat_count

    except sqlite3.Error as e:
        print(f"Error in get_breeding_rat: {e}")
        return 0

    finally:
        # ปิดการเชื่อมต่อกับฐานข้อมูล
        conn.close()


def get_current_breeding_pair():
    return int(get_breeding_rat() / 2)


def get_breeding_success_rate():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ดึงจำนวนหนูที่เป็น success
        cursor.execute(
            "SELECT COUNT(*) FROM breeding WHERE breeding_status = 'success'"
        )
        success_count = cursor.fetchone()[0]

        # ดึงจำนวนหนูทั้งหมดที่มีสถานะแน่นอน (ไม่รวม 'breeding')
        cursor.execute(
            "SELECT COUNT(*) FROM breeding WHERE breeding_status IN ('success', 'unsuccess', 'disorders')"
        )
        total_completed = cursor.fetchone()[0]

        if total_completed == 0:
            return 0.0

        success_rate = (success_count / total_completed) * 100
        return round(success_rate, 2)

    except sqlite3.Error as e:
        print(f"Error in get_breeding_success_rate: {e}")
        return 0.0
    finally:
        conn.close()


def get_amount_farm():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        count_query = "SELECT COUNT(*) FROM farm"

        cursor.execute(count_query)

        farm_count = cursor.fetchone()[0]

        return farm_count

    except sqlite3.Error as e:
        print(f"Error in get_amount_farm: {e}")
        return 0

    finally:
        # ปิดการเชื่อมต่อกับฐานข้อมูล
        conn.close()


def get_amount_pond():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        sum_query = "SELECT SUM(ponds_amount) FROM farm"

        cursor.execute(sum_query)

        result = cursor.fetchone()[0]

        pond_sum = result if result is not None else 0

        return pond_sum

    except sqlite3.Error as e:
        print(f"Error in get_amount_pond: {e}")
        return 0

    finally:
        conn.close()


def update_hmt_page(page_name):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ตรวจสอบว่ามีข้อมูลที่ page_id = 1 หรือไม่
        cursor.execute("SELECT COUNT(*) FROM hmt_page WHERE page_id = 1")
        count = cursor.fetchone()[0]

        if count > 0:
            update_query = "UPDATE hmt_page SET page_current_name = ? WHERE page_id = 1"
            cursor.execute(update_query, (page_name,))
        else:
            insert_query = (
                "INSERT INTO hmt_page (page_id, page_current_name) VALUES (1, ?)"
            )
            cursor.execute(insert_query, (page_name,))

        conn.commit()
        return True

    except sqlite3.Error as e:
        conn.rollback()
        return False

    finally:
        conn.close()


def get_current_page_name():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT page_current_name FROM hmt_page WHERE page_id = 1")
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return "main"

    except sqlite3.Error as e:
        return "main"

    finally:
        conn.close()


def update_selected_farm_id(farm_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS selected_farm (
                id INTEGER PRIMARY KEY,
                farm_id INTEGER
            )
        """
        )

        cursor.execute("SELECT COUNT(*) FROM selected_farm")
        count = cursor.fetchone()[0]

        if count > 0:
            # อัปเดต farm_id
            cursor.execute(
                "UPDATE selected_farm SET farm_id = ? WHERE id = 1", (farm_id,)
            )
        else:
            # เพิ่มข้อมูลใหม่
            cursor.execute(
                "INSERT INTO selected_farm (id, farm_id) VALUES (1, ?)", (farm_id,)
            )

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Error in update_selected_farm_id: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def generate_rat_id():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # รับวันที่ปัจจุบัน
        today = date.today()
        date_prefix = today.strftime("%Y%m%d")  # รูปแบบ YYYYMMDD

        # ค้นหาลำดับสูงสุดของวันนี้
        query = """
            SELECT rat_id FROM rat 
            WHERE rat_id LIKE ? 
            ORDER BY rat_id DESC 
            LIMIT 1
        """

        cursor.execute(query, (f"{date_prefix}%",))
        result = cursor.fetchone()

        if result:
            # ถ้ามีรหัสหนูของวันนี้แล้ว ให้เพิ่มลำดับที่ขึ้น 1
            last_id = result[0]
            # แยกส่วนลำดับหมายเลขจากรหัส (4 ตัวสุดท้าย)
            sequence_number = int(last_id[-4:])
            next_sequence = sequence_number + 1
        else:
            # ถ้าไม่มีรหัสหนูของวันนี้ ให้เริ่มที่ 1
            next_sequence = 1

        # สร้างรหัสใหม่โดยรวมวันที่กับลำดับที่ (เติม 0 ด้านหน้าให้ครบ 4 หลัก)
        new_rat_id = f"{date_prefix}{next_sequence:04d}"

        return new_rat_id

    except sqlite3.Error as e:
        import time

        timestamp = int(time.time())
        return f"{date_prefix}{timestamp % 10000:04d}"

    finally:
        conn.close()


def get_max_ring():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ดึงข้อมูลจำนวนห่วงขาทั้งหมดของฟาร์ม
        cursor.execute("SELECT ring_amount FROM farm")

        farm_result = cursor.fetchone()
        if not farm_result:
            # ถ้าไม่พบข้อมูลฟาร์ม ให้ return None
            return None

        total_rings = farm_result[0]

        # ดึงข้อมูลห่วงขาที่ใช้ไปแล้วในฟาร์มนี้ (เฉพาะหนูที่มี has_ring = 1)
        cursor.execute(
            """
            SELECT ring_number FROM rat 
            WHERE has_ring = 1 AND ring_number IS NOT NULL
            ORDER BY ring_number
            """
        )

        used_rings = [row[0] for row in cursor.fetchall()]

        # ถ้ายังไม่มีห่วงขาที่ถูกใช้ ให้ return 1 (เริ่มที่ 1)
        if not used_rings:
            return 1

        # หาหมายเลขห่วงขาที่ยังไม่ได้ใช้ที่มีค่าน้อยที่สุด
        # โดยตรวจสอบช่องว่างระหว่างหมายเลขที่ใช้แล้ว
        previous = 0
        for ring in used_rings:
            if ring > previous + 1:
                # พบช่องว่าง
                return previous + 1
            previous = ring

        # ถ้าไม่พบช่องว่าง ให้ใช้หมายเลขถัดไปจากหมายเลขสูงสุดที่ใช้
        next_ring = used_rings[-1] + 1

        # ตรวจสอบว่าเกินจำนวนห่วงขาของฟาร์มหรือไม่
        if next_ring > total_rings:
            # ถ้าเกิน ให้ return None (หมายถึงห่วงขาเต็มแล้ว)
            return None

        return next_ring

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการค้นหาหมายเลขห่วงขา: {e}")
        return None

    finally:
        conn.close()


def get_pond_id_by_farm_id(pond_index, farm_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT pond_id FROM pond WHERE pond_index = ? AND farm_id = ?"
        cursor.execute(query, (pond_index, farm_id))

        pond_id = cursor.fetchone()[0]
        return pond_id

    except sqlite3.Error as e:
        return False

    finally:
        conn.close()


def check_pond_exists(pond_id, farm_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT COUNT(*) FROM pond WHERE pond_id = ? AND farm_id = ?"
        cursor.execute(query, (pond_id, farm_id))

        count = cursor.fetchone()[0]
        return count > 0

    except sqlite3.Error as e:
        return False

    finally:
        conn.close()


def check_ring_used(farm_id, ring_number):
    """
    ตรวจสอบว่าหมายเลขห่วงขาถูกใช้ไปแล้วหรือไม่

    Args:
        farm_id (int): รหัสฟาร์ม
        ring_number (int): หมายเลขห่วงขาที่ต้องการตรวจสอบ

    Returns:
        bool: True ถ้าหมายเลขห่วงขานี้ถูกใช้ไปแล้ว, False ถ้ายังไม่ถูกใช้
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if farm_id is None:
            cursor.execute(
                """
                SELECT COUNT(*) FROM rat 
                WHERE has_ring = 1 AND ring_number = ?
                """,
                (ring_number,),
            )
        else:
            cursor.execute(
                """
                SELECT COUNT(*) FROM rat 
                WHERE farm_id = ? AND has_ring = 1 AND ring_number = ?
                """,
                (farm_id, ring_number),
            )

        count = cursor.fetchone()[0]
        return count > 0

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการตรวจสอบหมายเลขห่วงขา: {e}")
        return True  # ถ้าเกิดข้อผิดพลาด ให้ถือว่าใช้ไปแล้ว (เพื่อความปลอดภัย)

    finally:
        conn.close()


def check_pond_used(pond_id):
    """
    ตรวจสอบว่าหมายเลขบ่อถูกใช้ไปแล้วหรือไม่

    Args:
        farm_id (int): รหัสฟาร์ม
        pond_id (int): หมายเลขบ่อที่ต้องการตรวจสอบ

    Returns:
        bool: True ถ้าหมายเลขบ่อถูกใช้ไปแล้ว, False ถ้ายังไม่ถูกใช้
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM pond 
            WHERE pond_id = ? 
            AND status = 'empty' 
            AND farm_id = (SELECT farm_id FROM farm WHERE farm_type = 'main')
            """,
            (pond_id),
        )

        count = cursor.fetchone()[0]
        return count > 0

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการตรวจสอบหมายเลขบ่อ: {e}")
        return True  # ถ้าเกิดข้อผิดพลาด ให้ถือว่าใช้ไปแล้ว (เพื่อความปลอดภัย)

    finally:
        conn.close()


def check_gender(ring_number, gender):
    """
    ตรวจสอบว่าหมายเลขห่วงขาเป็นเพศที่ต้องการหรือไม่

    Args:
        ring_number (str): หมายเลขห่วงขาที่ต้องการตรวจสอบ
    Returns:
        bool: True ถ้าเพศตรงกัน, False ถ้าไม่ตรงกัน
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM rat 
            WHERE ring_number = ? AND gender = ?;
            """,
            (ring_number, gender),
        )

        count = cursor.fetchone()[0]
        return count > 0

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการตรวจสอบหมายเลขบ่อ: {e}")
        return True  # ถ้าเกิดข้อผิดพลาด ให้ถือว่าใช้ไปแล้ว (เพื่อความปลอดภัย)

    finally:
        conn.close()


def get_breeding_information():
    """
    ดึงข้อมูลการผสมพันธุ์หนูจากฐานข้อมูล

    Returns:
        dict: ข้อมูลการผสมพันธุ์หนู
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT breeding_id, father_id, mother_id, breeding_status
            FROM breeding order by breeding_id DESC;
            """
        )

        result = cursor.fetchall()
        datas = []

        for row in result:
            breeding_id = row[0]
            father_id = row[1]
            mother_id = row[2]

            if row[3] == "breeding":
                breeding_status = "กำลังผสมพันธุ์"
                color = ft.Colors.ORANGE_500
            elif row[3] == "success":
                breeding_status = "ผสมพันธุ์สำเร็จ"
                color = ft.Colors.GREEN_300
            elif row[3] == "unsuccess":
                breeding_status = "ผสมพันธุ์ล้มเหลว"
                color = ft.Colors.RED_300
            elif row[3] == "disorders":
                breeding_status = "ผสมแล้วได้หนูเผือก"
                color = ft.Colors.RED_500

            data = {
                "topic": f"การผสมพันธุ์ที่: {breeding_id}",
                "content": f"พ่อพันธุ์พ่อพันธุ์: {father_id} x แม่พันธุ์: {mother_id}",
                "result": breeding_status,
                "color": color,
            }

            datas.append(data)

        return datas

    except sqlite3.Error as e:
        print(f"Error in get_breeding_information: {e}")
        return {"breeding_pair": 0, "breeding_success_rate": 0.0}

    finally:
        conn.close()


def get_pond_use_rate():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ดึงจำนวนบ่อทั้งหมด
        cursor.execute("SELECT COUNT(*) FROM pond")
        total_ponds = cursor.fetchone()[0]

        # ดึงจำนวนบ่อที่ถูกใช้
        cursor.execute("SELECT COUNT(*) FROM pond WHERE status <> 'empty'")
        used_ponds = cursor.fetchone()[0]

        if total_ponds == 0:
            return 0.0

        use_rate = (used_ponds / total_ponds) * 100

        return use_rate

    except sqlite3.Error as e:
        print(f"Error in get_pond_use_rate: {e}")
        return 0.0

    finally:
        conn.close()


def find_ring_number(farm_id: int = None) -> Optional[int]:
    """
    หาเลขห่วงขาที่ว่างหมายเลขต่ำสุดที่สามารถใช้งานได้

    Args:
        farm_id: รหัสฟาร์ม (ถ้าไม่ระบุจะใช้ฟาร์มหลัก)

    Returns:
        int: หมายเลขห่วงขาที่ว่างและมีค่าต่ำสุด หรือ None ถ้าไม่มีว่าง
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ถ้าไม่ระบุ farm_id ให้ใช้ฟาร์มหลัก
        if farm_id is None:
            cursor.execute("SELECT farm_id FROM farm WHERE farm_type = 'main' LIMIT 1")
            result = cursor.fetchone()
            if result:
                farm_id = result[0]
            else:
                return None

        # ดึงจำนวนห่วงขาทั้งหมดที่ฟาร์มมี
        cursor.execute("SELECT ring_amount FROM farm WHERE farm_id = ?", (farm_id,))
        result = cursor.fetchone()
        if not result:
            return None

        ring_amount = result[0]

        # ดึงหมายเลขห่วงขาที่ถูกใช้งานอยู่ในฟาร์มนี้
        cursor.execute(
            """
            SELECT ring_number FROM rat 
            WHERE ring_number IS NOT NULL AND has_ring = 1 AND farm_id = ?
        """,
            (farm_id,),
        )
        used_rings = {row[0] for row in cursor.fetchall()}

        # ดึงหมายเลขห่วงขาที่หาย
        cursor.execute("SELECT ring_number FROM missing_rings")
        missing_rings = {row[0] for row in cursor.fetchall()}

        # หาหมายเลขห่วงขาที่ว่างที่ต่ำที่สุด
        for i in range(1, ring_amount + 1):
            if i not in used_rings and i not in missing_rings:
                return i

        return None

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None

    finally:
        conn.close()


def import_rat_from_csv(csv_path: str, farm_id: int = 1) -> dict:
    """
    นำเข้าข้อมูลหนูจากไฟล์ CSV พร้อมการเรียงลำดับตาม dependency
    """
    try:
        # อ่านข้อมูลจาก CSV
        df = pd.read_csv(csv_path, sep=",", encoding="utf-8-sig")

        # *** แก้ไข: ทำความสะอาดข้อมูล ID columns ***
        def clean_id_column(value):
            """ทำความสะอาด ID columns ให้เป็น string ที่ถูกต้อง"""
            if pd.isna(value):
                return None

            # แปลงเป็น string และลบ .0 ออก
            str_value = str(value).strip()
            if str_value.endswith(".0"):
                str_value = str_value[:-2]

            # ตรวจสอบว่าเป็นค่าว่างหรือไม่
            if str_value in ["", "nan", "0"]:
                return None

            return str_value

        # ทำความสะอาดข้อมูล ID columns
        df["rat_id"] = df["rat_id"].apply(clean_id_column)
        df["father_id"] = df["father_id"].apply(clean_id_column)
        df["mother_id"] = df["mother_id"].apply(clean_id_column)

        # ทำความสะอาดข้อมูลคอลัมน์อื่นๆ
        for col in df.columns:
            if df[col].dtype == "object" and col not in [
                "rat_id",
                "father_id",
                "mother_id",
            ]:
                df[col] = df[col].astype(str).str.strip()

        # แปลงวันที่
        df["birth_date"] = pd.to_datetime(df["birth_date"]).dt.date

        def calculate_generation_level(row_index, df_data, memo={}):
            """
            คำนวณ generation level ของหนูแต่ละตัว
            ใช้ recursive approach และ memoization
            """
            rat_id = df_data.iloc[row_index]["rat_id"]

            # ตรวจสอบ memo cache
            if rat_id in memo:
                return memo[rat_id]

            father_id = df_data.iloc[row_index]["father_id"]
            mother_id = df_data.iloc[row_index]["mother_id"]

            # ถ้าไม่มีพ่อแม่ = generation 0
            if father_id is None and mother_id is None:
                memo[rat_id] = 0
                return 0

            # หา generation ของพ่อและแม่
            father_gen = 0
            mother_gen = 0

            if father_id is not None:
                # หาแถวของพ่อ
                father_rows = df_data[df_data["rat_id"] == father_id]
                if not father_rows.empty:
                    father_index = father_rows.index[0]
                    father_gen = calculate_generation_level(father_index, df_data, memo)

            if mother_id is not None:
                # หาแถวของแม่
                mother_rows = df_data[df_data["rat_id"] == mother_id]
                if not mother_rows.empty:
                    mother_index = mother_rows.index[0]
                    mother_gen = calculate_generation_level(mother_index, df_data, memo)

            # generation ของลูก = max(generation ของพ่อ, generation ของแม่) + 1
            generation = max(father_gen, mother_gen) + 1
            memo[rat_id] = generation
            return generation

        # คำนวณ generation level สำหรับทุกแถว
        df["generation_level"] = df.index.map(
            lambda i: calculate_generation_level(i, df)
        )

        # เรียงลำดับตาม generation level และ rat_id
        df = df.sort_values(["generation_level", "rat_id"])

        # ลบ column ที่ใช้ช่วย
        df = df.drop("generation_level", axis=1)

        # Debug: แสดงลำดับที่เรียงแล้ว
        print("ลำดับการ import:")
        for index, row in df.iterrows():
            father = row["father_id"] if row["father_id"] is not None else "None"
            mother = row["mother_id"] if row["mother_id"] is not None else "None"
            print(f"  {row['rat_id']} (พ่อ: {father}, แม่: {mother})")

        imported_rats = []
        errors = []
        ring_changes = []

        # ตรวจสอบฟาร์ม
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM farm WHERE farm_id = ?", (farm_id,))
        if not cursor.fetchone():
            conn.close()
            return {
                "success": False,
                "message": f"ไม่พบข้อมูลฟาร์ม ID {farm_id}",
                "details": None,
            }
        conn.close()

        # ดำเนินการ import ตามลำดับที่เรียงแล้ว
        for index, row in df.iterrows():
            try:
                # ตรวจสอบและแปลงข้อมูล
                rat_id = row["rat_id"]
                father_id = row["father_id"]
                mother_id = row["mother_id"]

                # ตรวจสอบว่า rat_id ซ้ำหรือไม่
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM rat WHERE rat_id = ?", (rat_id,))
                if cursor.fetchone():
                    conn.close()
                    errors.append(f"แถว {index + 2}: หนูรหัส {rat_id} มีอยู่แล้วในระบบ")
                    continue

                # ตรวจสอบว่า father_id และ mother_id มีอยู่ในระบบหรือไม่
                if father_id:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM rat WHERE rat_id = ?", (father_id,))
                    if not cursor.fetchone():
                        conn.close()
                        errors.append(f"แถว {index + 2}: ไม่พบพ่อพันธุ์ {father_id} ในระบบ")
                        print(f"❌ ไม่พบพ่อพันธุ์: {father_id} สำหรับ {rat_id}")
                        continue

                if mother_id:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 FROM rat WHERE rat_id = ?", (mother_id,))
                    if not cursor.fetchone():
                        conn.close()
                        errors.append(f"แถว {index + 2}: ไม่พบแม่พันธุ์ {mother_id} ในระบบ")
                        print(f"❌ ไม่พบแม่พันธุ์: {mother_id} สำหรับ {rat_id}")
                        continue

                conn.close()

                # จัดการหมายเลขห่วงขา
                has_ring = 1 if str(row.get("has_ring", "0")).strip() == "1" else 0
                ring_number = None
                original_ring = None

                if has_ring == 1:
                    if "ring_number" in row and not pd.isna(row["ring_number"]):
                        original_ring = int(row["ring_number"])

                        if check_ring_used(farm_id, original_ring):
                            new_ring = get_max_ring()
                            if new_ring is None:
                                has_ring = 0
                                ring_number = None
                                ring_changes.append(
                                    {
                                        "rat_id": rat_id,
                                        "row": index + 2,
                                        "original_ring": original_ring,
                                        "new_ring": None,
                                        "reason": "ห่วงขาเต็มแล้ว",
                                        "action": "ยกเลิกการใส่ห่วงขา",
                                    }
                                )
                            else:
                                ring_number = new_ring
                                ring_changes.append(
                                    {
                                        "rat_id": rat_id,
                                        "row": index + 2,
                                        "original_ring": original_ring,
                                        "new_ring": new_ring,
                                        "reason": f"หมายเลข {original_ring} ถูกใช้แล้ว",
                                        "action": f"เปลี่ยนเป็น {new_ring}",
                                    }
                                )
                        else:
                            ring_number = original_ring
                    else:
                        ring_number = get_max_ring()
                        if ring_number is None:
                            has_ring = 0
                            ring_changes.append(
                                {
                                    "rat_id": rat_id,
                                    "row": index + 2,
                                    "original_ring": None,
                                    "new_ring": None,
                                    "reason": "ห่วงขาเต็มแล้ว",
                                    "action": "ยกเลิกการใส่ห่วงขา",
                                }
                            )

                # เตรียมข้อมูลสำหรับบันทึก
                rat_data = (
                    rat_id,
                    father_id,
                    mother_id,
                    row["birth_date"],
                    str(row["gender"]).strip().lower(),
                    (
                        float(row.get("weight", 0))
                        if not pd.isna(row.get("weight"))
                        else None
                    ),
                    float(row.get("size", 0)) if not pd.isna(row.get("size")) else None,
                    str(row.get("breed", "")).strip(),
                    str(row.get("status", "breeder2")).strip(),
                    (
                        int(row.get("pond_id"))
                        if not pd.isna(row.get("pond_id"))
                        and str(row.get("pond_id")).strip() != "0"
                        else None
                    ),
                    farm_id,
                    has_ring,
                    ring_number,
                    (
                        str(row.get("special_traits", "")).strip()
                        if not pd.isna(row.get("special_traits"))
                        else None
                    ),
                )

                result = add_rat_information(rat_data)

                if result:
                    imported_rats.append(rat_id)
                    print(f"✅ นำเข้าสำเร็จ: {rat_id}")
                else:
                    errors.append(f"แถว {index + 2}: ไม่สามารถบันทึกข้อมูลหนูรหัส {rat_id}")
                    print(f"❌ นำเข้าไม่สำเร็จ: {rat_id}")

            except Exception as e:
                error_msg = f"แถว {index + 2}: ไม่สามารถนำเข้าข้อมูลหนูรหัส {row.get('rat_id', 'ไม่ระบุ')}: {str(e)}"
                errors.append(error_msg)
                print(f"💥 Error: {error_msg}")

        # บันทึกประวัติการนำเข้า
        conn = get_connection()
        cursor = conn.cursor()
        import_id = f"IMP{datetime.now().strftime('%Y%m%d%H%M%S')}"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            INSERT INTO import_history (
                import_id, import_date, file_name, status, error_message
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                import_id,
                current_time,
                csv_path.split("/")[-1],
                "success" if not errors else "unsuccess",
                "\n".join(errors) if errors else None,
            ),
        )

        conn.commit()
        conn.close()

        result_msg = f"นำเข้าข้อมูลสำเร็จ {len(imported_rats)} ตัว"
        if errors:
            result_msg += f", มีข้อผิดพลาด {len(errors)} รายการ"

        return {
            "success": len(imported_rats) > 0,
            "message": result_msg,
            "details": {
                "imported_rats": imported_rats,
                "errors": errors,
                "ring_changes": ring_changes,
                "import_id": import_id,
                "total_processed": len(df),
                "success_count": len(imported_rats),
                "error_count": len(errors),
                "ring_change_count": len(ring_changes),
            },
        }

    except Exception as e:
        error_msg = f"เกิดข้อผิดพลาดในการนำเข้าข้อมูล: {str(e)}"
        return {"success": False, "message": error_msg, "details": None}


def get_export_history() -> List[Dict]:
    """ดึงประวัติการส่งออกข้อมูล"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT export_id, export_date, file_name, file_type, status, note
            FROM export_history
            ORDER BY export_date DESC
            LIMIT 50
        """
        )

        records = cursor.fetchall()
        conn.close()

        return [
            {
                "export_id": record[0],
                "export_date": record[1],
                "file_name": record[2],
                "file_type": record[3],
                "status": record[4],
                "note": record[5],
            }
            for record in records
        ]
    except Exception as e:
        print(f"Error getting export history: {e}")
        return []


def get_import_history() -> List[Dict]:
    """ดึงประวัติการนำเข้าข้อมูล"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT import_id, import_date, file_name, status, error_message
            FROM import_history
            ORDER BY import_date DESC
            LIMIT 50
        """
        )

        records = cursor.fetchall()
        conn.close()

        return [
            {
                "import_id": record[0],
                "import_date": record[1],
                "file_name": record[2],
                "status": record[3],
                "error_message": record[4],
            }
            for record in records
        ]
    except Exception as e:
        print(f"Error getting import history: {e}")
        return []


def analyze_csv_for_ring_changes(csv_path: str, farm_id: int = 1) -> dict:
    """
    วิเคราะห์ไฟล์ CSV เพื่อหาการเปลี่ยนแปลงห่วงขาที่จะเกิดขึ้น
    รองรับการจัดการหมายเลขห่วงขาหลายตัวไม่ให้ซ้ำกัน

    Args:
        csv_path: ที่อยู่ไฟล์ CSV
        farm_id: รหัสฟาร์ม

    Returns:
        dict: ผลการวิเคราะห์
    """
    try:
        # อ่านข้อมูลจาก CSV
        df = pd.read_csv(csv_path, sep=",", encoding="utf-8-sig")

        # ทำความสะอาดข้อมูล
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.strip()

        ring_changes = []
        duplicate_rats = []
        errors = []
        total_rats = len(df)

        # *** เพิ่มการติดตามหมายเลขห่วงขาที่จะใช้ในเซสชันนี้ ***
        used_rings_in_session = set()

        # ตรวจสอบฟาร์ม
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM farm WHERE farm_id = ?", (farm_id,))
        if not cursor.fetchone():
            conn.close()
            return {
                "success": False,
                "message": f"ไม่พบข้อมูลฟาร์ม ID {farm_id}",
                "details": None,
            }
        conn.close()

        def get_available_ring_number(farm_id: int, exclude_set: set) -> int:
            """
            หาหมายเลขห่วงขาที่ว่างและไม่ซ้ำกับที่จะใช้ในเซสชันนี้
            """
            current_ring = get_max_ring()
            if current_ring is None:
                return None

            # ตรวจสอบว่าหมายเลขนี้ถูกใช้ในเซสชันนี้หรือไม่
            while current_ring in exclude_set:
                # หาหมายเลขถัดไป
                next_ring = current_ring + 1
                if check_ring_used(farm_id, next_ring):
                    # หมายเลขถัดไปถูกใช้แล้ว ต้องหาใหม่
                    current_ring = next_ring + 1
                else:
                    current_ring = next_ring

                # ป้องกันการวนลูปไม่สิ้นสุด (ถ้าห่วงขาเต็มจริงๆ)
                if current_ring > 999999:  # สมมติว่าหมายเลขสูงสุดคือ 999999
                    return None

            return current_ring

        for index, row in df.iterrows():
            try:
                rat_id = str(row.get("rat_id", f"RAT_{index+1}")).strip()

                # ตรวจสอบ rat_id ซ้ำ
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM rat WHERE rat_id = ?", (rat_id,))
                if cursor.fetchone():
                    duplicate_rats.append(
                        {
                            "row": index + 2,
                            "rat_id": rat_id,
                            "reason": "หนูรหัสนี้มีอยู่แล้วในระบบ",
                        }
                    )
                    conn.close()
                    continue
                conn.close()

                # ตรวจสอบห่วงขา
                has_ring = 1 if str(row.get("has_ring", "0")).strip() == "1" else 0

                if has_ring == 1:
                    if "ring_number" in row and not pd.isna(row["ring_number"]):
                        original_ring = int(row["ring_number"])

                        # ตรวจสอบว่าหมายเลขห่วงขาถูกใช้แล้วหรือไม่ (ทั้งในฐานข้อมูลและในเซสชันนี้)
                        if (
                            check_ring_used(farm_id, original_ring)
                            or original_ring in used_rings_in_session
                        ):
                            # หาหมายเลขห่วงขาใหม่ที่ไม่ซ้ำ
                            new_ring = get_available_ring_number(
                                farm_id, used_rings_in_session
                            )
                            if new_ring is None:
                                # ไม่มีห่วงขาเหลือ
                                ring_changes.append(
                                    {
                                        "rat_id": rat_id,
                                        "row": index + 2,
                                        "original_ring": original_ring,
                                        "new_ring": None,
                                        "reason": "ห่วงขาเต็มแล้ว",
                                        "action": "ยกเลิกการใส่ห่วงขา",
                                        "type": "cancel",
                                    }
                                )
                            else:
                                ring_changes.append(
                                    {
                                        "rat_id": rat_id,
                                        "row": index + 2,
                                        "original_ring": original_ring,
                                        "new_ring": new_ring,
                                        "reason": f"หมายเลข {original_ring} ถูกใช้แล้ว{' (ในไฟล์นี้)' if original_ring in used_rings_in_session else ''}",
                                        "action": f"เปลี่ยนเป็น {new_ring}",
                                        "type": "change",
                                    }
                                )
                                # *** เพิ่มหมายเลขใหม่เข้าใน set เพื่อไม่ให้ซ้ำ ***
                                used_rings_in_session.add(new_ring)
                        else:
                            # หมายเลขห่วงขาว่าง ใช้ได้
                            used_rings_in_session.add(original_ring)
                    else:
                        # ไม่ได้ระบุหมายเลขห่วงขา หาหมายเลขใหม่
                        new_ring = get_available_ring_number(
                            farm_id, used_rings_in_session
                        )
                        if new_ring is None:
                            ring_changes.append(
                                {
                                    "rat_id": rat_id,
                                    "row": index + 2,
                                    "original_ring": None,
                                    "new_ring": None,
                                    "reason": "ห่วงขาเต็มแล้ว",
                                    "action": "ยกเลิกการใส่ห่วงขา",
                                    "type": "cancel",
                                }
                            )
                        else:
                            ring_changes.append(
                                {
                                    "rat_id": rat_id,
                                    "row": index + 2,
                                    "original_ring": None,
                                    "new_ring": new_ring,
                                    "reason": "ไม่ได้ระบุหมายเลขห่วงขา",
                                    "action": f"กำหนดหมายเลข {new_ring}",
                                    "type": "assign",
                                }
                            )
                            # *** เพิ่มหมายเลขใหม่เข้าใน set ***
                            used_rings_in_session.add(new_ring)

            except Exception as e:
                errors.append(
                    {
                        "row": index + 2,
                        "rat_id": row.get("rat_id", "ไม่ระบุ"),
                        "error": str(e),
                    }
                )

        # สรุปผลการวิเคราะห์
        success_changes = len(
            [c for c in ring_changes if c.get("new_ring") is not None]
        )
        cancelled_changes = len(ring_changes) - success_changes

        summary = {
            "total_rats": total_rats,
            "duplicate_rats": len(duplicate_rats),
            "ring_changes": len(ring_changes),
            "success_changes": success_changes,
            "cancelled_changes": cancelled_changes,
            "errors": len(errors),
            "importable_rats": total_rats - len(duplicate_rats) - len(errors),
            "used_rings_count": len(used_rings_in_session),  # เพิ่มจำนวนห่วงขาที่จะใช้
        }

        return {
            "success": True,
            "message": "วิเคราะห์ไฟล์สำเร็จ",
            "details": {
                "summary": summary,
                "ring_changes": ring_changes,
                "duplicate_rats": duplicate_rats,
                "errors": errors,
                "csv_data": df.to_dict("records"),  # ข้อมูล CSV สำหรับแสดงผล
                "used_rings_preview": sorted(
                    list(used_rings_in_session)
                ),  # แสดงหมายเลขห่วงขาที่จะใช้
            },
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"เกิดข้อผิดพลาดในการวิเคราะห์ไฟล์: {str(e)}",
            "details": None,
        }
