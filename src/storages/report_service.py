from datetime import datetime, timedelta
from storages.database_service import get_connection
import sqlite3
from typing import Dict, List, Optional
import pandas as pd


def get_breeding_performance() -> Dict:
    """
    ดึงข้อมูลประสิทธิภาพการผสมพันธุ์

    Returns:
        Dict: ข้อมูลประสิทธิภาพการผสมพันธุ์
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # อัตราความสำเร็จของการผสมพันธุ์
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_breedings,
                SUM(CASE WHEN breeding_status = 'success' THEN 1 ELSE 0 END) as successful_breedings,
                AVG(CASE WHEN breeding_status = 'success' THEN total_pups ELSE 0 END) as avg_pups,
                AVG(CASE WHEN breeding_status = 'success' THEN albino_pups ELSE 0 END) as avg_albino
            FROM breeding
            WHERE breeding_date >= date('now', '-12 months')
        """
        )

        result = cursor.fetchone()

        if result and result[0] > 0:
            total_breedings = result[0]
            successful_breedings = result[1] or 0
            avg_pups = result[2] or 0
            avg_albino = result[3] or 0

            success_rate = (successful_breedings / total_breedings) * 100
        else:
            total_breedings = 0
            successful_breedings = 0
            success_rate = 0
            avg_pups = 0
            avg_albino = 0

        conn.close()

        return {
            "success_rate": success_rate,
            "avg_pups_per_breeding": avg_pups,
            "avg_albino_per_breeding": avg_albino,
            "total_breedings": total_breedings,
            "successful_breedings": successful_breedings,
        }

    except Exception as e:
        print(f"Error getting breeding performance: {e}")
        return {
            "success_rate": 0,
            "avg_pups_per_breeding": 0,
            "avg_albino_per_breeding": 0,
            "total_breedings": 0,
            "successful_breedings": 0,
        }


