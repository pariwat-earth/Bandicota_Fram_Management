import sqlite3
from datetime import date, datetime
from pathlib import Path
import csv


def adapt_datetime(val: datetime) -> str:
    """แปลง datetime เป็น string format ที่ SQLite เข้าใจ"""
    return val.strftime("%Y-%m-%d %H:%M:%S")


def convert_datetime(val: bytes) -> datetime:
    """แปลง string จาก SQLite เป็น datetime object"""
    return datetime.strptime(val.decode(), "%Y-%m-%d %H:%M:%S")


def get_connection():
    try:
        # หา path ของโฟลเดอร์ปัจจุบัน
        current_dir = Path.cwd() / "src/storages"
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        current_dir.mkdir(parents=True, exist_ok=True)

        # สร้าง path ไปยังไฟล์ฐานข้อมูล
        db_path = current_dir / "bendicota_DB_farm.db"

        sqlite3.register_adapter(datetime, adapt_datetime)
        sqlite3.register_converter("datetime", convert_datetime)

        conn = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            timeout=20,
        )
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    except Exception as e:
        print(f"ไม่สามารถเชื่อมต่อกับฐานข้อมูลได้: {str(e)}")
        raise


# นำเข้าฟาร์ม
def add_farms_data(farms):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO farm (
                farm_name, 
                location, 
                latitude, 
                longtitude, 
                ponds_amount, 
                ring_amount, 
                manager_name, 
                start_date, 
                farm_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            farms,
        )

        conn.commit()
        return True

    except sqlite3.Error as e:
        conn.rollback()
        return False

    finally:
        conn.close()


def get_ponds_use(farm_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ดึงข้อมูลจำนวนบ่อที่ใช้งานอยู่
        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM pond 
            WHERE farm_id = ? AND status != 'empty'
        """,
            (farm_id,),
        )

        ponds_use = cursor.fetchone()[0]
        return ponds_use

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลบ่อที่ใช้งาน: {e}")
        return 0

    finally:
        conn.close()


def get_all_farm():
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row  # ตั้งค่าให้ผลลัพธ์เป็น dict-like object
        cursor = conn.cursor()

        # ดึงข้อมูลทั้งหมดจากตาราง farm เรียงตามชื่อฟาร์ม
        cursor.execute(
            """
            SELECT 
                farm_id, 
                farm_name, 
                location, 
                latitude, 
                longtitude, 
                ponds_amount, 
                ring_amount, 
                manager_name, 
                start_date, 
                farm_type
            FROM farm
            ORDER BY farm_id
        """
        )

        # ดึงผลลัพธ์ทั้งหมด
        rows = cursor.fetchall()

        # แปลงผลลัพธ์เป็น list ของ dict
        farms = []
        for row in rows:
            farm = {
                "farm_id": row["farm_id"],
                "farm_name": row["farm_name"],
                "location": row["location"],
                "latitude": row["latitude"],
                "longitude": row["longtitude"],  # แก้ชื่อให้ถูกต้องตามมาตรฐาน
                "ponds_amount": row["ponds_amount"],
                "ponds_use": get_ponds_use(row["farm_id"]),
                "ring_amount": row["ring_amount"],
                "manager_name": row["manager_name"],
                "start_date": row["start_date"],
                "farm_type": row["farm_type"],
                "farm_type_thai": (
                    "ฟาร์มหลัก" if row["farm_type"] == "main" else "ฟาร์มเครือข่าย"
                ),
            }
            farms.append(farm)

        return farms

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลฟาร์ม: {e}")
        return []

    finally:
        conn.close()


def get_farm_by_farm_id(farm_id):
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # ดึงข้อมูลฟาร์มตาม farm_id
        cursor.execute(
            """
            SELECT 
                farm_id, 
                farm_name, 
                location, 
                latitude, 
                longtitude, 
                ponds_amount, 
                ring_amount, 
                manager_name, 
                start_date, 
                farm_type
            FROM farm
            WHERE farm_id = ?
        """,
            (farm_id,),
        )

        # ดึงผลลัพธ์
        row = cursor.fetchone()

        # ถ้าไม่พบข้อมูล
        if row is None:
            return None

        # แปลงผลลัพธ์เป็น dict
        farm = {
            "farm_id": row["farm_id"],
            "farm_name": row["farm_name"],
            "location": row["location"],
            "latitude": row["latitude"],
            "longitude": row["longtitude"],
            "ponds_amount": row["ponds_amount"],
            "ponds_use": get_ponds_use(row["farm_id"]),
            "ring_amount": row["ring_amount"],
            "manager_name": row["manager_name"],
            "start_date": row["start_date"],
            "farm_type": row["farm_type"],
            "farm_type_thai": (
                "ฟาร์มหลัก" if row["farm_type"] == "main" else "ฟาร์มเครือข่าย"
            ),
        }

        return farm

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลฟาร์ม: {e}")
        return None

    finally:
        conn.close()


def update_farm_by_farm_id(farm_id, farms):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        update_query = """
            UPDATE farm SET
                farm_name = ?,
                location = ?,
                latitude = ?,
                longtitude = ?,
                ponds_amount = ?,
                ring_amount = ?,
                manager_name = ?,
                start_date = ?,
                farm_type = ?
            WHERE farm_id = ?
        """

        params = farms + (farm_id,)

        cursor.execute(update_query, params)

        conn.commit()
        return True

    except sqlite3.Error as e:
        conn.rollback()
        return False

    finally:
        conn.close()


def delete_farm_by_farm_id(farm_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        delete_query = "DELETE FROM farm WHERE farm_id = ?"

        cursor.execute(delete_query, (farm_id,))

        conn.commit()
        return True

    except sqlite3.Error as e:
        conn.rollback()
        return False

    finally:
        conn.close()


def add_number_pond(farm_id, num_pond):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # หา pond_index สูงสุดในฟาร์มนี้
        cursor.execute(
            "SELECT MAX(pond_index) FROM pond WHERE farm_id = ?", 
            (farm_id,)
        )
        max_index = cursor.fetchone()[0] or 0  # ถ้าไม่มีให้เป็น 0
        
        ponds = []
        update_date = date.today()
        
        for i in range(num_pond):
            new_index = max_index + i + 1  # เริ่มจากถัดไป
            pond = (new_index, farm_id, f"บ่อ{new_index}", "empty", update_date)
            ponds.append(pond)
        
        cursor.executemany(
            "INSERT INTO pond (pond_index, farm_id, pond_name, status, update_date) VALUES (?, ?, ?, ?, ?)",
            ponds
        )
        
        conn.commit()
        return True
        
    except sqlite3.Error as e:
        conn.rollback()
        return False
    finally:
        conn.close()


def delete_empty_ponds(farm_id, count_to_delete):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        select_query = """
            SELECT pond_id FROM pond 
            WHERE farm_id = ? AND status = 'empty' 
            ORDER BY pond_id DESC
            LIMIT ?
        """

        cursor.execute(select_query, (farm_id, count_to_delete))
        pond_ids = [row[0] for row in cursor.fetchall()]

        if pond_ids:
            placeholders = ",".join(["?"] * len(pond_ids))

            delete_query = f"""
                DELETE FROM pond 
                WHERE pond_id IN ({placeholders})
            """

            cursor.execute(delete_query, pond_ids)

        # บันทึกการเปลี่ยนแปลง
        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Error in delete_empty_ponds: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def get_pond_count_by_farm_id(farm_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        count_query = "SELECT COUNT(*) FROM pond WHERE farm_id = ?"

        cursor.execute(count_query, (farm_id,))

        pond_count = cursor.fetchone()[0]

        return pond_count

    except sqlite3.Error as e:
        print(f"Error in get_pond_count_by_farm_id: {e}")
        return 0

    finally:
        conn.close()


def get_empty_pond_by_farm_id():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT pond_id 
            FROM pond 
            WHERE status = 'empty' AND farm_id = (SELECT farm_id FROM farm WHERE farm_type = 'main')
            ORDER BY pond_id 
            LIMIT 1
        """
        )

        empty_pond = cursor.fetchone()
        pond_id = empty_pond[0]

        return pond_id

    except sqlite3.Error as e:
        print(f"Error in get_empty_pond_by_farm_id: {e}")
        return []

    finally:
        conn.close()


