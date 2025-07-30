from datetime import date, datetime
import threading
import flet as ft

from components.base_button import (
    base_button_gradient,
    base_button_gradient_v2,
    base_button_normal,
)
from main_calculate.advice_breed import calculate_inbreeding_coefficient, get_pair_breeding_by_basic_data
from pages.breeding_ad import breeding_ad
from storages.database_service import (
    add_breed_data,
    auto_manage_breeding_after_success,
    check_breed_exists,
    get_breed_by_breeding_id,
    get_breed_information,
    get_breeding_by_date,
    get_rat_id_by_ring_number,
    update_breed_data,
    update_pond_status,
    update_rat_pond,
    update_rat_status,
)
from storages.general_information import check_gender, check_pond_used, check_ring_used
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, White


def breeding_page():

    global is_valid
    global is_editing
    global edit_breeding_id
    is_valid = False

    text_style = ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=Grey)

    error_text_all = ft.Text(
        "",
        color=ft.Colors.RED_500,
        size=12,
        visible=False,
    )
    error_text_path1 = ft.Text(
        "",
        color=ft.Colors.RED_500,
        size=12,
        visible=False,
    )

    # สร้างตัวแปรสำหรับเก็บค่า input
    father_ring_number_filld = ft.TextField(
        label="เลขห่วงขาพ่อพันธุ์",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    mother_ring_number_filld = ft.TextField(
        label="เลขห่วงขาแม่พันธุ์",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    pond_number_filld = ft.TextField(
        label="บ่อเลี้ยง",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    inbreeding_coff_filld = ft.TextField(
        label="อัตราเลือดชิด",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        read_only=True,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        bgcolor=ft.Colors.GREY_200,
    )

    breed_date_filld = ft.TextField(
        label="วันที่เริ่ม",
        hint_text="เช่น 2023-05-20",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    born_date_filld = ft.TextField(
        label="วันที่คลอดลูก",
        hint_text="เช่น 2023-05-20",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    status_dropdown = ft.Dropdown(
        label="สถานะ",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        options=[
            ft.dropdown.Option("breeding", "กำลังผสมพันธุ์"),
            ft.dropdown.Option("success", "สำเร็จ"),
            ft.dropdown.Option("unsuccess", "ล้มเหลว"),
            ft.dropdown.Option("disorders", "ผสมแล้วได้หนูเผือก"),
        ],
    )

    normal_born_filld = ft.TextField(
        label="จำนวนที่ได้",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    abnormal_born_filld = ft.TextField(
        label="ผิดปกติ",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    dead_born_filld = ft.TextField(
        label="ตาย",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    end_breeding_filld = ft.TextField(
        label="วันที่แยกคู่",
        hint_text="เช่น 2023-05-20",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    fields = [
        father_ring_number_filld,
        mother_ring_number_filld,
        pond_number_filld,
        inbreeding_coff_filld,
        breed_date_filld,
        born_date_filld,
        status_dropdown,
        normal_born_filld,
        abnormal_born_filld,
        dead_born_filld,
        end_breeding_filld,
    ]

    def check_pair_compatibility(male_ring_number, female_ring_number):
        """
        ตรวจสอบว่าคู่ผสมที่เลือกผ่านเกณฑ์พื้นฐานหรือไม่
        โดยใช้ข้อมูลจาก get_pair_breeding_by_basic_data
        
        Args:
            male_ring_number: หมายเลขห่วงขาพ่อ
            female_ring_number: หมายเลขห่วงขาแม่
        
        Returns:
            dict: {
                'is_compatible': bool,
                'error_message': str,
                'pair_info': dict หรือ None
            }
        """
        try:
            # ดึงข้อมูล rat_id จาก ring number
            male_rat_id = get_rat_id_by_ring_number(male_ring_number)
            female_rat_id = get_rat_id_by_ring_number(female_ring_number)
            
            if not male_rat_id or not female_rat_id:
                return {
                    'is_compatible': False,
                    'error_message': 'ไม่พบข้อมูลหนูในระบบ',
                    'pair_info': None
                }
            
            # ดึงข้อมูลคู่ผสมที่เป็นไปได้ทั้งหมด
            breeding_data = get_pair_breeding_by_basic_data()
            
            if not breeding_data:
                return {
                    'is_compatible': False,
                    'error_message': 'เกิดข้อผิดพลาดในการดึงข้อมูลคู่ผสม',
                    'pair_info': None
                }
            
            # รวมคู่ผสมทั้งหมด (same_farm + different_farm)
            all_pairs = breeding_data['same_farm'] + breeding_data['different_farm']
            
            # ค้นหาคู่ที่ตรงกับที่เลือก
            target_pair = None
            for pair in all_pairs:
                if (pair['male']['id'] == male_rat_id and 
                    pair['female']['id'] == female_rat_id):
                    target_pair = pair
                    break
            
            if target_pair:
                return {
                    'is_compatible': True,
                    'error_message': '',
                    'pair_info': target_pair
                }
            else:
                return {
                    'is_compatible': False,
                    'error_message': 'คู่ผสมนี้ไม่ผ่านเกณฑ์พื้นฐาน (อาจเป็นเลือดชิด, ขนาดไม่เหมาะสม, หรือมีประวัติปัญหา)',
                    'pair_info': None
                }
                
        except Exception as e:
            return {
                'is_compatible': False,
                'error_message': f'เกิดข้อผิดพลาดในการตรวจสอบ: {str(e)}',
                'pair_info': None
            }


    def on_breeding_change(e):
        global is_valid
        father_ring_number = father_ring_number_filld.value
        mother_ring_number = mother_ring_number_filld.value
        pond_number = pond_number_filld.value

        # รีเซ็ตค่าเริ่มต้น
        is_valid = False
        error_text_path1.value = ""
        error_text_path1.visible = False

        # ตรวจสอบห่วงขาพ่อ
        if father_ring_number:
            if not check_ring_used(None, father_ring_number):
                error_text_path1.value = "ไม่พบข้อมูลหนูพ่อพันธุ์"
                error_text_path1.visible = True
                is_valid = True
                error_text_path1.update()
                return
            elif not check_gender(father_ring_number, "male"):
                error_text_path1.value = "หมายเลขห่วงขาไม่ใช่พ่อพันธุ์"
                error_text_path1.visible = True
                is_valid = True
                error_text_path1.update()
                return
            elif check_breed_exists(father_ring_number):
                error_text_path1.value = "พ่อพันธุ์นี้มีการผสมพันธุ์อยู่แล้ว"
                error_text_path1.visible = True
                is_valid = True
                error_text_path1.update()
                return

        # ตรวจสอบห่วงขาแม่
        if mother_ring_number:
            if not check_ring_used(None, mother_ring_number):
                error_text_path1.value = "ไม่พบข้อมูลหนูแม่พันธุ์"
                error_text_path1.visible = True
                is_valid = True
                error_text_path1.update()
                return
            elif not check_gender(mother_ring_number, "female"):
                error_text_path1.value = "หมายเลขห่วงขาไม่ใช่แม่พันธุ์"
                error_text_path1.visible = True
                is_valid = True
                error_text_path1.update()
                return
            elif check_breed_exists(mother_ring_number):
                error_text_path1.value = "แม่พันธุ์นี้มีการผสมพันธุ์อยู่แล้ว"
                error_text_path1.visible = True
                is_valid = True
                error_text_path1.update()
                return

        # ตรวจสอบบ่อ
        if pond_number:
            if not check_pond_used(pond_number):
                error_text_path1.value = "หมายเลขบ่อถูกใช้ไปแล้ว"
                error_text_path1.visible = True
                is_valid = True
                error_text_path1.update()
                return

        # ตรวจสอบความเข้ากันได้ของคู่ผสม (เมื่อมีทั้งพ่อและแม่)
        if father_ring_number and mother_ring_number:
            try:
                # ใช้ function ใหม่ที่เรียกใช้ get_pair_breeding_by_basic_data
                compatibility_result = check_pair_compatibility(
                    father_ring_number, mother_ring_number
                )
                
                if not compatibility_result['is_compatible']:
                    error_text_path1.value = compatibility_result['error_message']
                    error_text_path1.visible = True
                    is_valid = True
                    error_text_path1.update()
                    return
                
                # ถ้าผ่านเกณฑ์ แสดงข้อมูลเพิ่มเติม
                pair_info = compatibility_result['pair_info']
                if pair_info:
                    inbreeding_rate = pair_info['inbreeding_coef']
                    size_diff = pair_info['size_diff_percent']
                    
                    # อัพเดตค่าในฟิลด์
                    inbreeding_coff_filld.value = f"{inbreeding_rate:.4f}"
                    inbreeding_coff_filld.update()
                    
                    # แสดงข้อมูลเพิ่มเติม (ถ้ามีฟิลด์สำหรับแสดง)
                    # size_diff_field.value = f"{size_diff:.2f}%"
                    
                    print(f"คู่ผสมผ่านเกณฑ์: Inbreeding = {inbreeding_rate:.4f}, Size diff = {size_diff:.2f}%")

                # ถ้าผ่านเกณฑ์ทั้งหมด
                error_text_path1.value = ""
                error_text_path1.visible = False
                is_valid = False  # ไม่มี error (valid)

            except Exception as ex:
                error_text_path1.value = f"เกิดข้อผิดพลาดในการตรวจสอบคู่ผสม: {str(ex)}"
                error_text_path1.visible = True
                is_valid = True
                error_text_path1.update()
                return

        # ถ้าไม่มี error ใดๆ
        if not father_ring_number or not mother_ring_number or not pond_number:
            # ยังกรอกข้อมูลไม่ครบ
            is_valid = True  # ยังไม่พร้อมส่งข้อมูล
        else:
            # ข้อมูลครบและผ่านเกณฑ์ทั้งหมด
            is_valid = False  # พร้อมส่งข้อมูล

        error_text_path1.update()

    father_ring_number_filld.on_change = on_breeding_change
    mother_ring_number_filld.on_change = on_breeding_change
    pond_number_filld.on_change = on_breeding_change

    def on_status_change(e):
        if status_dropdown.value == "unsuccess":
            normal_born_filld.value = "0"
            abnormal_born_filld.value = "0"
            dead_born_filld.value = "0"
            born_date_filld.value = ""
            end_breeding_filld.value = ""
            normal_born_filld.read_only = True
            abnormal_born_filld.read_only = True
            dead_born_filld.read_only = True
            born_date_filld.read_only = True
            end_breeding_filld.read_only = True
            normal_born_filld.bgcolor = ft.Colors.GREY_200
            abnormal_born_filld.bgcolor = ft.Colors.GREY_200
            dead_born_filld.bgcolor = ft.Colors.GREY_200
            born_date_filld.bgcolor = ft.Colors.GREY_200
            end_breeding_filld.bgcolor = ft.Colors.GREY_200
        else:
            normal_born_filld.value = ""
            abnormal_born_filld.value = ""
            dead_born_filld.value = ""
            born_date_filld.value = ""
            end_breeding_filld.value = ""
            normal_born_filld.read_only = False
            abnormal_born_filld.read_only = False
            dead_born_filld.read_only = False
            born_date_filld.read_only = False
            end_breeding_filld.read_only = False
            normal_born_filld.bgcolor = White
            abnormal_born_filld.bgcolor = White
            dead_born_filld.bgcolor = White
            born_date_filld.bgcolor = White
            end_breeding_filld.bgcolor = White

        list_view.update()

    status_dropdown.on_change = on_status_change

    def save_breeding_data(e):
        if validate_input():
            print(validate_input())
            error_text_all.value = "กรุณากรอกข้อมูลให้ถูกต้อง"
            error_text_all.visible = True
        else:
            error_text_all.value = ""
            error_text_all.visible = False

            breeding_data = (
                get_rat_id_by_ring_number(father_ring_number_filld.value),
                get_rat_id_by_ring_number(mother_ring_number_filld.value),
                pond_number_filld.value,
                float(inbreeding_coff_filld.value),
                status_dropdown.value,
                breed_date_filld.value,
            )

            if add_breed_data(breeding_data):
                update_rat_pond(get_rat_id_by_ring_number(father_ring_number_filld.value), pond_number_filld.value),
                update_rat_pond(get_rat_id_by_ring_number(mother_ring_number_filld.value), pond_number_filld.value),
                update_rat_status(get_rat_id_by_ring_number(father_ring_number_filld.value), 'breeder1'),
                update_rat_status(get_rat_id_by_ring_number(mother_ring_number_filld.value), 'breeder1'),
                update_pond_status(1, pond_number_filld.value, 'work')
                print("บันทึกข้อมูลการผสมพันธุ์สำเร็จ")
            else:
                # บันทึกไม่สำเร็จ
                error_text_all.value = "ไม่สามารถบันทึกข้อมูลได้ กรุณาตรวจสอบข้อมูลอีกครั้ง"
                error_text_all.visible = True

        error_text_all.update()

    def cancel_add_breeding(e):
        global is_editing
        is_editing = False
        global edit_breeding_id
        edit_breeding_id = None
        list_view.controls = [build_main_content()]
        list_view.update()

    # ฟังก์ชันตรวจสอบรูปแบบวันที่
    def validate_date(date_value):
        # ถ้าเป็น datetime.date หรือ datetime.datetime อยู่แล้ว
        if isinstance(date_value, (datetime, date)):
            return True

        # ถ้าเป็น string ให้ลองแปลงเป็น datetime
        if isinstance(date_value, str):
            try:
                datetime.strptime(date_value, "%Y-%m-%d")
                return True
            except ValueError:
                return False

        # ถ้าไม่ใช่ทั้ง datetime หรือ string ที่ถูกต้อง
        return False

    def validate_input():
        global is_valid
        is_valid = False

        # กำหนดรายการฟิลด์ที่ต้องการตรวจสอบ (ส่วนแรก - บังคับเสมอ)
        required_fields = {
            father_ring_number_filld: "",
            mother_ring_number_filld: "",
            pond_number_filld: "",
            breed_date_filld: "",
        }

        # ตรวจสอบฟิลด์บังคับ
        has_required_error = False
        for field, error_message in required_fields.items():
            if not field.value:
                field.border_color = ft.Colors.RED_500
                field.helper_text = error_message
                field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                has_required_error = True
            else:
                field.border_color = None
                field.helper_text = ""
                field.helper_style = None

        # ตรวจสอบรูปแบบวันที่ผสม
        if breed_date_filld.value and not validate_date(breed_date_filld.value):
            breed_date_filld.border_color = ft.Colors.RED_500
            breed_date_filld.helper_text = "รูปแบบวันที่ไม่ถูกต้อง (ปี-เดือน-วัน)"
            breed_date_filld.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            has_required_error = True

        # ตรวจสอบว่ามีการกรอกจำนวนลูกอย่างน้อย 1 ฟิลด์หรือไม่
        birth_fields = [normal_born_filld, abnormal_born_filld, dead_born_filld]
        has_birth_data = any(field.value for field in birth_fields)

        # ถ้ามีการกรอกจำนวนลูก ให้ตรวจสอบฟิลด์ที่เหลือ
        if has_birth_data:
            # กำหนดรายการฟิลด์ที่ต้องการตรวจสอบ ส่วนที่เหลือ (เมื่อมีข้อมูลลูก)
            optional_required_fields = {
                normal_born_filld: "",
                abnormal_born_filld: "",
                dead_born_filld: "",
                born_date_filld: "",
                end_breeding_filld: "",
            }

            has_birth_error = False
            for field, error_message in optional_required_fields.items():
                if not field.value:
                    field.border_color = ft.Colors.RED_500
                    field.helper_text = error_message
                    field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                    has_birth_error = True
                else:
                    field.border_color = None
                    field.helper_text = ""
                    field.helper_style = None

            # ตรวจสอบรูปแบบวันที่คลอด
            if born_date_filld.value and not validate_date(born_date_filld.value):
                born_date_filld.border_color = ft.Colors.RED_500
                born_date_filld.helper_text = "รูปแบบวันที่ไม่ถูกต้อง (ปี-เดือน-วัน)"
                born_date_filld.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                has_birth_error = True

            # ตรวจสอบรูปแบบวันที่สิ้นสุดการผสม
            if end_breeding_filld.value and not validate_date(end_breeding_filld.value):
                end_breeding_filld.border_color = ft.Colors.RED_500
                end_breeding_filld.helper_text = "รูปแบบวันที่ไม่ถูกต้อง (ปี-เดือน-วัน)"
                end_breeding_filld.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                has_birth_error = True

            # ตรวจสอบว่าจำนวนลูกเป็นตัวเลขหรือไม่
            for field in birth_fields:
                if field.value:
                    try:
                        int(field.value)
                        field.border_color = None
                        field.helper_text = ""
                        field.helper_style = None
                    except ValueError:
                        field.border_color = ft.Colors.RED_500
                        field.helper_text = "กรุณากรอกตัวเลขเท่านั้น"
                        field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                        has_birth_error = True

            # กำหนดค่า is_valid สำหรับกรณีที่มีข้อมูลลูก
            is_valid = has_required_error or has_birth_error

        else:
            # ถ้าไม่มีการกรอกจำนวนลูก ให้รีเซ็ตฟิลด์ที่เกี่ยวข้องกับการคลอด
            birth_related_fields = [
                normal_born_filld,
                abnormal_born_filld,
                dead_born_filld,
                born_date_filld,
                end_breeding_filld,
            ]
            for field in birth_related_fields:
                field.border_color = None
                field.helper_text = ""
                field.helper_style = None

            # กำหนดค่า is_valid สำหรับกรณีที่ไม่มีข้อมูลลูก (ตรวจเฉพาะฟิลด์บังคับ)
            is_valid = has_required_error

        list_view.update()
        return is_valid

    def add_breeding():
        status_dropdown.value = "breeding"

        today = date.today()
        date_prefix = today.strftime("%Y-%m-%d")
        breed_date_filld.value = date_prefix

        breeding_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text("เพิ่มการผสมพันธุ์", size=18, weight=ft.FontWeight.BOLD),
                    error_text_all,
                    ft.Divider(),
                    ft.Text("ข้อมูลการผสมพันธุ์", size=14, weight=ft.FontWeight.BOLD),
                    error_text_path1,
                    ft.Row(
                        [
                            father_ring_number_filld,
                            mother_ring_number_filld,
                        ]
                    ),
                    ft.Row(
                        [
                            pond_number_filld,
                            inbreeding_coff_filld,
                        ]
                    ),
                    ft.Row(
                        [
                            status_dropdown,
                        ]
                    ),
                    ft.Row(
                        [
                            breed_date_filld,
                        ]
                    ),
                    ft.Divider(),
                    ft.Text("ลูกที่คลอด", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            normal_born_filld,
                            abnormal_born_filld,
                            dead_born_filld,
                        ]
                    ),
                    born_date_filld,
                    end_breeding_filld,
                    base_button_gradient(
                        button_name="บันทึก", on_click=lambda e: save_breeding_data(e)
                    ),
                    base_button_normal(
                        button_name="ยกเลิก",
                        on_click=lambda e: cancel_add_breeding(e),
                        background_color=White,
                        text_color=Black,
                    ),
                ]
            ),
        )

        return ft.Card(
            content=ft.Container(
                padding=20,
                content=breeding_content,
            ),
            expand=True,
            color=White,
            margin=ft.margin.only(top=-10),
        )

    def build_breeding_content(e):

        for field in fields:
            field.value = ""
            field.border_color = None
            field.helper_text = ""
            field.helper_style = None

        error_text_all.value = ""
        error_text_all.visible = False

        list_view.controls = [add_breeding()]
        list_view.update()

    def recommend_breeding(e):
        list_view.controls = [breeding_ad()]
        list_view.update()

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
                        "ไม่พบข้อมูลการผสมพันธุ์ตามเงื่อนไขที่กำหนด",
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

    def create_breeding_card():
        # ตัวแปรสถานะการแสดง filter
        is_filter_expanded = False

        # ===== DEFINE ฟังก์ชัน toggle_filter ก่อน =====
        def toggle_filter(e):
            nonlocal is_filter_expanded
            is_filter_expanded = not is_filter_expanded
            filter_ui.visible = is_filter_expanded
            filter_toggle_button.icon = (
                ft.Icons.KEYBOARD_ARROW_UP
                if is_filter_expanded
                else ft.Icons.KEYBOARD_ARROW_DOWN
            )
            breeding_cards_column.update()
            filter_ui.update()

        # ตัวแปรสำหรับ filter
        start_date_field = ft.TextField(
            label="วันที่เริ่มต้น",
            hint_text="2025-01-01",
            text_style=ft.TextStyle(size=16, color=Grey),
            label_style=ft.TextStyle(size=14, color=Grey),
            dense=True,
        )

        end_date_field = ft.TextField(
            label="วันที่สิ้นสุด",
            hint_text="2025-12-31",
            text_style=ft.TextStyle(size=16, color=Grey),
            label_style=ft.TextStyle(size=14, color=Grey),
            dense=True,
        )

        def apply_filter(e):
            # ดึงข้อมูลใหม่ตามช่วงวันที่
            start_date = start_date_field.value
            end_date = end_date_field.value

            # ดึงข้อมูลการผสมพันธุ์ (ตรงนี้อาจต้องส่ง parameter ไปยัง get_breed_information)
            breeding_data = get_breeding_by_date(
                start_date=start_date, end_date=end_date
            )

            # อัพเดทการ์ด
            update_breeding_cards(breeding_data)

        def reset_filter(e):
            # รีเซ็ตฟิลด์
            start_date_field.value = ""
            end_date_field.value = ""

            # ดึงข้อมูลทั้งหมด
            breeding_data = get_breed_information()
            update_breeding_cards(breeding_data)

            start_date_field.update()
            end_date_field.update()

        def update_breeding_cards(breeding_data):
            # ล้างการ์ดเก่า (เก็บเฉพาะ header)
            breeding_cards_list.clear()

            # สร้างการ์ดใหม่
            for breed in breeding_data:
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Text(
                                                f"การผสมพันธุ์ที่: {breed['breeding_id']}",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            padding=ft.padding.only(top=10, left=10),
                                        )
                                    ]
                                ),
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text(
                                                        "พ่อพันธุ์", size=11, color=Grey
                                                    ),
                                                    ft.Text(
                                                        f"{breed['father_ring_id']}",
                                                        size=12,
                                                        color=Black,
                                                    ),
                                                ]
                                            ),
                                            expand=True,
                                            border_radius=5,
                                            padding=10,
                                            margin=ft.margin.only(left=10),
                                            bgcolor=White,
                                            shadow=ft.BoxShadow(
                                                spread_radius=1,
                                                blur_radius=1,
                                                color=ft.Colors.GREY_300,
                                                offset=ft.Offset(0, 1),
                                            ),
                                        ),
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text(
                                                        "แม่พันธุ์", size=11, color=Grey
                                                    ),
                                                    ft.Text(
                                                        f"{breed['mother_ring_id']}",
                                                        size=12,
                                                        color=Black,
                                                    ),
                                                ]
                                            ),
                                            expand=True,
                                            border_radius=5,
                                            padding=10,
                                            margin=ft.margin.only(right=10),
                                            bgcolor=White,
                                            shadow=ft.BoxShadow(
                                                spread_radius=1,
                                                blur_radius=1,
                                                color=ft.Colors.GREY_300,
                                                offset=ft.Offset(0, 1),
                                            ),
                                        ),
                                    ]
                                ),
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"บ่อเลี้ยง: {breed['pond_id']}",
                                            color=Grey,
                                            size=11,
                                        ),
                                        ft.Text(
                                            f"อัตราเลือดชิด: {breed['inbreeding_rate']}",
                                            color=Grey,
                                            size=11,
                                        ),
                                        ft.Text(
                                            f"วันที่เริ่มผสมพันธุ์: {breed['breeding_date']}",
                                            color=Grey,
                                            size=11,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                ),
                                ft.Container(
                                    content=base_button_gradient_v2(
                                        button_name="ดูรายละเอียด",
                                        on_click=lambda e, breeding_id=breed[
                                            "breeding_id"
                                        ]: show_edit_breeding(breeding_id),
                                    )
                                ),
                            ],
                            spacing=5,
                        ),
                    ),
                    expand=True,
                    color=White,
                    margin=ft.margin.only(bottom=10),
                )
                breeding_cards_list.append(card)

            # อัพเดท UI
            breeding_cards_column.controls = [
                ft.Row(
                    [ft.Text("ตัวกรอง", size=12, color=Grey), filter_toggle_button],
                    alignment=ft.MainAxisAlignment.END,
                ),
                filter_ui,
                *(breeding_cards_list if breeding_cards_list else [create_empty_result()]),
            ]
            breeding_cards_column.update()

        # ===== สร้างปุ่ม toggle หลังจาก define ฟังก์ชันแล้ว =====
        filter_toggle_button = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_DOWN,
            icon_color=Grey,
            icon_size=20,
            on_click=toggle_filter,
            tooltip="เปิด/ปิดตัวกรอง",
        )

        # สร้าง UI ส่วนตัวกรอง
        filter_ui = ft.Container(
            content=ft.Column(
                [
                    ft.Text("วันที่ผสมพันธุ์", size=13, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.Container(
                                content=start_date_field,
                                expand=True,
                            ),
                            ft.Text("-", size=16, color=Grey),
                            ft.Container(
                                content=end_date_field,
                                expand=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=base_button_normal(
                                    button_name="นำไปใช้",
                                    on_click=apply_filter,
                                    background_color=Neo_Mint,
                                    text_color=White,
                                ),
                                expand=True,
                            ),
                            ft.Container(
                                content=base_button_normal(
                                    button_name="รีเซ็ต",
                                    on_click=reset_filter,
                                    background_color=White,
                                    text_color=Black,
                                ),
                                expand=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ]
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=10,
            expand=True,
            margin=ft.margin.only(bottom=15, left=5, right=5),
            shadow=ft.BoxShadow(
                spread_radius=0.1, blur_radius=4, color=Grey, offset=ft.Offset(0, 0)
            ),
            visible=is_filter_expanded,
        )

        # ดึงข้อมูลการผสมพันธุ์
        breeding_data = get_breed_information()

        # สร้างรายการการ์ด
        breeding_cards_list = []

        for breed in breeding_data:
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(
                                            f"การผสมพันธุ์ที่: {breed['breeding_id']}",
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        padding=ft.padding.only(top=10, left=10),
                                    )
                                ]
                            ),
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("พ่อพันธุ์", size=11, color=Grey),
                                                ft.Text(
                                                    f"{breed['father_ring_id']}",
                                                    size=12,
                                                    color=Black,
                                                ),
                                            ]
                                        ),
                                        expand=True,
                                        border_radius=5,
                                        padding=10,
                                        margin=ft.margin.only(left=10),
                                        bgcolor=White,
                                        shadow=ft.BoxShadow(
                                            spread_radius=1,
                                            blur_radius=1,
                                            color=ft.Colors.GREY_300,
                                            offset=ft.Offset(0, 1),
                                        ),
                                    ),
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("แม่พันธุ์", size=11, color=Grey),
                                                ft.Text(
                                                    f"{breed['mother_ring_id']}",
                                                    size=12,
                                                    color=Black,
                                                ),
                                            ]
                                        ),
                                        expand=True,
                                        border_radius=5,
                                        padding=10,
                                        margin=ft.margin.only(right=10),
                                        bgcolor=White,
                                        shadow=ft.BoxShadow(
                                            spread_radius=1,
                                            blur_radius=1,
                                            color=ft.Colors.GREY_300,
                                            offset=ft.Offset(0, 1),
                                        ),
                                    ),
                                ]
                            ),
                            ft.Row(
                                [
                                    ft.Text(
                                        f"บ่อเลี้ยง: {breed['pond_id']}",
                                        color=Grey,
                                        size=11,
                                    ),
                                    ft.Text(
                                        f"อัตราเลือดชิด: {breed['inbreeding_rate']}",
                                        color=Grey,
                                        size=11,
                                    ),
                                    ft.Text(
                                        f"วันที่เริ่มผสมพันธุ์: {breed['breeding_date']}",
                                        color=Grey,
                                        size=11,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                            ),
                            ft.Container(
                                content=base_button_gradient_v2(
                                    button_name="ดูรายละเอียด",
                                    on_click=lambda e, breeding_id=breed[
                                        "breeding_id"
                                    ]: show_edit_breeding(breeding_id),
                                )
                            ),
                        ],
                        spacing=5,
                    ),
                ),
                expand=True,
                color=White,
                margin=ft.margin.only(bottom=10),
            )
            breeding_cards_list.append(card)

        # สร้าง Column หลัก
        breeding_cards_column = ft.Column(
            [
                ft.Row(
                    [ft.Text("ตัวกรอง", size=12, color=Grey), filter_toggle_button],
                    alignment=ft.MainAxisAlignment.END,
                ),
                filter_ui,
                *(breeding_cards_list if breeding_cards_list else [create_empty_result()]),
            ],
            expand=True,
        )

        return breeding_cards_column

    def show_edit_breeding(breeding_id):
        """ฟังก์ชันสำหรับแสดงหน้าแก้ไขการผสมพันธุ์"""
        global is_editing, edit_breeding_id
        is_editing = True
        edit_breeding_id = breeding_id

        # สร้างหน้าแก้ไข
        edit_card = build_edit_breeding_content(breeding_id)

        # อัพเดท list_view
        list_view.controls = [edit_card]
        list_view.update()

    def build_edit_breeding_content(breeding_id):
        """สร้างการ์ดสำหรับแก้ไขการผสมพันธุ์ (สไตล์เหมือนการเพิ่ม)"""
        print(f"แก้ไขการผสมพันธุ์ ID: {breeding_id}")

        # ดึงข้อมูลการผสมพันธุ์ที่ต้องการแก้ไข
        breeding_data = get_breed_by_breeding_id(breeding_id)

        # รีเซ็ต error messages
        error_text_all.value = ""
        error_text_all.visible = False
        error_text_path1.value = ""
        error_text_path1.visible = False

        # กรอกข้อมูลในฟิลด์ต่างๆ
        father_ring_number_filld.value = str(breeding_data.get("father_ring_id", ""))
        mother_ring_number_filld.value = str(breeding_data.get("mother_ring_id", ""))
        pond_number_filld.value = str(breeding_data.get("pond_id", ""))
        inbreeding_coff_filld.value = (
            f"{float(breeding_data.get('inbreeding_rate', 0)):.2f}"
        )
        status_dropdown.value = breeding_data.get("breeding_status", "breeding")
        breed_date_filld.value = str(breeding_data.get("breeding_date", ""))

        # ข้อมูลการคลอด (อาจเป็น None หรือ 0)
        normal_born_filld.value = str(
            breeding_data.get("survived_pups", "")
            if breeding_data.get("survived_pups")
            else ""
        )
        abnormal_born_filld.value = str(
            breeding_data.get("albino_pups", "")
            if breeding_data.get("albino_pups")
            else ""
        )
        dead_born_filld.value = str(
            breeding_data.get("dead_pups", "") if breeding_data.get("dead_pups") else ""
        )
        born_date_filld.value = str(
            breeding_data.get("birth_date", "")
            if breeding_data.get("birth_date")
            else ""
        )
        end_breeding_filld.value = str(
            breeding_data.get("separation_date", "")
            if breeding_data.get("separation_date")
            else ""
        )

        # รีเซ็ตสีของฟิลด์ทั้งหมด
        for field in fields:
            field.border_color = None
            field.helper_text = ""
            field.helper_style = None

        # ปรับสถานะฟิลด์ตามสถานะการผสม
        if status_dropdown.value == "unsuccess":
            normal_born_filld.read_only = True
            abnormal_born_filld.read_only = True
            dead_born_filld.read_only = True
            born_date_filld.read_only = True
            end_breeding_filld.read_only = True
            normal_born_filld.bgcolor = ft.Colors.GREY_200
            abnormal_born_filld.bgcolor = ft.Colors.GREY_200
            dead_born_filld.bgcolor = ft.Colors.GREY_200
            born_date_filld.bgcolor = ft.Colors.GREY_200
            end_breeding_filld.bgcolor = ft.Colors.GREY_200
        else:
            normal_born_filld.read_only = False
            abnormal_born_filld.read_only = False
            dead_born_filld.read_only = False
            born_date_filld.read_only = False
            end_breeding_filld.read_only = False
            normal_born_filld.bgcolor = White
            abnormal_born_filld.bgcolor = White
            dead_born_filld.bgcolor = White
            born_date_filld.bgcolor = White
            end_breeding_filld.bgcolor = White

        def save_edit_breeding_data(e):
            """บันทึกการแก้ไขข้อมูลการผสมพันธุ์"""
            if validate_input():
                print(validate_input())
                error_text_all.value = "กรุณากรอกข้อมูลให้ถูกต้อง"
                error_text_all.visible = True
                error_text_all.update()
            else:
                error_text_all.value = ""
                error_text_all.visible = False

                # เตรียมข้อมูลสำหรับอัพเดท
                try:
                    # ข้อมูลพื้นฐานการผสม
                    update_breeding_data = {
                        "breeding_id": breeding_id,
                        "father_id": get_rat_id_by_ring_number(
                            father_ring_number_filld.value
                        ),
                        "mother_id": get_rat_id_by_ring_number(
                            mother_ring_number_filld.value
                        ),
                        "pond_id": int(pond_number_filld.value),
                        "inbreeding_rate": float(inbreeding_coff_filld.value),
                        "breeding_status": status_dropdown.value,
                        "breeding_date": breed_date_filld.value,
                    }

                    # ข้อมูลการคลอด (ถ้ามี)
                    if any(
                        [
                            normal_born_filld.value,
                            abnormal_born_filld.value,
                            dead_born_filld.value,
                        ]
                    ):
                        update_breeding_data.update(
                            {
                                "survived_pups": (
                                    int(normal_born_filld.value)
                                    if normal_born_filld.value
                                    else 0
                                ),
                                "albino_pups": (
                                    int(abnormal_born_filld.value)
                                    if abnormal_born_filld.value
                                    else 0
                                ),
                                "dead_pups": (
                                    int(dead_born_filld.value)
                                    if dead_born_filld.value
                                    else 0
                                ),
                                "birth_date": (
                                    born_date_filld.value
                                    if born_date_filld.value
                                    else None
                                ),
                                "separation_date": (
                                    end_breeding_filld.value
                                    if end_breeding_filld.value
                                    else None
                                ),
                                "total_pups": (
                                    int(normal_born_filld.value)
                                    if normal_born_filld.value
                                    else 0
                                )
                                + (
                                    int(abnormal_born_filld.value)
                                    if abnormal_born_filld.value
                                    else 0
                                )
                                + (
                                    int(dead_born_filld.value)
                                    if dead_born_filld.value
                                    else 0
                                ),
                            }
                        )

                    # เรียกฟังก์ชันอัพเดทข้อมูล (ต้องสร้างฟังก์ชันนี้)
                    if update_breed_data(update_breeding_data):
                        print("อัพเดทข้อมูลการผสมพันธุ์สำเร็จ")
                        if status_dropdown.value == 'success':
                            auto_result = auto_manage_breeding_after_success(
                                update_breeding_data["father_id"],
                                update_breeding_data["mother_id"],
                                update_breeding_data["pond_id"]
                            )
                        
                        error_text_all.color = ft.Colors.GREEN_500
                        error_text_all.value = "บันทึกการแก้ไขสำเร็จ"
                        error_text_all.visible = True


                        def go_back():
                            cancel_edit_breeding(None)

                        # Delay 1.5 วินาทีแล้วกลับหน้าหลัก
                        threading.Timer(0.5, go_back).start()

                    else:
                        error_text_all.value = (
                            "ไม่สามารถบันทึกการแก้ไขได้ กรุณาตรวจสอบข้อมูลอีกครั้ง"
                        )
                        error_text_all.visible = True

                except Exception as ex:
                    print(f"Error updating breeding data: {ex}")
                    error_text_all.value = f"เกิดข้อผิดพลาด: {str(ex)}"
                    error_text_all.visible = True

                error_text_all.update()

        def cancel_edit_breeding(e):
            """ยกเลิกการแก้ไขและกลับไปหน้าหลัก"""
            global is_editing, edit_breeding_id
            is_editing = False
            edit_breeding_id = None

            # รีเซ็ตฟิลด์ทั้งหมด
            for field in fields:
                field.value = ""
                field.border_color = None
                field.helper_text = ""
                field.helper_style = None
                if hasattr(field, "read_only"):
                    field.read_only = False
                if hasattr(field, "bgcolor"):
                    field.bgcolor = White

            # รีเซ็ต error messages
            error_text_all.value = ""
            error_text_all.visible = False
            error_text_path1.value = ""
            error_text_path1.visible = False

            # กลับไปหน้าหลัก
            list_view.controls = [build_main_content()]
            list_view.update()

        # สร้าง UI สำหรับแก้ไขการผสมพันธุ์ (สไตล์เหมือนการเพิ่ม)
        breeding_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "แก้ไขการผสมพันธุ์",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    error_text_all,
                    ft.Divider(),
                    ft.Text("ข้อมูลการผสมพันธุ์", size=14, weight=ft.FontWeight.BOLD),
                    error_text_path1,
                    ft.Row(
                        [
                            father_ring_number_filld,
                            mother_ring_number_filld,
                        ]
                    ),
                    ft.Row(
                        [
                            pond_number_filld,
                            inbreeding_coff_filld,
                        ]
                    ),
                    ft.Row(
                        [
                            status_dropdown,
                        ]
                    ),
                    ft.Row(
                        [
                            breed_date_filld,
                        ]
                    ),
                    ft.Divider(),
                    ft.Text("ลูกที่คลอด", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            normal_born_filld,
                            abnormal_born_filld,
                            dead_born_filld,
                        ]
                    ),
                    born_date_filld,
                    end_breeding_filld,
                    ft.Container(
                        content=base_button_gradient(
                            button_name="บันทึกการแก้ไข",
                            on_click=save_edit_breeding_data,
                        ),
                        expand=True,
                    ),
                    ft.Container(
                        content=base_button_normal(
                            button_name="ยกเลิก",
                            on_click=cancel_edit_breeding,
                            background_color=White,
                            text_color=Black,
                        ),
                        expand=True,
                    ),
                ]
            ),
        )

        return ft.Card(
            content=ft.Container(
                padding=20,
                content=breeding_content,
            ),
            expand=True,
            color=White,
            margin=ft.margin.only(top=-10),
        )

    def build_main_content():
        main_content = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Container(
                                    content=base_button_normal(
                                        button_name="เพิ่มการผสมพันธุ์",
                                        icon="ADD_CIRCLE_OUTLINE",
                                        text_color=White,
                                        icon_color=White,
                                        background_color=Neo_Mint,
                                        on_click=lambda e: build_breeding_content(e),
                                    ),
                                    expand=True,
                                ),
                                ft.Container(
                                    content=base_button_normal(
                                        button_name="แนะนำคู่ผสมพันธุ์",
                                        icon="FAVORITE_OUTLINE_ROUNDED",
                                        text_color=White,
                                        icon_color=White,
                                        background_color=Deep_Purple,
                                        on_click=lambda e: recommend_breeding(e),
                                    ),
                                    expand=True,
                                ),
                            ],
                            expand=True,
                            spacing=0,
                        ),
                        expand=True,
                    ),
                    create_breeding_card(),
                ],
                expand=True,
            ),
            expand=True,
        )

        return main_content
              
    # สร้าง ListView หลัก
    list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.padding.only(top=20, bottom=20, left=5, right=5),
        controls=[build_main_content()],
    )

    return list_view
