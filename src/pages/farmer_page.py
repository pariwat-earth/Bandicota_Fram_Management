from datetime import date
import flet as ft
import requests
from components.base_box import (
    base_empty_box,
    base_info_report_box_v2,
)
from components.base_button import (
    base_button_gradient,
    base_button_gradient_v2,
    base_button_normal,
)
from storages.database_service import (
    add_farms_data,
    add_number_pond,
    delete_empty_ponds,
    delete_farm_by_farm_id,
    get_all_farm,
    get_farm_by_farm_id,
    get_last_inserted_farm_id,
    get_pond_count_by_farm_id,
    update_farm_by_farm_id,
)
from storages.general_information import get_amount_farm, get_amount_pond, get_amount_rat, get_pond_use_rate, update_hmt_page, update_selected_farm_id
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, White

sql_status = 0  # 0:insert 1:update
farm_edit_id = 0


def farmer_page():

    page_list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.padding.all(20),
    )

    """
    เริ่ม code ส่วนการเพิ่มฟาร์ม
    """

    # LONGDO_API_KEY คือคีย์ที่ได้จากการลงทะเบียนที่ https://map.longdo.com/console/
    LONGDO_API_KEY = ""

    text_style = ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=Grey)

    error_text = ft.Text(
        "",
        color=ft.Colors.RED_500,
        size=12,
        visible=False,
    )

    selected_location = ft.Text("ยังไม่ได้เลือกตำแหน่ง", size=10)

    # สร้างตัวแปรสำหรับเก็บค่า input
    farm_name_field = ft.TextField(
        label="ชื่อฟาร์ม",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    # เพิ่มฟิลด์พิกัดที่ผู้ใช้สามารถกรอกเองได้
    latitude_field = ft.TextField(
        label="Latitude",
        border=ft.InputBorder.OUTLINE,
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    longitude_field = ft.TextField(
        label="Longitude",
        border=ft.InputBorder.OUTLINE,
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    # สร้างฟิลด์สำหรับกรอกข้อมูลที่อยู่
    address_number_field = ft.TextField(
        label="บ้านเลขที่",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    moo_field = ft.TextField(
        label="หมู่",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    subdistrict_field = ft.TextField(
        label="ตำบล/แขวง",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    district_field = ft.TextField(
        label="อำเภอ/เขต",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    province_field = ft.TextField(
        label="จังหวัด",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    postcode_field = ft.TextField(
        label="รหัสไปรษณีย์",
        border=ft.InputBorder.OUTLINE,
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    location_progress = ft.ProgressRing(
        width=16, height=16, stroke_width=2, visible=False
    )

    # ข้อความแสดงสถานะ
    location_status = ft.Text("", size=12, color=Grey, visible=False)

    farm_manager_field = ft.TextField(
        label="ชื่อผู้จัดการ",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    farm_ponds_field = ft.TextField(
        label="จำนวนบ่อเลี้ยง",
        border=ft.InputBorder.OUTLINE,
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    farm_ring_field = ft.TextField(
        label="จำนวนห่วงขา",
        border=ft.InputBorder.OUTLINE,
        keyboard_type=ft.KeyboardType.NUMBER,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    farm_type_dropdown = ft.Dropdown(
        label="ประเภทฟาร์ม",
        options=[ft.dropdown.Option("ฟาร์มหลัก"), ft.dropdown.Option("ฟาร์มเครือข่าย")],
        expand=True,
        text_style=text_style,
        label_style=text_style,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    # ฟังก์ชันค้นหาพิกัดจากที่อยู่
    def search_coordinates_from_address(e):
        # ตรวจสอบว่ามีการกรอกข้อมูลที่อยู่ที่จำเป็นหรือไม่
        if not (province_field.value and district_field.value):
            location_status.value = "กรุณากรอกข้อมูลจังหวัดและอำเภอเป็นอย่างน้อย"
            location_status.color = ft.Colors.RED_500
            location_status.visible = True
            page_list_view.update()
            return

        location_progress.visible = True
        location_status.value = "กำลังค้นหาพิกัด..."
        location_status.color = Grey
        location_status.visible = True
        page_list_view.update()

        # สร้างข้อความที่อยู่จากข้อมูลที่กรอก
        address_parts = []

        if address_number_field.value:
            address_parts.append(address_number_field.value)
        if moo_field.value:
            address_parts.append(f"หมู่ที่ {moo_field.value}")
        if subdistrict_field.value:
            address_parts.append(f"ต.{subdistrict_field.value}")
        if district_field.value:
            address_parts.append(f"อ.{district_field.value}")
        if province_field.value:
            address_parts.append(f"จ.{province_field.value}")
        if postcode_field.value:
            address_parts.append(postcode_field.value)

        address_text = " ".join(address_parts)

        try:
            # ใช้ Longdo Map Geocoding API เพื่อค้นหาพิกัดจากที่อยู่
            url = "https://search.longdo.com/mapsearch/json/search"
            params = {"keyword": address_text, "key": LONGDO_API_KEY, "limit": "1"}

            headers = {"User-Agent": "Mozilla/5.0", "Referer": "http://localhost"}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()

                if "data" in result and len(result["data"]) > 0:
                    location_data = result["data"][0]

                    if "lat" in location_data and "lon" in location_data:
                        lat = location_data["lat"]
                        lon = location_data["lon"]

                        # อัปเดตค่าพิกัด
                        latitude_field.value = str(lat)
                        longitude_field.value = str(lon)
                        selected_location.value = f"พิกัดที่พบ: {lat:.6f}, {lon:.6f}"

                        place_name = location_data.get("name", "")

                        # อัปเดตสถานะ
                        location_status.value = f"พบพิกัดสำหรับที่อยู่: {place_name if place_name else address_text}"
                        location_status.color = ft.Colors.GREEN
                    else:
                        location_status.value = "พบสถานที่แต่ไม่มีข้อมูลพิกัด"
                        location_status.color = ft.Colors.ORANGE

                        # ลองใช้ API อีกตัวหนึ่ง
                        try_alternative_geocoding_api(address_text)
                else:
                    location_status.value = f"ไม่พบพิกัดสำหรับที่อยู่นี้"
                    location_status.color = ft.Colors.RED_500

                    # ลองใช้ API อีกตัวหนึ่ง
                    try_alternative_geocoding_api(address_text)
            else:
                location_status.value = f"การค้นหาพิกัดล้มเหลว: {response.status_code}"
                location_status.color = ft.Colors.RED_500

                # ลองใช้ API อีกตัวหนึ่ง
                try_alternative_geocoding_api(address_text)

        except Exception as e:
            print(f"Error in search_coordinates_from_address: {e}")
            location_status.value = f"เกิดข้อผิดพลาด: {str(e)}"
            location_status.color = ft.Colors.RED_500

            # ลองใช้ API อีกตัวหนึ่ง
            try_alternative_geocoding_api(address_text)

        finally:
            location_progress.visible = False
            location_status.visible = True
            page_list_view.update()

    # ฟังก์ชันทางเลือกสำหรับค้นหาพิกัด
    def try_alternative_geocoding_api(address_text):
        try:
            # ใช้ Longdo Map Smartsearch API
            url = "https://search.longdo.com/smartsearch/json/search"
            params = {"keyword": address_text, "key": LONGDO_API_KEY}

            headers = {"User-Agent": "Mozilla/5.0", "Referer": "http://localhost"}

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()

                if "data" in result and len(result["data"]) > 0:
                    location_data = result["data"][0]

                    if "lat" in location_data and "lon" in location_data:
                        lat = location_data["lat"]
                        lon = location_data["lon"]

                        # อัปเดตค่าพิกัด
                        latitude_field.value = str(lat)
                        longitude_field.value = str(lon)
                        selected_location.value = f"พิกัดที่พบ: {lat:.6f}, {lon:.6f}"

                        # อัปเดตสถานะ
                        location_status.value = f"พบพิกัด (จาก API ทางเลือก): {lat}, {lon}"
                        location_status.color = ft.Colors.GREEN
                        page_list_view.update()
                        return True

        except Exception as e:
            print(f"Error in alternative API: {e}")

        return False

    # ฟังก์ชันสำหรับตรวจสอบความถูกต้องของข้อมูล
    def validate_form():
        is_valid = True

        # ตรวจสอบชื่อฟาร์ม
        if not farm_name_field.value:
            farm_name_field.border_color = ft.Colors.RED_500
            farm_name_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            farm_name_field.border_color = None
            farm_name_field.helper_text = ""
            farm_name_field.helper_style = None

        # ตรวจสอบบ้านเลขที่/หมู่
        if not address_number_field.value:
            address_number_field.border_color = ft.Colors.RED_500
            address_number_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            address_number_field.border_color = None
            address_number_field.helper_text = ""
            address_number_field.helper_style = None

        if not moo_field.value:
            moo_field.border_color = ft.Colors.RED_500
            moo_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            moo_field.border_color = None
            moo_field.helper_text = ""
            moo_field.helper_style = None

        # ตรวจสอบตำบล/แขวง
        if not subdistrict_field.value:
            subdistrict_field.border_color = ft.Colors.RED_500
            subdistrict_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            subdistrict_field.border_color = None
            subdistrict_field.helper_text = ""
            subdistrict_field.helper_style = None

        # ตรวจสอบอำเภอ/เขต
        if not district_field.value:
            district_field.border_color = ft.Colors.RED_500
            district_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            district_field.border_color = None
            district_field.helper_text = ""
            district_field.helper_style = None

        # ตรวจสอบจังหวัด
        if not province_field.value:
            province_field.border_color = ft.Colors.RED_500
            province_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            province_field.border_color = None
            province_field.helper_text = ""
            province_field.helper_style = None

        # ตรวจสอบรหัสไปรษณีย์
        if not postcode_field.value:
            postcode_field.border_color = ft.Colors.RED_500
            postcode_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            # ตรวจสอบว่ารหัสไปรษณีย์เป็นตัวเลข 5 หลัก
            if not postcode_field.value.isdigit() or len(postcode_field.value) != 5:
                postcode_field.border_color = ft.Colors.RED_500
                postcode_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                is_valid = False
            else:
                postcode_field.border_color = None
                postcode_field.helper_text = ""
                postcode_field.helper_style = None

        # ตรวจสอบพิกัด (latitude, longitude)
        if not (latitude_field.value and longitude_field.value):
            latitude_field.border_color = ft.Colors.RED_500
            longitude_field.border_color = ft.Colors.RED_500
            latitude_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            longitude_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            try:
                lat = float(latitude_field.value)
                lon = float(longitude_field.value)

                # ตรวจสอบพิสัยของค่าพิกัด
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    latitude_field.border_color = ft.Colors.RED_500
                    longitude_field.border_color = ft.Colors.RED_500
                    latitude_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                    longitude_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                    is_valid = False
                else:
                    latitude_field.border_color = None
                    longitude_field.border_color = None
                    latitude_field.helper_text = ""
                    longitude_field.helper_text = ""
                    latitude_field.helper_style = None
                    longitude_field.helper_style = None
            except ValueError:
                latitude_field.border_color = ft.Colors.RED_500
                longitude_field.border_color = ft.Colors.RED_500
                latitude_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                longitude_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                is_valid = False

        # ตรวจสอบชื่อผู้จัดการ
        if not farm_manager_field.value:
            farm_manager_field.border_color = ft.Colors.RED_500
            farm_manager_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            farm_manager_field.border_color = None
            farm_manager_field.helper_text = ""
            farm_manager_field.helper_style = None

        # ตรวจสอบจำนวนบ่อเลี้ยง
        if not farm_ponds_field.value:
            farm_ponds_field.border_color = ft.Colors.RED_500
            farm_ponds_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            try:
                ponds = int(farm_ponds_field.value)
                if ponds <= 0:
                    farm_ponds_field.border_color = ft.Colors.RED_500
                    farm_ponds_field.helper_style = ft.TextStyle(
                        color=ft.Colors.RED_500
                    )
                    is_valid = False
                else:
                    farm_ponds_field.border_color = None
                    farm_ponds_field.helper_text = ""
                    farm_ponds_field.helper_style = None
            except ValueError:
                farm_ponds_field.border_color = ft.Colors.RED_500
                farm_ponds_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                is_valid = False

        # ตรวจสอบจำนวนห่วงขา
        if not farm_ring_field.value:
            farm_ring_field.border_color = ft.Colors.RED_500
            farm_ring_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            try:
                rings = int(farm_ring_field.value)
                if rings < 0:
                    farm_ring_field.border_color = ft.Colors.RED_500
                    farm_ring_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                    is_valid = False
                else:
                    farm_ring_field.border_color = None
                    farm_ring_field.helper_text = ""
                    farm_ring_field.helper_style = None
            except ValueError:
                farm_ring_field.border_color = ft.Colors.RED_500
                farm_ring_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                is_valid = False

        # ตรวจสอบประเภทฟาร์ม
        if not farm_type_dropdown.value:
            farm_type_dropdown.border_color = ft.Colors.RED_500
            farm_type_dropdown.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False
        else:
            farm_type_dropdown.border_color = None
            farm_type_dropdown.helper_text = ""
            farm_type_dropdown.helper_style = None

        # ตรวจสอบความถูกต้องโดยรวม
        if not is_valid:
            error_text.value = "กรุณากรอกข้อมูลให้ครบถ้วนและถูกต้อง"
            error_text.visible = True
        else:
            error_text.visible = False

        page_list_view.update()
        return is_valid

    # ฟังก์ชันสร้างข้อความที่อยู่แบบเต็ม
    def get_full_address():
        address_parts = []

        if address_number_field.value:
            address_parts.append(address_number_field.value)
        if moo_field.value:
            address_parts.append(f"หมู่{moo_field.value}")
        if subdistrict_field.value:
            address_parts.append(f"ตำบล{subdistrict_field.value}")
        if district_field.value:
            address_parts.append(f"อำเภอ{district_field.value}")
        if province_field.value:
            address_parts.append(f"จังหวัด{province_field.value}")
        if postcode_field.value:
            address_parts.append(postcode_field.value)

        return " ".join(address_parts)

    def save_new_farm(e):
        global sql_status
        global farm_edit_id
        if validate_form():
            full_address = get_full_address()

            farm_type_id = "member"

            if farm_type_dropdown.value == "ฟาร์มหลัก":
                farm_type_id = "main"

            today = date.today()
            formatted_date = today.strftime("%Y-%m-%d")
            farms = (
                farm_name_field.value,
                full_address,
                latitude_field.value,
                longitude_field.value,
                int(farm_ponds_field.value),
                int(farm_ring_field.value),
                farm_manager_field.value,
                formatted_date,
                farm_type_id,
            )

            if sql_status:
                # อัปเดตข้อมูลฟาร์มเดิม
                insert_status = update_farm_by_farm_id(farm_edit_id, farms)
                
                if insert_status:
                    # ตรวจสอบการเปลี่ยนแปลงจำนวนบ่อ
                    current_ponds = get_pond_count_by_farm_id(farm_edit_id)
                    new_ponds = int(farm_ponds_field.value)
                    
                    if new_ponds > current_ponds:
                        # เพิ่มบ่อ
                        add_number_pond(farm_edit_id, new_ponds - current_ponds)
                    elif new_ponds < current_ponds:
                        # ลบบ่อที่มีสถานะเป็น empty
                        delete_empty_ponds(farm_edit_id, current_ponds - new_ponds)
            else:
                # เพิ่มฟาร์มใหม่
                insert_status = add_farms_data(farms)
                
                if insert_status:
                    # ดึง farm_id ล่าสุดที่เพิ่งเพิ่ม
                    last_farm_id = get_last_inserted_farm_id()
                    
                    # เพิ่มบ่อตามจำนวนที่ระบุ
                    add_number_pond(last_farm_id, int(farm_ponds_field.value))

            if insert_status:
                reset_main_view()

    def cancel_add_farm(e):
        reset_main_view()

    def clear_error_on_change(e):
        control = e.control
        control.border_color = None
        control.helper_style = None
        if error_text.visible:
            validate_form()

    farm_name_field.on_change = clear_error_on_change
    farm_manager_field.on_change = clear_error_on_change
    farm_ponds_field.on_change = clear_error_on_change
    farm_ring_field.on_change = clear_error_on_change
    farm_type_dropdown.on_change = clear_error_on_change
    province_field.on_change = clear_error_on_change
    district_field.on_change = clear_error_on_change

    # สร้าง UI สำหรับส่วนของที่อยู่และพิกัด
    address_section = ft.Column(
        [
            ft.Text("ระบุที่อยู่ฟาร์ม", size=16, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    address_number_field,
                    moo_field,
                ]
            ),
            ft.Row(
                [
                    subdistrict_field,
                    district_field,
                ]
            ),
            ft.Row(
                [
                    province_field,
                    postcode_field,
                ]
            ),
            base_button_normal(
                button_name="ค้นหาพิกัด",
                icon="SEARCH",
                background_color=Deep_Purple,
                text_color=White,
                on_click=search_coordinates_from_address,
            ),
            location_progress,
            location_status,
            base_empty_box(1),
            ft.Text("พิกัดที่ได้", size=14, weight=ft.FontWeight.BOLD),
            ft.Row(
                [
                    latitude_field,
                    longitude_field,
                ]
            ),
            selected_location,
        ]
    )

    add_farm_container = ft.Card(
        content=ft.Container(
            padding=10,
            content=ft.Column(
                [
                    ft.Text("เพิ่มฟาร์มใหม่", size=15, weight=ft.FontWeight.BOLD),
                    error_text,
                    ft.Container(
                        content=farm_name_field,
                    ),
                    base_empty_box(2),
                    # ใช้ address_section แทน
                    address_section,
                    base_empty_box(2),
                    ft.Container(
                        content=farm_manager_field,
                    ),
                    base_empty_box(2),
                    ft.Container(
                        content=farm_ponds_field,
                    ),
                    base_empty_box(2),
                    ft.Container(
                        content=farm_ring_field,
                    ),
                    base_empty_box(2),
                    ft.Container(
                        content=farm_type_dropdown,
                    ),
                    base_empty_box(2),
                    ft.Column(
                        [
                            base_button_gradient(
                                button_name="บันทึก", on_click=save_new_farm
                            ),
                            base_button_normal(
                                button_name="ยกเลิก",
                                on_click=cancel_add_farm,
                                background_color=White,
                                text_color=Black,
                            ),
                        ]
                    ),
                ]
            ),
        ),
        expand=True,
        color=White,
        margin=ft.margin.only(top=-10),
    )

    def add_farm(e):
        global sql_status

        sql_status = 0
        # รีเซ็ตค่าของฟิลด์เมื่อเปิดฟอร์มใหม่
        farm_name_field.value = ""
        latitude_field.value = ""
        longitude_field.value = ""
        address_number_field.value = ""
        moo_field.value = ""
        subdistrict_field.value = ""
        district_field.value = ""
        province_field.value = ""
        postcode_field.value = ""
        farm_manager_field.value = ""
        farm_ponds_field.value = ""
        farm_ring_field.value = ""
        farm_type_dropdown.value = None
        selected_location.value = "ยังไม่ได้เลือกตำแหน่ง"
        location_status.visible = False

        # รีเซ็ตสถานะของข้อความแจ้งเตือน
        error_text.visible = False
        farm_name_field.border_color = None
        latitude_field.border_color = None
        longitude_field.border_color = None
        address_number_field.border_color = None
        moo_field.border_color = None
        subdistrict_field.border_color = None
        district_field.border_color = None
        province_field.border_color = None
        postcode_field.border_color = None
        farm_manager_field.border_color = None
        farm_ponds_field.border_color = None
        farm_ring_field.border_color = None
        farm_type_dropdown.border_color = None

        farm_name_field.helper_text = ""
        latitude_field.helper_text = ""
        longitude_field.helper_text = ""
        address_number_field.helper_text = ""
        moo_field.helper_text = ""
        subdistrict_field.helper_text = ""
        district_field.helper_text = ""
        province_field.helper_text = ""
        postcode_field.helper_text = ""
        farm_manager_field.helper_text = ""
        farm_ponds_field.helper_text = ""
        farm_ring_field.helper_text = ""
        farm_type_dropdown.helper_text = ""

        farm_name_field.helper_style = None
        latitude_field.helper_style = None
        longitude_field.helper_style = None
        address_number_field.helper_style = None
        moo_field.helper_style = None
        subdistrict_field.helper_style = None
        district_field.helper_style = None
        province_field.helper_style = None
        postcode_field.helper_style = None
        farm_manager_field.helper_style = None
        farm_ponds_field.helper_style = None
        farm_ring_field.helper_style = None
        farm_type_dropdown.helper_style = None

        page_list_view.controls = [add_farm_container]
        page_list_view.update()

    """
    จบ code ส่วนการเพิ่มฟาร์ม
    """

    """
    เริ่ม code ส่วนการแก้ไขฟาร์ม
    """

    def edit_farm(farm_id):

        global sql_status
        global farm_edit_id

        sql_status = 1
        farm_edit_id = farm_id

        # ดึงข้อมูลฟาร์มตาม farm_id
        farm = get_farm_by_farm_id(farm_id)

        if farm is None:
            # ถ้าไม่พบข้อมูลฟาร์ม
            print(f"ไม่พบข้อมูลฟาร์ม ID: {farm_id}")
            return

        # รีเซ็ตสถานะของข้อความแจ้งเตือน
        error_text.visible = False

        # รีเซ็ต border และ helper text ของทุก field
        fields = [
            farm_name_field,
            latitude_field,
            longitude_field,
            address_number_field,
            moo_field,
            subdistrict_field,
            district_field,
            province_field,
            postcode_field,
            farm_manager_field,
            farm_ponds_field,
            farm_ring_field,
        ]

        for field in fields:
            field.border_color = None
            field.helper_text = ""
            field.helper_style = None

        farm_type_dropdown.border_color = None
        farm_type_dropdown.helper_text = ""
        farm_type_dropdown.helper_style = None

        # นำข้อมูลฟาร์มมาใส่ใน TextField
        farm_name_field.value = farm["farm_name"]
        farm_manager_field.value = farm["manager_name"]
        farm_ponds_field.value = str(farm["ponds_amount"])
        farm_ring_field.value = str(farm["ring_amount"])
        latitude_field.value = farm["latitude"]
        longitude_field.value = farm["longitude"]

        # ตั้งค่า farm_type_dropdown
        farm_type_dropdown.value = (
            "ฟาร์มหลัก" if farm["farm_type"] == "main" else "ฟาร์มเครือข่าย"
        )

        # แยกที่อยู่เพื่อใส่ในฟิลด์ต่างๆ
        if farm["location"]:
            location_parts = parse_address(farm["location"])

            # ใส่ข้อมูลที่อยู่ลงในฟิลด์ต่างๆ
            address_number_field.value = location_parts.get("address_number", "")
            moo_field.value = location_parts.get("moo", "")
            subdistrict_field.value = location_parts.get("subdistrict", "")
            district_field.value = location_parts.get("district", "")
            province_field.value = location_parts.get("province", "")
            postcode_field.value = location_parts.get("postcode", "")

        # อัปเดตข้อความแสดงสถานะ
        selected_location.value = f"พิกัดฟาร์ม: {farm['latitude']}, {farm['longitude']}"
        location_status.visible = False

        # แสดงฟอร์มแก้ไขฟาร์ม
        page_list_view.controls = [add_farm_container]
        page_list_view.update()

    def parse_address(address_text):
        result = {
            "address_number": "",
            "moo": "",
            "subdistrict": "",
            "district": "",
            "province": "",
            "postcode": "",
        }

        if not address_text:
            return result

        # แยกข้อความที่อยู่ตามช่องว่าง
        parts = address_text.split()

        i = 0
        while i < len(parts):
            part = parts[i]

            # บ้านเลขที่
            if i == 0 and part.isdigit():
                result["address_number"] = part

            # หมู่ ("หมู่X")
            elif part.startswith("หมู่"):
                # กรณี "หมู่X"
                if len(part) > 2 and part[4:]:
                    result["moo"] = part[4:]
                # กรณี "หมู่ X"
                elif i + 1 < len(parts) and parts[i + 4]:
                    result["moo"] = parts[i + 4]
                    i += 1  # ข้ามคำถัดไป

            # ตำบล ("ตำบลX")
            elif part.startswith("ตำบล"):
                # ตัดคำนำหน้า "ตำบล" ออก
                if len(part) > 4:
                    result["subdistrict"] = part[4:]
                # กรณีชื่อตำบลอยู่ในคำถัดไป
                elif i + 1 < len(parts) and not any(
                    parts[i + 1].startswith(prefix)
                    for prefix in ["หมู่", "อำเภอ", "จังหวัด"]
                ):
                    result["subdistrict"] = parts[i + 1]
                    i += 1  # ข้ามคำถัดไป

            # อำเภอ ("อำเภอX")
            elif part.startswith("อำเภอ"):
                # ตัดคำนำหน้า "อำเภอ" ออก
                if len(part) > 5:
                    result["district"] = part[5:]
                # กรณีชื่ออำเภออยู่ในคำถัดไป
                elif i + 1 < len(parts) and not any(
                    parts[i + 1].startswith(prefix)
                    for prefix in ["หมู่", "ตำบล", "จังหวัด"]
                ):
                    result["district"] = parts[i + 1]
                    i += 1  # ข้ามคำถัดไป

            # จังหวัด ("จังหวัดX")
            elif part.startswith("จังหวัด"):
                # ตัดคำนำหน้า "จังหวัด" ออก
                if len(part) > 7:
                    result["province"] = part[7:]
                # กรณีชื่อจังหวัดอยู่ในคำถัดไป
                elif i + 1 < len(parts) and not (
                    parts[i + 1].isdigit() and len(parts[i + 1]) == 5
                ):
                    result["province"] = parts[i + 1]
                    i += 1  # ข้ามคำถัดไป

            # รหัสไปรษณีย์ (ตัวเลข 5 หลัก)
            elif part.isdigit() and len(part) == 5:
                result["postcode"] = part

            i += 1

        # ถ้ายังไม่มีบ้านเลขที่ และมีตัวเลขอยู่ด้านหน้า (ยกเว้นหมู่และรหัสไปรษณีย์)
        if (
            not result["address_number"]
            and parts
            and parts[0].isdigit()
            and not (len(parts) > 1 and parts[1].startswith("หมู่"))
            and len(parts[0]) != 5
        ):
            result["address_number"] = parts[0]

        return result

    def delete_farm(farm_id):
        delete_status = delete_farm_by_farm_id(farm_id)
        if delete_status:
            reset_main_view()

    def manage_pond(farm_id):
        update_selected_farm_id(farm_id)
        update_hmt_page("pond_page")
        
        from pages.pond_page import pond_page
        pond_view = pond_page(farm_id)
        page_list_view.controls = [pond_view]
        page_list_view.update()

    """
    จบ code ส่วนการแก้ไขฟาร์ม
    """

    """
    เริ่ม code ส่วนการแสดงฟาร์ม
    """
    # ฟังก์ชันสร้าง UI แสดงกรณีไม่พบข้อมูล
    def create_empty_result():
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        name=ft.Icons.SEARCH_OFF_ROUNDED,
                        size=50,
                        color=Grey,
                    ),
                    ft.Text(
                        "ไม่พบข้อมูลฟาร์ม",
                        color=Grey,
                        size=14,
                        italic=True,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            height=200,
            alignment=ft.alignment.center,
        )

    def get_all_farm_info():
        farms = get_all_farm()
        farm_elements = [
            ft.Row(
                [
                    ft.Text(
                        "รายการฟาร์มทั้งหมด",
                        color=Black,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                    )
                ]
            )
        ]

        if farms:
            for farm in farms:
                farm_card = ft.Container(
                    content=ft.Column(
                        [
                            # แถวบนสุด: ชื่อฟาร์มและปุ่มดำเนินการ
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(
                                            farm["farm_name"],
                                            color=Black,
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        margin=ft.margin.only(left=13),
                                    ),
                                    ft.Row(
                                        [
                                            ft.Container(
                                                content=ft.IconButton(
                                                    icon=ft.Icons.EDIT_OUTLINED,
                                                    icon_color=Grey,
                                                    tooltip="แก้ไขข้อมูล",
                                                    icon_size=13,
                                                    on_click=lambda e, id=farm[
                                                        "farm_id"
                                                    ]: edit_farm(id),
                                                ),
                                                margin=ft.margin.only(left=-10, right=-10),
                                            ),
                                            ft.Container(
                                                content=ft.IconButton(
                                                    icon=ft.Icons.DELETE_OUTLINE,
                                                    icon_color=Grey,
                                                    tooltip="ลบฟาร์ม",
                                                    icon_size=13,
                                                    on_click=lambda e, id=farm[
                                                        "farm_id"
                                                    ]: delete_farm(id),
                                                ),
                                                margin=ft.margin.only(left=-10, right=5),
                                            ),
                                        ]
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            # แถวที่สอง: ที่อยู่พร้อมไอคอน
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(
                                            name=ft.Icons.LOCATION_ON_OUTLINED,
                                            color=Grey,
                                            size=15,
                                        ),
                                        ft.Text(
                                            farm.get("location").split()[4],
                                            color=Grey,
                                            size=13,
                                            no_wrap=False,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                margin=ft.margin.only(left=15, top=-15, bottom=5),
                            ),
                            # แถวที่สาม: ชื่อผู้จัดการพร้อมไอคอน
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.Icon(
                                            name=ft.Icons.PERSON_OUTLINE,
                                            color=Grey,
                                            size=15,
                                        ),
                                        ft.Text(
                                            f"ผู้จัดการ: {farm.get('manager_name')}",
                                            color=Grey,
                                            size=13,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                margin=ft.margin.only(left=15, top=-15, bottom=5),
                            ),
                            # แถวที่สี่: ข้อมูลบ่อเลี้ยงและห่วงขา
                            ft.Container(
                                content=ft.Row(
                                    [
                                        # จำนวนบ่อ
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text("จำนวนบ่อ", color=Grey, size=13),
                                                    ft.Container(
                                                        content=ft.Text(
                                                            str(farm.get("ponds_amount")),
                                                            color=Black,
                                                            size=15,
                                                            weight=ft.FontWeight.BOLD,
                                                            text_align=ft.TextAlign.CENTER,
                                                        ),
                                                        margin=ft.margin.only(
                                                            top=-10, bottom=-7
                                                        ),
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            expand=True,
                                            alignment=ft.alignment.center,
                                        ),
                                        # บ่อที่ใช้งาน (สมมติค่า 80% ของบ่อทั้งหมด)
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text(
                                                        "บ่อที่ใช้งาน", color=Grey, size=13
                                                    ),
                                                    ft.Container(
                                                        content=ft.Text(
                                                            str(int(farm.get("ponds_use"))),
                                                            color=Black,
                                                            size=15,
                                                            weight=ft.FontWeight.BOLD,
                                                            text_align=ft.TextAlign.CENTER,
                                                        ),
                                                        margin=ft.margin.only(
                                                            top=-10, bottom=-7
                                                        ),
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            expand=True,
                                            alignment=ft.alignment.center,
                                        ),
                                        # จำนวนหนู
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text("จำนวนหนู", color=Grey, size=13),
                                                    ft.Container(
                                                        content=ft.Text(
                                                            str(farm.get("ring_amount")),
                                                            color=Black,
                                                            size=15,
                                                            weight=ft.FontWeight.BOLD,
                                                            text_align=ft.TextAlign.CENTER,
                                                        ),
                                                        margin=ft.margin.only(
                                                            top=-10, bottom=-7
                                                        ),
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            expand=True,
                                            alignment=ft.alignment.center,
                                        ),
                                    ]
                                ),
                                margin=ft.margin.only(left=15, top=-10, bottom=5),
                            ),
                            # ปุ่มจัดการบ่อเลี้ยง
                            ft.Container(
                                content=base_button_gradient_v2(
                                    button_name="จัดการบ่อเลี้ยง", 
                                    on_click=lambda e, id=farm["farm_id"]: manage_pond(id)
                                )
                            ),
                        ]
                    ),
                    # padding=15,
                    margin=ft.margin.only(bottom=15),
                    border_radius=10,
                    bgcolor=White,
                    shadow=ft.BoxShadow(
                        spread_radius=0.1, blur_radius=4, color=Grey, offset=ft.Offset(0, 0)
                    ),
                )

                farm_elements.append(farm_card)
        else:
            # ถ้าไม่มีฟาร์มใดๆ ให้แสดงข้อความว่าไม่พบข้อมูล
            farm_elements.append(create_empty_result())

        return farm_elements

    def overview_information():
        overview_content = [
            ft.Column(
                [
                    ft.Text(
                        "ภาพรวมฟาร์มทั้งหมด",
                        color=Black,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        base_info_report_box_v2(
                                            topic="จำนวนฟาร์มทั้งหมด",
                                            content=get_amount_farm(),
                                            color=Deep_Purple,
                                        ),
                                        base_empty_box(2),
                                        base_info_report_box_v2(
                                            topic="บ่อเลี้ยงทั้งหมด",
                                            content=get_amount_pond(),
                                            color=Neo_Mint,
                                        ),
                                    ]
                                ),
                                ft.Row(
                                    [
                                        base_info_report_box_v2(
                                            topic="จำนวนหนูทั้งหมด",
                                            content=get_amount_rat(),
                                            color=Deep_Purple,
                                        ),
                                        base_empty_box(2),
                                        base_info_report_box_v2(
                                            topic="อัตราการใช้งานบ่อ",
                                            content=get_pond_use_rate(),
                                            color=Neo_Mint,
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        bgcolor=White,
                        padding=15,
                        border_radius=10,
                        shadow=ft.BoxShadow(
                            spread_radius=0.1,
                            blur_radius=3,
                            color=Grey,
                            offset=ft.Offset(0.1, 0.1),
                        ),
                    ),
                ]
            )
        ]

        return overview_content

    main_container = ft.Column(
        [
            base_button_gradient(
                button_name="เพิ่มฟาร์มใหม่", icon="ADD_CIRCLE_OUTLINE", on_click=add_farm
            ),
        ],
        expand=True,
    )

    controls = [main_container]
    controls.extend(get_all_farm_info())
    controls.extend(overview_information())

    """
    จบ code ส่วนการแสดงฟาร์ม
    """

    page_list_view.controls = controls

    def reset_main_view():
        controls = [main_container]
        controls.extend(get_all_farm_info())
        controls.extend(overview_information())

        page_list_view.controls = controls
        page_list_view.update()

    return page_list_view