def get_last_inserted_farm_id():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT MAX(farm_id) FROM farm"

        cursor.execute(query)

        farm_id = cursor.fetchone()[0]

        return farm_id

    except sqlite3.Error as e:
        print(f"Error in get_last_inserted_farm_id: {e}")
        return None

    finally:
        conn.close()


def get_ponds_by_farm_id(farm_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT * FROM pond
        WHERE farm_id = ?
        ORDER BY pond_name
        """

        cursor.execute(query, (farm_id,))

        ponds = []
        column_names = [description[0] for description in cursor.description]

        for row in cursor.fetchall():
            pond = dict(zip(column_names, row))
            ponds.append(pond)

        return ponds

    except sqlite3.Error as e:
        print(f"Error in get_ponds_by_farm_id: {e}")
        return []

    finally:
        conn.close()


def update_selected_farm_id(farm_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ตรวจสอบว่ามีตาราง selected_farm หรือไม่
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS selected_farm (
                id INTEGER PRIMARY KEY,
                farm_id INTEGER
            )
        """
        )

        # ตรวจสอบว่ามีข้อมูลในตารางหรือไม่
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


def get_selected_farm_id():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ตรวจสอบว่ามีตาราง selected_farm หรือไม่
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS selected_farm (
                id INTEGER PRIMARY KEY,
                farm_id INTEGER
            )
        """
        )

        # ดึงข้อมูล farm_id
        cursor.execute("SELECT farm_id FROM selected_farm WHERE id = 1")
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    except sqlite3.Error as e:
        print(f"Error in get_selected_farm_id: {e}")
        return None

    finally:
        conn.close()


def update_pond_status(farm_id, pond_id, new_status):
    try:
        if new_status not in ["empty", "work", "maintenance"]:
            return False

        # เชื่อมต่อกับฐานข้อมูล
        conn = get_connection()
        cursor = conn.cursor()

        today = date.today().isoformat()

        cursor.execute(
            "UPDATE pond SET status = ?, update_date = ? WHERE pond_id = ? AND farm_id = ?",
            (new_status, today, pond_id, farm_id),
        )

        rows_affected = cursor.rowcount

        conn.commit()

        return rows_affected > 0

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()


def get_rats_by_farm_and_pond(farm_id, pond_id):
    """
    ตรวจสอบหนูที่ใช้งานอยู่ในบ่อของฟาร์มที่ระบุ

    Args:
        farm_id (int): รหัสฟาร์ม
        pond_id (int): รหัสบ่อ

    Returns:
        dict: {'father_ring_number': int, 'mother_ring_number': int} หรือ None ถ้าไม่พบ
    """
    from storages.database_service import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT ring_number, gender
            FROM rat 
            WHERE farm_id = ? 
            AND pond_id = ?
            AND ring_number IS NOT NULL
            ORDER BY gender DESC
        """,
            (farm_id, pond_id),
        )

        result = cursor.fetchall()

        father_ring_number = None
        mother_ring_number = None

        for ring_number, gender in result:
            if gender == "male" and father_ring_number is None:
                father_ring_number = ring_number
            elif gender == "female" and mother_ring_number is None:
                mother_ring_number = ring_number

        return {
            "father_ring_number": father_ring_number,
            "mother_ring_number": mother_ring_number,
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"father_ring_number": None, "mother_ring_number": None}

    finally:
        conn.close()


def get_all_rat_data():
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # ดึงข้อมูลทั้งหมดจากตาราง rat
        cursor.execute(
            """
            SELECT 
                rat_id, 
                father_id, 
                mother_id, 
                birth_date, 
                gender, 
                weight, 
                size, 
                breed, 
                status, 
                pond_id, 
                farm_id, 
                has_ring, 
                ring_number, 
                special_traits
            FROM rat
            WHERE status != 'dispose'
            ORDER BY ring_number desc
            """
        )

        # ดึงผลลัพธ์ทั้งหมด
        rows = cursor.fetchall()

        rats = []
        for row in rows:
            # แปลงสถานะเป็นภาษาไทย
            status_thai = ""
            if row["status"] == "breeder1":
                status_thai = "กำลังผสม"
            elif row["status"] == "breeder2":
                status_thai = "พร้อมผสม"
            elif row["status"] == "fertilize":
                status_thai = "ขุน"
            elif row["status"] == "dispose":
                status_thai = "จำหน่าย"

            # แปลงเพศเป็นภาษาไทย
            gender_thai = "ผู้" if row["gender"] == "male" else "เมีย"

            rat = {
                "rat_id": row["rat_id"],
                "father_id": row["father_id"],
                "mother_id": row["mother_id"],
                "birth_date": row["birth_date"],
                "gender": row["gender"],
                "gender_thai": gender_thai,
                "weight": row["weight"],
                "size": row["size"],
                "breed": row["breed"],
                "status": row["status"],
                "status_thai": status_thai,
                "pond_id": row["pond_id"],
                "farm_id": row["farm_id"],
                "has_ring": row["has_ring"],
                "ring_number": row["ring_number"],
                "special_traits": row["special_traits"],
            }
            rats.append(rat)

        return rats

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลหนู: {e}")
        return []

    finally:
        conn.close()