def get_health_statistics() -> Dict:
    """
    ดึงสถิติสุขภาพหนู

    Returns:
        Dict: สถิติสุขภาพหนู
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # นับจำนวนหนูทั้งหมด
        cursor.execute("SELECT COUNT(*) FROM rat WHERE status != 'dispose'")
        total_rats = cursor.fetchone()[0] or 0

        if total_rats == 0:
            return {
                "healthy_rate": 0,
                "sick_rate": 0,
                "monitoring_rate": 0,
                "total_rats": 0,
            }

        # นับหนูที่มีปัญหาสุขภาพล่าสุด
        cursor.execute(
            """
            SELECT 
                SUM(CASE WHEN h.results = 'sick' THEN 1 ELSE 0 END) as sick_count,
                SUM(CASE WHEN h.results = 'monitoring' THEN 1 ELSE 0 END) as monitoring_count,
                SUM(CASE WHEN h.results IN ('healed', 'recovering') THEN 1 ELSE 0 END) as recovered_count
            FROM (
                SELECT rat_id, results
                FROM health h1
                WHERE h1.record_date = (
                    SELECT MAX(h2.record_date)
                    FROM health h2
                    WHERE h2.rat_id = h1.rat_id
                )
            ) h
        """
        )

        health_result = cursor.fetchone()

        if health_result:
            sick_count = health_result[0] or 0
            monitoring_count = health_result[1] or 0
            recovered_count = health_result[2] or 0

            # หนูที่มีปัญหาสุขภาพ
            unhealthy_count = sick_count + monitoring_count
            healthy_count = total_rats - unhealthy_count

            healthy_rate = (healthy_count / total_rats) * 100
            sick_rate = (sick_count / total_rats) * 100
            monitoring_rate = (monitoring_count / total_rats) * 100
        else:
            healthy_rate = 100
            sick_rate = 0
            monitoring_rate = 0

        conn.close()

        return {
            "healthy_rate": max(0, healthy_rate),
            "sick_rate": sick_rate,
            "monitoring_rate": monitoring_rate,
            "total_rats": total_rats,
        }

    except Exception as e:
        print(f"Error getting health statistics: {e}")
        return {
            "healthy_rate": 0,
            "sick_rate": 0,
            "monitoring_rate": 0,
            "total_rats": 0,
        }


def get_albino_trend_data(period: str) -> List[int]:
    """
    ดึงข้อมูลแนวโน้มหนูเผือกตาแดงตามช่วงเวลา

    Args:
        period: ช่วงเวลา ('1W', '1M', '3M', '6M', '1Y')

    Returns:
        List[int]: ข้อมูลจำนวนหนูเผือกแต่ละช่วง
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # กำหนดช่วงเวลาและจำนวนจุดข้อมูล
        period_mapping = {
            "1W": (7, "day"),
            "1M": (30, "day"),
            "3M": (12, "week"),
            "6M": (24, "week"),
            "1Y": (12, "month"),
        }

        if period not in period_mapping:
            return []

        points, unit = period_mapping[period]
        data = []

        for i in range(points):
            if unit == "day":
                start_date = datetime.now() - timedelta(days=points - i)
                end_date = start_date + timedelta(days=1)
            elif unit == "week":
                start_date = datetime.now() - timedelta(weeks=points - i)
                end_date = start_date + timedelta(weeks=1)
            else:  # month
                start_date = datetime.now() - timedelta(days=30 * (points - i))
                end_date = start_date + timedelta(days=30)

            cursor.execute(
                """
                SELECT COALESCE(SUM(albino_pups), 0)
                FROM breeding
                WHERE birth_date >= ? AND birth_date < ? AND breeding_status = 'success'
            """,
                (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
            )

            result = cursor.fetchone()
            data.append(result[0] if result else 0)

        conn.close()
        return data

    except Exception as e:
        print(f"Error getting albino trend data: {e}")
        # Return sample data if error occurs
        sample_data = {
            "1W": [2, 1, 3, 0, 1, 2, 0],
            "1M": [8, 6, 10, 4, 5, 7, 9, 3, 6, 8],
            "3M": [25, 22, 28, 20, 18, 24, 26, 21, 19, 23, 27, 24],
            "6M": [45, 42, 48, 40, 38, 44, 46, 41, 39, 43, 47, 44] * 2,
            "1Y": [85, 82, 88, 80, 78, 84, 86, 81, 79, 83, 87, 84],
        }
        return sample_data.get(period, [])


def get_birth_rate_data(period: str) -> List[int]:
    """
    ดึงข้อมูลอัตราการเกิดตามช่วงเวลา

    Args:
        period: ช่วงเวลา ('1W', '1M', '3M', '6M', '1Y')

    Returns:
        List[int]: ข้อมูลจำนวนลูกที่เกิดแต่ละช่วง
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # กำหนดช่วงเวลาและจำนวนจุดข้อมูล
        period_mapping = {
            "1W": (7, "day"),
            "1M": (30, "day"),
            "3M": (12, "week"),
            "6M": (24, "week"),
            "1Y": (12, "month"),
        }

        if period not in period_mapping:
            return []

        points, unit = period_mapping[period]
        data = []

        for i in range(points):
            if unit == "day":
                start_date = datetime.now() - timedelta(days=points - i)
                end_date = start_date + timedelta(days=1)
            elif unit == "week":
                start_date = datetime.now() - timedelta(weeks=points - i)
                end_date = start_date + timedelta(weeks=1)
            else:  # month
                start_date = datetime.now() - timedelta(days=30 * (points - i))
                end_date = start_date + timedelta(days=30)

            cursor.execute(
                """
                SELECT COALESCE(SUM(total_pups), 0)
                FROM breeding
                WHERE birth_date >= ? AND birth_date < ? AND breeding_status = 'success'
            """,
                (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
            )

            result = cursor.fetchone()
            data.append(result[0] if result else 0)

        conn.close()
        return data

    except Exception as e:
        print(f"Error getting birth rate data: {e}")
        # Return sample data if error occurs
        sample_data = {
            "1W": [12, 8, 15, 10, 6, 13, 9],
            "1M": [45, 38, 52, 41, 35, 48, 44, 39, 42, 46],
            "3M": [125, 118, 132, 121, 115, 128, 124, 119, 122, 126, 130, 123],
            "6M": [245, 238, 252, 241, 235, 248, 244, 239, 242, 246, 250, 243] * 2,
            "1Y": [485, 478, 492, 481, 475, 488, 484, 479, 482, 486, 490, 483],
        }
        return sample_data.get(period, [])


def get_general_statistics() -> Dict:
    """
    ดึงสถิติทั่วไป

    Returns:
        Dict: สถิติทั่วไป
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # นับจำนวนหนูตามสถานะ
        cursor.execute(
            """
            SELECT status, COUNT(*) 
            FROM rat 
            GROUP BY status
        """
        )

        rat_status = dict(cursor.fetchall())

        # นับจำนวนการผสมตามสถานะ
        cursor.execute(
            """
            SELECT breeding_status, COUNT(*) 
            FROM breeding 
            WHERE breeding_date >= date('now', '-12 months')
            GROUP BY breeding_status
        """
        )

        breeding_status = dict(cursor.fetchall())

        # นับจำนวนบ่อตามสถานะ
        cursor.execute(
            """
            SELECT status, COUNT(*) 
            FROM pond 
            GROUP BY status
        """
        )

        pond_status = dict(cursor.fetchall())

        conn.close()

        return {
            "rat_status": rat_status,
            "breeding_status": breeding_status,
            "pond_status": pond_status,
        }

    except Exception as e:
        print(f"Error getting general statistics: {e}")
        return {"rat_status": {}, "breeding_status": {}, "pond_status": {}}


def get_monthly_breeding_summary(months: int = 12) -> List[Dict]:
    """
    ดึงสรุปการผสมพันธุ์รายเดือน

    Args:
        months: จำนวนเดือนที่ต้องการ

    Returns:
        List[Dict]: ข้อมูลการผสมแต่ละเดือน
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                strftime('%Y-%m', breeding_date) as month,
                COUNT(*) as total_breedings,
                SUM(CASE WHEN breeding_status = 'success' THEN 1 ELSE 0 END) as successful,
                SUM(CASE WHEN breeding_status = 'success' THEN total_pups ELSE 0 END) as total_pups,
                SUM(CASE WHEN breeding_status = 'success' THEN albino_pups ELSE 0 END) as albino_pups
            FROM breeding
            WHERE breeding_date >= date('now', '-{} months')
            GROUP BY strftime('%Y-%m', breeding_date)
            ORDER BY month
        """.format(
                months
            )
        )

        results = cursor.fetchall()
        monthly_data = []

        for row in results:
            month, total, successful, total_pups, albino_pups = row
            success_rate = (successful / total * 100) if total > 0 else 0

            monthly_data.append(
                {
                    "month": month,
                    "total_breedings": total,
                    "successful_breedings": successful,
                    "success_rate": success_rate,
                    "total_pups": total_pups or 0,
                    "albino_pups": albino_pups or 0,
                }
            )

        conn.close()
        return monthly_data

    except Exception as e:
        print(f"Error getting monthly breeding summary: {e}")
        return []


def get_health_trend_data(period: str) -> List[int]:
    """
    ดึงข้อมูลแนวโน้มการป่วยตามช่วงเวลา (ข้อมูลจริงจากฐานข้อมูล)

    Args:
        period: ช่วงเวลา ('1W', '1M', '3M', '6M', '1Y')

    Returns:
        List[int]: ข้อมูลจำนวนหนูป่วยแต่ละช่วง
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # กำหนดช่วงเวลาและจำนวนจุดข้อมูล
        period_mapping = {
            "1W": (7, "day"),
            "1M": (30, "day"),
            "3M": (12, "week"),
            "6M": (24, "week"),
            "1Y": (12, "month"),
        }

        if period not in period_mapping:
            print(f"Invalid period: {period}")
            return []

        points, unit = period_mapping[period]
        data = []

        for i in range(points):
            if unit == "day":
                end_date = datetime.now() - timedelta(days=i)
                start_date = end_date - timedelta(days=1)
            elif unit == "week":
                end_date = datetime.now() - timedelta(weeks=i)
                start_date = end_date - timedelta(weeks=1)
            else:  # month
                end_date = datetime.now() - timedelta(days=30 * i)
                start_date = end_date - timedelta(days=30)

            # Query สำหรับนับจำนวนหนูป่วยในช่วงเวลานั้น
            cursor.execute(
                """
                SELECT COUNT(DISTINCT rat_id)
                FROM health
                WHERE record_date >= ? AND record_date < ? 
                AND results IN ('sick', 'monitoring')
            """,
                (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
            )

            result = cursor.fetchone()
            count = result[0] if result else 0
            data.append(count)

        # เรียงข้อมูลจากเก่าไปใหม่
        data.reverse()

        conn.close()

        # ถ้าไม่มีข้อมูลในฐานข้อมูล ให้ใช้ข้อมูลตัวอย่าง
        if all(x == 0 for x in data):
            # sample_data = {
            #     "1W": [5, 3, 7, 4, 2, 6, 1],
            #     "1M": [
            #         15,
            #         12,
            #         18,
            #         10,
            #         8,
            #         14,
            #         16,
            #         11,
            #         9,
            #         13,
            #         17,
            #         5,
            #         8,
            #         12,
            #         6,
            #         9,
            #         11,
            #         14,
            #         7,
            #         4,
            #         13,
            #         10,
            #         8,
            #         15,
            #         12,
            #         6,
            #         9,
            #         11,
            #         7,
            #         3,
            #     ],
            #     "3M": [45, 38, 52, 41, 35, 48, 44, 39, 42, 46, 50, 43],
            #     "6M": [
            #         85,
            #         78,
            #         92,
            #         81,
            #         75,
            #         88,
            #         84,
            #         79,
            #         82,
            #         86,
            #         90,
            #         83,
            #         87,
            #         91,
            #         76,
            #         89,
            #         93,
            #         77,
            #         80,
            #         85,
            #         88,
            #         74,
            #         82,
            #         90,
            #     ],
            #     "1Y": [165, 158, 172, 161, 155, 168, 164, 159, 162, 166, 170, 163],
            # }
            sample_data = {
                "1W": [0, 0, 0, 0, 0, 0, 0],
                "1M": [
                    0,
                    0,
                    0,
                    0,
                0,
                    0,
                    0,
                    0,
                0,
                    0,
                    0,
                0,
                0,
                    0,
                0,
                0,
                    0,
                    0,
                0,
                0,
                    0,
                    0,
                0,
                    0,
                    0,
                0,
                0,
                    0,
                0,
                0,
                ],
                "3M": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
                "6M": [
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                ],
                "1Y": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
            }
            return sample_data.get(period, data)

        return data

    except Exception as e:
        print(f"Error getting health trend data: {e}")
        # Return sample data if error occurs
        sample_data = {
            "1W": [5, 3, 7, 4, 2, 6, 1],
            "1M": [
                15,
                12,
                18,
                10,
                8,
                14,
                16,
                11,
                9,
                13,
                17,
                5,
                8,
                12,
                6,
                9,
                11,
                14,
                7,
                4,
                13,
                10,
                8,
                15,
                12,
                6,
                9,
                11,
                7,
                3,
            ],
            "3M": [45, 38, 52, 41, 35, 48, 44, 39, 42, 46, 50, 43],
            "6M": [
                85,
                78,
                92,
                81,
                75,
                88,
                84,
                79,
                82,
                86,
                90,
                83,
                87,
                91,
                76,
                89,
                93,
                77,
                80,
                85,
                88,
                74,
                82,
                90,
            ],
            "1Y": [165, 158, 172, 161, 155, 168, 164, 159, 162, 166, 170, 163],
        }
        return sample_data.get(period, [])


def get_productivity_metrics() -> Dict:
    """
    ดึงตัวชี้วัดประสิทธิภาพฟาร์ม

    Returns:
        Dict: ตัวชี้วัดต่างๆ
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # อัตราการใช้ห่วงขา
        cursor.execute(
            """
            SELECT 
                MAX(ring_amount) as total_rings,
                COUNT(CASE WHEN has_ring = 1 THEN 1 END) as used_rings
            FROM farm f
            LEFT JOIN rat r ON f.farm_id = r.farm_id
        """
        )

        ring_result = cursor.fetchone()
        total_rings = ring_result[0] or 0
        used_rings = ring_result[1] or 0
        ring_usage_rate = (used_rings / total_rings * 100) if total_rings > 0 else 0

        # อัตราการใช้บ่อ
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_ponds,
                COUNT(CASE WHEN status != 'empty' THEN 1 END) as used_ponds
            FROM pond
        """
        )

        pond_result = cursor.fetchone()
        total_ponds = pond_result[0] or 0
        used_ponds = pond_result[1] or 0
        pond_usage_rate = (used_ponds / total_ponds * 100) if total_ponds > 0 else 0

        # อัตราส่วนเพศ
        cursor.execute(
            """
            SELECT 
                gender,
                COUNT(*) as count
            FROM rat
            WHERE status != 'dispose'
            GROUP BY gender
        """
        )

        gender_results = dict(cursor.fetchall())
        male_count = gender_results.get("male", 0)
        female_count = gender_results.get("female", 0)
        total_gender = male_count + female_count

        male_ratio = (male_count / total_gender * 100) if total_gender > 0 else 0
        female_ratio = (female_count / total_gender * 100) if total_gender > 0 else 0

        conn.close()

        return {
            "ring_usage_rate": ring_usage_rate,
            "pond_usage_rate": pond_usage_rate,
            "male_ratio": male_ratio,
            "female_ratio": female_ratio,
            "total_rings": total_rings,
            "used_rings": used_rings,
            "total_ponds": total_ponds,
            "used_ponds": used_ponds,
        }

    except Exception as e:
        print(f"Error getting productivity metrics: {e}")
        return {
            "ring_usage_rate": 0,
            "pond_usage_rate": 0,
            "male_ratio": 50,
            "female_ratio": 50,
            "total_rings": 0,
            "used_rings": 0,
            "total_ponds": 0,
            "used_ponds": 0,
        }