def get_rat_by_rat_id(rat_id):
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # ดึงข้อมูลหนูตาม rat_id
        cursor.execute(
            """
            SELECT 
                rat_id, 
                father_id, 
                mother_id, 
                birth_date, 
                gender, 
                weight, 
                size, 
                breed, 
                status, 
                pond_id, 
                farm_id, 
                has_ring, 
                ring_number, 
                special_traits
            FROM rat
            WHERE rat_id = ?
            """,
            (rat_id,),
        )

        # ดึงผลลัพธ์
        row = cursor.fetchone()

        # ถ้าไม่พบข้อมูล
        if row is None:
            return None

        # แปลงสถานะเป็นภาษาไทย
        status_thai = ""
        if row["status"] == "breeder1":
            status_thai = "กำลังผสม"
        elif row["status"] == "breeder2":
            status_thai = "พร้อมผสม"
        elif row["status"] == "fertilize":
            status_thai = "ขุน"
        elif row["status"] == "dispose":
            status_thai = "จำหน่าย"

        # แปลงเพศเป็นภาษาไทย
        gender_thai = "ผู้" if row["gender"] == "male" else "เมีย"

        # แปลงผลลัพธ์เป็น dict
        rat = {
            "rat_id": row["rat_id"],
            "father_id": row["father_id"],
            "mother_id": row["mother_id"],
            "birth_date": row["birth_date"],
            "gender": row["gender"],
            "gender_thai": gender_thai,
            "weight": row["weight"],
            "size": row["size"],
            "breed": row["breed"],
            "status": row["status"],
            "status_thai": status_thai,
            "pond_id": row["pond_id"],
            "farm_id": row["farm_id"],
            "has_ring": row["has_ring"],
            "ring_number": row["ring_number"],
            "special_traits": row["special_traits"],
        }

        return rat

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลหนู: {e}")
        return None

    finally:
        conn.close()


def add_rat_information(rat_data):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO rat (
                rat_id, 
                father_id, 
                mother_id, 
                birth_date, 
                gender, 
                weight, 
                size, 
                breed, 
                status, 
                pond_id, 
                farm_id, 
                has_ring, 
                ring_number, 
                special_traits
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rat_data,
        )

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการเพิ่มข้อมูลหนู: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def update_rat_by_rat_id(rat_id, rat_data):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        update_query = """
            UPDATE rat SET
                father_id = ?,
                mother_id = ?,
                birth_date = ?,
                gender = ?,
                weight = ?,
                size = ?,
                breed = ?,
                status = ?,
                pond_id = ?,
                farm_id = ?,
                has_ring = ?,
                ring_number = ?,
                special_traits = ?
            WHERE rat_id = ?
        """

        # ตัด rat_id (ตำแหน่งแรก) ออกจาก rat_data และเพิ่ม rat_id กลับเข้าไปที่ท้าย
        fixed_params = rat_data[1:] + (rat_id,)

        cursor.execute(update_query, fixed_params)

        conn.commit()
        return True
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอัปเดตข้อมูลหนู: {e}")
        return False

    finally:
        conn.close()


def delete_rat_by_rat_id(rat_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        delete_query = "DELETE FROM rat WHERE rat_id = ?"

        cursor.execute(delete_query, (rat_id,))

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการลบข้อมูลหนู: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def get_rats_by_farm_id(farm_id):
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # ดึงข้อมูลหนูตาม farm_id
        cursor.execute(
            """
            SELECT 
                rat_id, 
                father_id, 
                mother_id, 
                birth_date, 
                gender, 
                weight, 
                size, 
                breed, 
                status, 
                pond_id, 
                farm_id, 
                has_ring, 
                ring_number, 
                special_traits
            FROM rat
            WHERE farm_id = ?
            ORDER BY rat_id
            """,
            (farm_id,),
        )

        # ดึงผลลัพธ์ทั้งหมด
        rows = cursor.fetchall()

        # แปลงผลลัพธ์เป็น list ของ dict
        rats = []
        for row in rows:
            # แปลงสถานะเป็นภาษาไทย
            status_thai = ""
            if row["status"] == "breeder1":
                status_thai = "กำลังผสม"
            elif row["status"] == "breeder2":
                status_thai = "พร้อมผสม"
            elif row["status"] == "fertilize":
                status_thai = "ขุน"
            elif row["status"] == "dispose":
                status_thai = "จำหน่าย"

            # แปลงเพศเป็นภาษาไทย
            gender_thai = "ผู้" if row["gender"] == "male" else "เมีย"

            rat = {
                "rat_id": row["rat_id"],
                "father_id": row["father_id"],
                "mother_id": row["mother_id"],
                "birth_date": row["birth_date"],
                "gender": row["gender"],
                "gender_thai": gender_thai,
                "weight": row["weight"],
                "size": row["size"],
                "breed": row["breed"],
                "status": row["status"],
                "status_thai": status_thai,
                "pond_id": row["pond_id"],
                "farm_id": row["farm_id"],
                "has_ring": row["has_ring"],
                "ring_number": row["ring_number"],
                "special_traits": row["special_traits"],
            }
            rats.append(rat)

        return rats

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลหนู: {e}")
        return []

    finally:
        conn.close()


def get_rats_by_pond_id(pond_id, farm_id=None):
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT 
                rat_id, 
                father_id, 
                mother_id, 
                birth_date, 
                gender, 
                weight, 
                size, 
                breed, 
                status, 
                pond_id, 
                farm_id, 
                has_ring, 
                ring_number, 
                special_traits
            FROM rat
            WHERE pond_id = ?
        """

        params = [pond_id]

        # ถ้ามีการระบุ farm_id
        if farm_id is not None:
            query += " AND farm_id = ?"
            params.append(farm_id)

        query += " ORDER BY rat_id"

        # ดึงข้อมูลหนูตาม pond_id
        cursor.execute(query, params)

        # ดึงผลลัพธ์ทั้งหมด
        rows = cursor.fetchall()

        # แปลงผลลัพธ์เป็น list ของ dict
        rats = []
        for row in rows:
            # แปลงสถานะเป็นภาษาไทย
            status_thai = ""
            if row["status"] == "breeder1":
                status_thai = "กำลังผสม"
            elif row["status"] == "breeder2":
                status_thai = "พร้อมผสม"
            elif row["status"] == "fertilize":
                status_thai = "ขุน"
            elif row["status"] == "dispose":
                status_thai = "จำหน่าย"

            # แปลงเพศเป็นภาษาไทย
            gender_thai = "ผู้" if row["gender"] == "male" else "เมีย"

            rat = {
                "rat_id": row["rat_id"],
                "father_id": row["father_id"],
                "mother_id": row["mother_id"],
                "birth_date": row["birth_date"],
                "gender": row["gender"],
                "gender_thai": gender_thai,
                "weight": row["weight"],
                "size": row["size"],
                "breed": row["breed"],
                "status": row["status"],
                "status_thai": status_thai,
                "pond_id": row["pond_id"],
                "farm_id": row["farm_id"],
                "has_ring": row["has_ring"],
                "ring_number": row["ring_number"],
                "special_traits": row["special_traits"],
            }
            rats.append(rat)

        return rats

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลหนูตามบ่อ: {e}")
        return []

    finally:
        conn.close()


def get_rats_by_status(status, farm_id=None):
    try:
        # ตรวจสอบว่าสถานะถูกต้อง
        if status not in ["breeder1", "breeder2", "fertilize", "dispose"]:
            print(f"สถานะไม่ถูกต้อง: {status}")
            return []

        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT 
                rat_id, 
                father_id, 
                mother_id, 
                birth_date, 
                gender, 
                weight, 
                size, 
                breed, 
                status, 
                pond_id, 
                farm_id, 
                has_ring, 
                ring_number, 
                special_traits
            FROM rat
            WHERE status = ?
        """

        params = [status]

        # ถ้ามีการระบุ farm_id
        if farm_id is not None:
            query += " AND farm_id = ?"
            params.append(farm_id)

        query += " ORDER BY rat_id"

        # ดึงข้อมูลหนูตามสถานะ
        cursor.execute(query, params)

        # ดึงผลลัพธ์ทั้งหมด
        rows = cursor.fetchall()

        # แปลงสถานะเป็นภาษาไทย
        status_thai = ""
        if status == "breeder1":
            status_thai = "กำลังผสม"
        elif status == "breeder2":
            status_thai = "พร้อมผสม"
        elif status == "fertilize":
            status_thai = "ขุน"
        elif status == "dispose":
            status_thai = "จำหน่าย"

        # แปลงผลลัพธ์เป็น list ของ dict
        rats = []
        for row in rows:
            # แปลงเพศเป็นภาษาไทย
            gender_thai = "ผู้" if row["gender"] == "male" else "เมีย"

            rat = {
                "rat_id": row["rat_id"],
                "father_id": row["father_id"],
                "mother_id": row["mother_id"],
                "birth_date": row["birth_date"],
                "gender": row["gender"],
                "gender_thai": gender_thai,
                "weight": row["weight"],
                "size": row["size"],
                "breed": row["breed"],
                "status": row["status"],
                "status_thai": status_thai,
                "pond_id": row["pond_id"],
                "farm_id": row["farm_id"],
                "has_ring": row["has_ring"],
                "ring_number": row["ring_number"],
                "special_traits": row["special_traits"],
            }
            rats.append(rat)

        return rats

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลหนูตามสถานะ: {e}")
        return []

    finally:
        conn.close()


def update_rat_status(rat_id, new_status):
    try:
        # ตรวจสอบว่าสถานะถูกต้อง
        if new_status not in ["breeder1", "breeder2", "fertilize", "dispose"]:
            print(f"สถานะไม่ถูกต้อง: {new_status}")
            return False

        conn = get_connection()
        cursor = conn.cursor()

        update_query = """
            UPDATE rat
            SET status = ?
            WHERE rat_id = ?
        """

        cursor.execute(update_query, (new_status, rat_id))

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการอัปเดตสถานะหนู: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def update_rat_pond(rat_id, pond_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        update_query = """
            UPDATE rat
            SET pond_id = ?
            WHERE rat_id = ?
        """

        cursor.execute(update_query, (pond_id, rat_id))

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการอัปเดตบ่อของหนู: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def get_rat_id_by_ring_number(ring_number):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT rat_id FROM rat WHERE ring_number = ?"
        cursor.execute(query, (ring_number,))

        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None

    except sqlite3.Error as e:
        print(f"Error in get_rat_id_by_ring_number: {e}")
        return None

    finally:
        conn.close()


def add_breed_data(breed_data):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO breeding (
                father_id, 
                mother_id, 
                pond_id,
                inbreeding_rate,
                breeding_status,
                breeding_date
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            breed_data,
        )

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการเพิ่มข้อมูลการผสมพันธุ์: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def get_breed_information():
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                breeding_id, 
                father_id, 
                mother_id, 
                pond_id, 
                inbreeding_rate, 
                breeding_status, 
                breeding_date
            FROM breeding
            WHERE breeding_status = 'breeding'
            ORDER BY breeding_id desc
            """
        )

        rows = cursor.fetchall()

        breeds = []
        for row in rows:
            breed = {
                "breeding_id": row["breeding_id"],
                "father_ring_id": get_rat_by_rat_id(row["father_id"])["ring_number"],
                "mother_ring_id": get_rat_by_rat_id(row["mother_id"])["ring_number"],
                "pond_id": row["pond_id"],
                "inbreeding_rate": round(row["inbreeding_rate"], 2),
                "breeding_status": row["breeding_status"],
                "breeding_date": row["breeding_date"],
            }
            breeds.append(breed)

        return breeds

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลการผสมพันธุ์: {e}")
        return []

    finally:
        conn.close()


def get_breed_by_breeding_id(breeding_id):
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                breeding_id, 
                father_id, 
                mother_id, 
                pond_id, 
                inbreeding_rate, 
                breeding_status, 
                breeding_date
            FROM breeding
            WHERE breeding_id = ?
            """,
            (breeding_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        breed = {
            "breeding_id": row["breeding_id"],
            "father_ring_id": get_rat_by_rat_id(row["father_id"])["ring_number"],
            "mother_ring_id": get_rat_by_rat_id(row["mother_id"])["ring_number"],
            "pond_id": row["pond_id"],
            "inbreeding_rate": row["inbreeding_rate"],
            "breeding_status": row["breeding_status"],
            "breeding_date": row["breeding_date"],
        }

        return breed

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลการผสมพันธุ์: {e}")
        return None

    finally:
        conn.close()


def get_breeding_by_date(start_date, end_date):
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                breeding_id, 
                father_id, 
                mother_id, 
                pond_id, 
                inbreeding_rate, 
                breeding_status, 
                breeding_date
            FROM breeding
            WHERE breeding_date BETWEEN ? AND ?
            ORDER BY breeding_date
            """,
            (start_date, end_date),
        )

        rows = cursor.fetchall()

        breeds = []
        for row in rows:
            breed = {
                "breeding_id": row["breeding_id"],
                "father_ring_id": get_rat_by_rat_id(row["father_id"])["ring_number"],
                "mother_ring_id": get_rat_by_rat_id(row["mother_id"])["ring_number"],
                "pond_id": row["pond_id"],
                "inbreeding_rate": round(row["inbreeding_rate"], 2),
                "breeding_status": row["breeding_status"],
                "breeding_date": row["breeding_date"],
            }
            breeds.append(breed)

        return breeds

    except sqlite3.Error as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลการผสมพันธุ์: {e}")
        return []

    finally:
        conn.close()


def update_breed_data(breeding_data):
    """อัพเดทข้อมูลการผสมพันธุ์ในฐานข้อมูล"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # สร้าง SQL สำหรับอัพเดท
        sql = """
            UPDATE breeding SET
                father_id = ?,
                mother_id = ?,
                pond_id = ?,
                inbreeding_rate = ?,
                breeding_status = ?,
                breeding_date = ?
        """

        params = [
            breeding_data["father_id"],
            breeding_data["mother_id"],
            breeding_data["pond_id"],
            breeding_data["inbreeding_rate"],
            breeding_data["breeding_status"],
            breeding_data["breeding_date"],
        ]

        # เพิ่มข้อมูลการคลอดถ้ามี
        if "survived_pups" in breeding_data:
            sql += """
                , birth_date = ?,
                total_pups = ?,
                survived_pups = ?,
                albino_pups = ?,
                separation_date = ?
            """
            params.extend(
                [
                    breeding_data.get("birth_date"),
                    breeding_data.get("total_pups"),
                    breeding_data.get("survived_pups"),
                    breeding_data.get("albino_pups"),
                    breeding_data.get("separation_date"),
                ]
            )

        sql += " WHERE breeding_id = ?"
        params.append(breeding_data["breeding_id"])

        cursor.execute(sql, params)
        conn.commit()

        return True

    except Exception as e:
        print(f"Error updating breeding data: {e}")
        if conn:
            conn.rollback()
        return False

    finally:
        if conn:
            conn.close()


def check_breed_exists(ring_number):
    """ตรวจสอบว่ามีการผสมพันธุ์ที่เกี่ยวข้องกับ ring_number นี้หรือไม่"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT COUNT(*) FROM breeding
            WHERE father_id IN (SELECT rat_id FROM rat WHERE ring_number = ?)
            OR mother_id IN (SELECT rat_id FROM rat WHERE ring_number = ?)
        """

        cursor.execute(query, (ring_number, ring_number))
        count = cursor.fetchone()[0]

        return count > 0

    except sqlite3.Error as e:
        print(f"Error checking breeding existence: {e}")
        return False

    finally:
        conn.close()


def auto_manage_breeding_after_success(father_id, mother_id, current_pond_id):
    """
    ฟังก์ชันจัดการอัตโนมัติหลังจากบันทึกการผสมสำเร็จ

    Args:
        father_id: รหัสหนูพ่อพันธุ์
        mother_id: รหัสหนูแม่พันธุ์
        current_pond_id: รหัสบ่อปัจจุบัน

    Returns:
        dict: ผลลัพธ์การดำเนินการ
    """
    from storages.database_service import get_connection
    from datetime import date

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1. ตรวจสอบจำนวนครั้งที่หนูคู่นี้ผสมสำเร็จ
        cursor.execute(
            """
            SELECT COUNT(*) as success_count
            FROM breeding 
            WHERE father_id = ? AND mother_id = ? 
            AND breeding_status = 'success'
        """,
            (father_id, mother_id),
        )

        success_count = cursor.fetchone()[0]
        print(f"หนูคู่นี้ผสมสำเร็จแล้ว {success_count} ครั้ง")

        if success_count <= 6:
            # กรณีที่ยังไม่เกิน 6 ครั้ง - สร้างการผสมใหม่
            result = create_new_breeding_cycle(
                cursor, father_id, mother_id, current_pond_id
            )
            conn.commit()
            return {
                "action": "new_breeding",
                "success": result["success"],
                "message": f"สร้างการผสมรอบใหม่สำเร็จ (รอบที่ {success_count + 1})",
                "details": result,
            }
        else:
            # กรณีที่เกิน 6 ครั้ง - เปลี่ยนเป็นหนูขุน
            result = retire_breeding_pair(cursor, father_id, mother_id, current_pond_id)
            conn.commit()
            return {
                "action": "retire_pair",
                "success": result["success"],
                "message": f"หนูคู่นี้ผสมครบ {success_count} ครั้งแล้ว เปลี่ยนเป็นหนูขุน",
                "details": result,
            }

    except Exception as e:
        print(f"Error in auto_manage_breeding_after_success: {e}")
        conn.rollback()
        return {
            "action": "error",
            "success": False,
            "message": f"เกิดข้อผิดพลาด: {str(e)}",
            "details": {},
        }
    finally:
        conn.close()


def create_new_breeding_cycle(cursor, father_id, mother_id, current_pond_id):
    """
    สร้างรอบการผสมใหม่สำหรับหนูคู่เดิม

    Args:
        cursor: database cursor
        father_id: รหัสหนูพ่อพันธุ์
        mother_id: รหัสหนูแม่พันธุ์
        current_pond_id: รหัสบ่อปัจจุบัน

    Returns:
        dict: ผลลัพธ์การสร้างการผสมใหม่
    """
    from datetime import date
    from main_calculate.advice_breed import calculate_inbreeding_coefficient

    try:
        # 1. คำนวณค่า inbreeding coefficient
        inbreeding_rate = calculate_inbreeding_coefficient(father_id, mother_id)

        # 2. ตรวจสอบว่าค่า inbreeding ยังอยู่ในเกณฑ์ปลอดภัยหรือไม่
        if inbreeding_rate > 0.0625:  # > 6.25%
            return {
                "success": False,
                "message": f"หนูคู่นี้มีอัตราเลือดชิดสูงเกินไป ({inbreeding_rate*100:.2f}%) ไม่สามารถผสมต่อได้",
                "pond_freed": False,
            }

        # 3. สร้างข้อมูลการผสมใหม่
        today = date.today()
        cursor.execute(
            """
            INSERT INTO breeding (
                father_id,
                mother_id,
                breeding_date,
                pond_id,
                inbreeding_rate,
                breeding_status
            ) VALUES (?, ?, ?, ?, ?, 'breeding')
        """,
            (father_id, mother_id, today, current_pond_id, inbreeding_rate),
        )

        new_breeding_id = cursor.lastrowid

        # 4. อัพเดทสถานะหนูเป็น 'breeder1' (กำลังผสม)
        cursor.execute(
            """
            UPDATE rat 
            SET status = 'breeder1', pond_id = ?
            WHERE rat_id IN (?, ?)
        """,
            (current_pond_id, father_id, mother_id),
        )

        # 5. อัพเดทสถานะบ่อเป็น 'work'
        cursor.execute(
            """
            UPDATE pond 
            SET status = 'work', update_date = ?
            WHERE pond_id = ?
        """,
            (today, current_pond_id),
        )

        return {
            "success": True,
            "message": "สร้างรอบการผสมใหม่สำเร็จ",
            "new_breeding_id": new_breeding_id,
            "inbreeding_rate": inbreeding_rate,
            "pond_freed": False,
        }

    except Exception as e:
        print(f"Error creating new breeding cycle: {e}")
        return {
            "success": False,
            "message": f"ไม่สามารถสร้างการผสมใหม่ได้: {str(e)}",
            "pond_freed": False,
        }


def retire_breeding_pair(cursor, father_id, mother_id, current_pond_id):
    """
    เปลี่ยนหนูคู่ผสมเป็นหนูขุนเมื่อผสมครบ 6 ครั้ง

    Args:
        cursor: database cursor
        father_id: รหัสหนูพ่อพันธุ์
        mother_id: รหัสหนูแม่พันธุ์
        current_pond_id: รหัสบ่อปัจจุบัน

    Returns:
        dict: ผลลัพธ์การเปลี่ยนสถานะ
    """
    from datetime import date

    try:
        today = date.today()

        # 1. หาบ่อว่างสำหรับหนูขุน
        cursor.execute(
            """
            SELECT pond_id 
            FROM pond 
            WHERE status = 'empty' 
            ORDER BY pond_id 
            LIMIT 2
        """
        )
        empty_ponds = cursor.fetchall()

        if len(empty_ponds) < 2:
            # ถ้าไม่มีบ่อว่างพอ ให้ใช้บ่อเดิม
            father_pond = current_pond_id
            mother_pond = current_pond_id
            pond_message = "ใช้บ่อเดิมเนื่องจากไม่มีบ่อว่างเพียงพอ"
        else:
            father_pond = empty_ponds[0][0]
            mother_pond = empty_ponds[1][0]
            pond_message = f"ย้ายไปบ่อใหม่ (บ่อ {father_pond}, {mother_pond})"

        # 2. อัพเดทสถานะหนูเป็น 'fertilize' (ขุน)
        cursor.execute(
            """
            UPDATE rat 
            SET status = 'fertilize', pond_id = ?
            WHERE rat_id = ?
        """,
            (father_pond, father_id),
        )

        cursor.execute(
            """
            UPDATE rat 
            SET status = 'fertilize', pond_id = ?
            WHERE rat_id = ?
        """,
            (mother_pond, mother_id),
        )

        # 3. อัพเดทบ่อที่ใช้สำหรับหนูขุน
        if len(empty_ponds) >= 2:
            cursor.execute(
                """
                UPDATE pond 
                SET status = 'work', update_date = ?
                WHERE pond_id IN (?, ?)
            """,
                (today, father_pond, mother_pond),
            )

        # 4. ปลดปล่อยบ่อเดิม (ถ้าหนูย้ายไปบ่อใหม่)
        if len(empty_ponds) >= 2:
            cursor.execute(
                """
                UPDATE pond 
                SET status = 'empty', update_date = ?
                WHERE pond_id = ?
            """,
                (today, current_pond_id),
            )
            pond_freed = True
        else:
            pond_freed = False

        # 5. ดึงข้อมูลหนูเพื่อแสดงผล
        cursor.execute(
            """
            SELECT r.rat_id, r.ring_number
            FROM rat r
            WHERE r.rat_id IN (?, ?)
        """,
            (father_id, mother_id),
        )
        rat_info = cursor.fetchall()

        return {
            "success": True,
            "message": "เปลี่ยนสถานะเป็นหนูขุนสำเร็จ",
            "father_pond": father_pond,
            "mother_pond": mother_pond,
            "pond_freed": pond_freed,
            "freed_pond_id": current_pond_id if pond_freed else None,
            "pond_message": pond_message,
            "rat_info": rat_info,
        }

    except Exception as e:
        print(f"Error retiring breeding pair: {e}")
        return {
            "success": False,
            "message": f"ไม่สามารถเปลี่ยนสถานะหนูได้: {str(e)}",
            "pond_freed": False,
        }


def get_breeding_statistics(father_id, mother_id):
    """
    ดึงสถิติการผสมของหนูคู่นี้

    Args:
        father_id: รหัสหนูพ่อพันธุ์
        mother_id: รหัสหนูแม่พันธุ์

    Returns:
        dict: สถิติการผสม
    """
    from storages.database_service import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT 
                breeding_status,
                COUNT(*) as count,
                AVG(survived_pups) as avg_survived,
                AVG(total_pups) as avg_total,
                AVG(albino_pups) as avg_albino
            FROM breeding 
            WHERE father_id = ? AND mother_id = ?
            GROUP BY breeding_status
        """,
            (father_id, mother_id),
        )

        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = {
                "count": row[1],
                "avg_survived": row[2] or 0,
                "avg_total": row[3] or 0,
                "avg_albino": row[4] or 0,
            }

        return stats

    except Exception as e:
        print(f"Error getting breeding statistics: {e}")
        return {}
    finally:
        conn.close()


def add_sick_rat(sick_rats):
    """
    เพิ่มข้อมูลหนูป่วย
    sick_rats = [record_date, rat_id, symptoms, treatment, treated_by, results]
    """
    record_date = sick_rats[0]
    rat_id = sick_rats[1]
    symptoms = sick_rats[2] if len(sick_rats) > 2 else "มีอาการป่วย ซึม เบื่ออาหาร"
    treatment = sick_rats[3] if len(sick_rats) > 3 else "ให้ยาปฏิชีวนะและวิตามิน"
    treated_by = sick_rats[4] if len(sick_rats) > 4 else "สัตวแพทย์ประจำฟาร์ม"
    results = sick_rats[5] if len(sick_rats) > 5 else "sick"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ดึงข้อมูลหนูเพื่อตรวจสอบสถานะ
        cursor.execute("SELECT status FROM rat WHERE rat_id = ?", (rat_id,))
        rat_status = cursor.fetchone()

        if not rat_status:
            return {"success": False, "message": f"ไม่พบหนูรหัส {rat_id}"}

        # บันทึกประวัติการป่วย (health_id จะเป็น auto increment)
        cursor.execute(
            """
            INSERT INTO health (
                rat_id, record_date, symptoms, treatment, treated_by, results
            ) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (rat_id, record_date, symptoms, treatment, treated_by, results),
        )

        # ดึง health_id ที่ถูกสร้างใหม่
        health_id = cursor.lastrowid

        # ถ้าหนูกำลังผสมพันธุ์ ให้แยกคู่
        if rat_status[0] == "breeder1":
            # หาข้อมูลการผสมพันธุ์ที่กำลังดำเนินอยู่
            cursor.execute(
                """
                SELECT b.breeding_id, b.father_id, b.mother_id
                FROM breeding b 
                WHERE b.breeding_status = 'breeding'
                AND (b.father_id = ? OR b.mother_id = ?)
            """,
                (rat_id, rat_id),
            )

            breeding = cursor.fetchone()
            if breeding:
                breeding_id, father_id, mother_id = breeding
                separation_date = record_date

                # อัพเดทสถานะการผสมพันธุ์เป็น unsuccess
                cursor.execute(
                    """
                    UPDATE breeding 
                    SET breeding_status = 'unsuccess',
                        separation_date = ?,
                        total_pups = 0,
                        survived_pups = 0,
                        albino_pups = 0,
                        inbreeding_rate = 0
                    WHERE breeding_id = ?
                """,
                    (separation_date, breeding_id),
                )

                # หาบ่อที่ใช้ผสมพันธุ์
                cursor.execute(
                    """
                    SELECT DISTINCT pond_id 
                    FROM rat 
                    WHERE rat_id IN (?, ?) 
                    AND pond_id IS NOT NULL
                """,
                    (father_id, mother_id),
                )

                breeding_pond = cursor.fetchone()
                if breeding_pond:
                    # อัพเดทสถานะบ่อเป็นว่าง
                    cursor.execute(
                        """
                        UPDATE pond 
                        SET status = 'empty',
                            update_date = ?
                        WHERE pond_id = ?
                    """,
                        (separation_date, breeding_pond[0]),
                    )

                # อัพเดทสถานะพ่อแม่พันธุ์เป็น breeder2 และย้ายออกจากบ่อ
                cursor.execute(
                    """
                    UPDATE rat 
                    SET status = 'breeder2',
                        pond_id = NULL
                    WHERE rat_id IN (?, ?)
                """,
                    (father_id, mother_id),
                )

        conn.commit()
        return {
            "success": True,
            "health_id": health_id,
            "message": f"บันทึกข้อมูลสุขภาพเรียบร้อย รหัส: {health_id}",
        }

    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}
    finally:
        conn.close()


def get_all_health_records():
    """ดึงข้อมูลสุขภาพทั้งหมด"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            h.health_id,
            h.rat_id,
            h.record_date,
            h.symptoms,
            h.treatment,
            h.treated_by,
            h.results,
            r.gender,
            r.birth_date,
            r.breed,
            r.ring_number,
            r.pond_id
        FROM health h
        JOIN rat r ON h.rat_id = r.rat_id
        ORDER BY h.record_date DESC
    """
    )

    records = cursor.fetchall()
    conn.close()

    # แปลงเป็น dictionary
    health_records = []
    for record in records:
        health_records.append(
            {
                "health_id": record[0],
                "rat_id": record[1],
                "record_date": record[2],
                "symptoms": record[3],
                "treatment": record[4],
                "treated_by": record[5],
                "results": record[6],
                "gender": record[7],
                "birth_date": record[8],
                "breed": record[9],
                "ring_number": record[10],
                "pond_id": record[11],
            }
        )

    return health_records


def get_health_records_by_rat_id(rat_id):
    """ดึงประวัติสุขภาพของหนูตัวใดตัวหนึ่ง"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            health_id,
            record_date,
            symptoms,
            treatment,
            treated_by,
            results
        FROM health 
        WHERE rat_id = ?
        ORDER BY record_date DESC
    """,
        (rat_id,),
    )

    records = cursor.fetchall()
    conn.close()

    # แปลงเป็น dictionary
    health_history = []
    for record in records:
        health_history.append(
            {
                "health_id": record[0],
                "record_date": record[1],
                "symptoms": record[2],
                "treatment": record[3],
                "treated_by": record[4],
                "results": record[5],
            }
        )

    return health_history


def update_health_record(health_id, health_data):
    """อัพเดทข้อมูลการรักษา"""
    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE health 
            SET symptoms = ?, treatment = ?, treated_by = ?, results = ?
            WHERE health_id = ?
        """,
            (
                health_data["symptoms"],
                health_data["treatment"],
                health_data["treated_by"],
                health_data["results"],
                health_id,
            ),
        )
        
        conn.commit()

        health_record = get_health_record_by_id(health_id)
        if health_data["results"] == 'dead':
            update_rat_status(health_record["rat_id"], 'dispose')

        return {"success": True, "message": "อัพเดทข้อมูลเรียบร้อย"}

    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}
    finally:
        conn.close()


def get_health_record_by_id(health_id):
    """ดึงข้อมูลการรักษาตาม health_id"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            h.health_id,
            h.rat_id,
            h.record_date,
            h.symptoms,
            h.treatment,
            h.treated_by,
            h.results,
            r.gender,
            r.ring_number,
            r.breed
        FROM health h
        JOIN rat r ON h.rat_id = r.rat_id
        WHERE h.health_id = ?
    """,
        (health_id,),
    )

    record = cursor.fetchone()
    conn.close()

    if record:
        return {
            "health_id": record[0],
            "rat_id": record[1],
            "record_date": record[2],
            "symptoms": record[3],
            "treatment": record[4],
            "treated_by": record[5],
            "results": record[6],
            "gender": record[7],
            "ring_number": record[8],
            "breed": record[9],
        }
    return None


def get_rats_for_health_check():
    """ดึงรายชื่อหนูทั้งหมดสำหรับตรวจสุขภาพ"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            rat_id,
            gender,
            breed,
            ring_number,
            pond_id,
            status
        FROM rat 
        WHERE status NOT IN ('dispose')
        ORDER BY rat_id
    """
    )

    rats = cursor.fetchall()
    conn.close()

    # แปลงเป็น dictionary
    rat_list = []
    for rat in rats:
        rat_list.append(
            {
                "rat_id": rat[0],
                "gender": rat[1],
                "breed": rat[2],
                "ring_number": rat[3],
                "pond_id": rat[4],
                "status": rat[5],
            }
        )

    return rat_list


def get_health_statistics():
    """ดึงสถิติข้อมูลสุขภาพ"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # นับจำนวนตามสถานะ
        cursor.execute(
            """
            SELECT results, COUNT(*) as count
            FROM health 
            WHERE record_date >= date('now', '-30 days')
            GROUP BY results
        """
        )

        stats = cursor.fetchall()

        # แปลงเป็น dictionary
        health_stats = {
            "sick": 0,
            "recovering": 0,
            "monitoring": 0,
            "healed": 0,
            "dead": 0,
        }

        for stat in stats:
            health_stats[stat[0]] = stat[1]

        return health_stats

    except Exception as e:
        print(f"Error getting health statistics: {e}")
        return health_stats
    finally:
        conn.close()


def get_all_health_records():
    """ดึงข้อมูลสุขภาพทั้งหมด"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            h.health_id,
            h.rat_id,
            h.record_date,
            h.symptoms,
            h.treatment,
            h.treated_by,
            h.results,
            r.gender,
            r.birth_date,
            r.breed,
            r.ring_number,
            r.pond_id
        FROM health h
        JOIN rat r ON h.rat_id = r.rat_id
        WHERE h.results NOT IN ('healed', 'dead')
        ORDER BY h.record_date DESC
    """
    )

    records = cursor.fetchall()
    conn.close()

    # แปลงเป็น dictionary
    health_records = []
    for record in records:
        health_records.append(
            {
                "health_id": record[0],
                "rat_id": record[1],
                "record_date": record[2],
                "symptoms": record[3],
                "treatment": record[4],
                "treated_by": record[5],
                "results": record[6],
                "gender": record[7],
                "birth_date": record[8],
                "breed": record[9],
                "ring_number": record[10],
                "pond_id": record[11],
            }
        )

    return health_records


def get_health_records_by_rat_id(rat_id):
    """ดึงประวัติสุขภาพของหนูตัวใดตัวหนึ่ง"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            health_id,
            record_date,
            symptoms,
            treatment,
            treated_by,
            results
        FROM health 
        WHERE rat_id = ?
        ORDER BY record_date DESC
    """,
        (rat_id,),
    )

    records = cursor.fetchall()
    conn.close()

    # แปลงเป็น dictionary
    health_history = []
    for record in records:
        health_history.append(
            {
                "health_id": record[0],
                "record_date": record[1],
                "symptoms": record[2],
                "treatment": record[3],
                "treated_by": record[4],
                "results": record[5],
            }
        )

    return health_history


def get_health_record_by_id(health_id):
    """ดึงข้อมูลการรักษาตาม health_id"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            h.health_id,
            h.rat_id,
            h.record_date,
            h.symptoms,
            h.treatment,
            h.treated_by,
            h.results,
            r.gender,
            r.ring_number,
            r.breed
        FROM health h
        JOIN rat r ON h.rat_id = r.rat_id
        WHERE h.health_id = ?
    """,
        (health_id,),
    )

    record = cursor.fetchone()
    conn.close()

    if record:
        return {
            "health_id": record[0],
            "rat_id": record[1],
            "record_date": record[2],
            "symptoms": record[3],
            "treatment": record[4],
            "treated_by": record[5],
            "results": record[6],
            "gender": record[7],
            "ring_number": record[8],
            "breed": record[9],
        }
    return None


def delete_health_record(health_id):
    """ลบข้อมูลการรักษาตาม health_id"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM health WHERE health_id = ?", (health_id,))
        conn.commit()
        return {"success": True, "message": "ลบข้อมูลการรักษาเรียบร้อย"}

    except Exception as e:
        conn.rollback()
        return {"success": False, "message": f"เกิดข้อผิดพลาด: {str(e)}"}
    finally:
        conn.close()


def get_rats_for_health_check():
    """ดึงรายชื่อหนูทั้งหมดสำหรับตรวจสุขภาพ (ยกเว้นหนูที่ป่วยอยู่)"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
       SELECT 
           r.rat_id,
           r.gender,
           r.breed,
           r.ring_number,
           r.pond_id,
           r.status
       FROM rat r
       WHERE r.status NOT IN ('dispose', 'fertilize')
       AND r.rat_id NOT IN (
           SELECT h.rat_id 
           FROM health h 
           WHERE h.results IN ('sick', 'recovering', 'monitoring')
       )
       ORDER BY r.rat_id
   """
    )

    rats = cursor.fetchall()
    conn.close()

    # แปลงเป็น dictionary
    rat_list = []
    for rat in rats:
        rat_list.append(
            {
                "rat_id": rat[0],
                "gender": rat[1],
                "breed": rat[2],
                "ring_number": rat[3],
                "pond_id": rat[4],
                "status": rat[5],
            }
        )

    return rat_list


def export_rat_with_ancestors(rat_id: str, output_path: str) -> dict:
    """
    ส่งออกข้อมูลหนูและบรรพบุรุษเป็นไฟล์ CSV

    Args:
        rat_id: รหัสหนูที่ต้องการส่งออกข้อมูล
        output_path: ที่อยู่ไฟล์ CSV ที่ต้องการบันทึก

    Returns:
        dict: ผลลัพธ์การส่งออก
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ดึงข้อมูลบรรพบุรุษทั้งหมด
        cursor.execute(
            """
            WITH RECURSIVE ancestors AS (
                SELECT 
                    r.rat_id,
                    r.father_id,
                    r.mother_id,
                    strftime('%Y-%m-%d', r.birth_date) as birth_date,
                    r.gender,
                    r.weight,
                    r.size,
                    r.breed,
                    r.status,
                    r.pond_id,
                    r.farm_id,
                    r.has_ring,
                    r.ring_number,
                    r.special_traits,
                    0 as generation
                FROM rat r
                WHERE r.rat_id = ?
                
                UNION ALL
                
                SELECT 
                    r.rat_id,
                    r.father_id,
                    r.mother_id,
                    strftime('%Y-%m-%d', r.birth_date) as birth_date,
                    r.gender,
                    r.weight,
                    r.size,
                    r.breed,
                    r.status,
                    r.pond_id,
                    r.farm_id,
                    r.has_ring,
                    r.ring_number,
                    r.special_traits,
                    a.generation + 1
                FROM rat r
                JOIN ancestors a ON r.rat_id IN (a.father_id, a.mother_id)
                WHERE r.rat_id IS NOT NULL
            )
            SELECT * FROM ancestors
            ORDER BY generation ASC, rat_id ASC
        """,
            (rat_id,),
        )

        rats_data = cursor.fetchall()

        if not rats_data:
            return {
                "success": False,
                "message": f"ไม่พบข้อมูลหนูรหัส {rat_id}",
                "file_path": None,
            }

        # สร้าง CSV header
        columns = [
            "rat_id",
            "father_id",
            "mother_id",
            "birth_date",
            "gender",
            "weight",
            "size",
            "breed",
            "status",
            "pond_id",
            "farm_id",
            "has_ring",
            "ring_number",
            "special_traits",
            "generation",
        ]

        # เขียนไฟล์ CSV
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(columns)  # เขียน header
            writer.writerows(rats_data)  # เขียนข้อมูล

        # สร้าง export_id สำหรับบันทึกประวัติ
        export_id = f"EXP{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # บันทึกประวัติการส่งออก
        export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO export_history (
                export_id, export_date, file_name, file_type, status, note
            ) VALUES (?, ?, ?, 'CSV', 'success', ?)
        """,
            (
                export_id,
                export_date,
                output_path.split("/")[-1],  # เอาเฉพาะชื่อไฟล์
                f"ส่งออกข้อมูลหนูรหัส {rat_id} และบรรพบุรุษ {len(rats_data)} ตัว",
            ),
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": f"ส่งออกข้อมูลสำเร็จ {len(rats_data)} ตัว",
            "file_path": output_path,
            "export_id": export_id,
            "total_records": len(rats_data),
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"เกิดข้อผิดพลาดในการส่งออกข้อมูล: {str(e)}",
            "file_path": None,
        }


def export_all_rats(output_path: str) -> dict:
    """
    ส่งออกข้อมูลหนูทั้งหมด
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                rat_id, father_id, mother_id,
                strftime('%Y-%m-%d', birth_date) as birth_date,
                gender, weight, size, breed, status,
                pond_id, farm_id, has_ring, ring_number, special_traits
            FROM rat
            ORDER BY rat_id
        """
        )

        rats_data = cursor.fetchall()

        if not rats_data:
            return {"success": False, "message": "ไม่มีข้อมูลหนูในระบบ", "file_path": None}

        columns = [
            "rat_id",
            "father_id",
            "mother_id",
            "birth_date",
            "gender",
            "weight",
            "size",
            "breed",
            "status",
            "pond_id",
            "farm_id",
            "has_ring",
            "ring_number",
            "special_traits",
        ]

        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rats_data)

        # บันทึกประวัติ
        export_id = f"EXP{datetime.now().strftime('%Y%m%d%H%M%S')}"
        export_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            INSERT INTO export_history (
                export_id, export_date, file_name, file_type, status, note
            ) VALUES (?, ?, ?, 'CSV', 'success', ?)
        """,
            (
                export_id,
                export_date,
                output_path.split("/")[-1],
                f"ส่งออกข้อมูลหนูทั้งหมด {len(rats_data)} ตัว",
            ),
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": f"ส่งออกข้อมูลสำเร็จ {len(rats_data)} ตัว",
            "file_path": output_path,
            "export_id": export_id,
            "total_records": len(rats_data),
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"เกิดข้อผิดพลาดในการส่งออกข้อมูล: {str(e)}",
            "file_path": None,
        }
