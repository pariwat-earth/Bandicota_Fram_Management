from datetime import date, datetime
import flet as ft

from components.base_box import base_empty_box
from components.base_button import (
    base_button_gradient,
    base_button_gradient_v2,
    base_button_normal,
)

from pages.pedigree_tree import (
    check_mating_compatibility_toggle,
    display_rat_pedigree_toggle,
)
from storages.database_service import (
    get_all_farm,
    add_rat_information,
    get_all_rat_data,
    get_rat_by_rat_id,
    get_rat_id_by_ring_number,
    update_rat_by_rat_id,
    delete_rat_by_rat_id,
)
from storages.general_information import (
    check_pond_exists,
    check_ring_used,
    generate_rat_id,
    get_max_ring,
    get_pond_id_by_farm_id,
)
from styles.colors import Grey, Red, White, Black, Deep_Purple


def rat_page(target="view"):
    global is_editing
    is_editing = False
    global editing_rat_id
    editing_rat_id = None

    error_text = ft.Text(
        "",
        color=ft.Colors.RED_500,
        size=12,
        visible=False,
    )

    text_style = ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=Grey)

    # สร้างช่องกรอกสำหรับ rat_id
    rat_id_field = ft.TextField(
        label="รหัสหนู",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        read_only=True,
        bgcolor=ft.Colors.GREY_200,
    )

    # ช่องกรอกข้อมูลเพศ
    rat_gender_dropdown = ft.Dropdown(
        label="เพศ",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        options=[
            ft.dropdown.Option("male", "ผู้"),
            ft.dropdown.Option("female", "เมีย"),
        ],
    )

    # ช่องกรอกวันเกิด
    rat_birth_date_field = ft.TextField(
        label="วันเกิด (ปี-เดือน-วัน)",
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

    # ช่องกรอกน้ำหนัก
    weight_field = ft.TextField(
        label="น้ำหนัก (กรัม)",
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

    # ช่องกรอกขนาด
    size_field = ft.TextField(
        label="ขนาด (เซนติเมตร)",
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

    # ช่องกรอกสายพันธุ์
    breed_name_field = ft.TextField(
        label="สายพันธุ์",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    # ช่องกรอกสถานะ
    status_dropdown = ft.Dropdown(
        label="สถานะ",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        options=[
            ft.dropdown.Option("breeder1", "กำลังผสม"),
            ft.dropdown.Option("breeder2", "พร้อมผสม"),
            ft.dropdown.Option("fertilize", "ขุน"),
            ft.dropdown.Option("dispose", "จำหน่าย"),
        ],
    )

    # ช่องกรอกพ่อพันธุ์
    father_id_field = ft.TextField(
        label="รหัสพ่อพันธุ์",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    # ช่องกรอกแม่พันธุ์
    mother_id_field = ft.TextField(
        label="รหัสแม่พันธุ์",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=1,
        max_lines=1,
        multiline=False,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

    # สร้าง options สำหรับฟาร์มก่อน
    farms = get_all_farm()
    farm_options = []
    for farm in farms:
        farm_options.append(ft.dropdown.Option(str(farm["farm_id"]), farm["farm_name"]))

    # ช่องเลือกฟาร์ม
    farm_dropdown = ft.Dropdown(
        label="ฟาร์ม",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        options=farm_options,
    )

    farm_ponds_field = ft.TextField(
        label="รหัสบ่อ",  # เปลี่ยนจาก "จำนวนบ่อเลี้ยง" เป็น "รหัสบ่อ" เพื่อความชัดเจน
        hint_text="กรอกรหัสบ่อที่มีอยู่ในฟาร์มที่เลือก",
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

    # ช่องกรอกมีห่วงขาหรือไม่
    has_ring_dropdown = ft.Dropdown(
        label="มีห่วงขาหรือไม่",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        options=[
            ft.dropdown.Option("1", "มี"),
            ft.dropdown.Option("0", "ไม่มี"),
        ],
        value="0",
    )

    # ช่องกรอกหมายเลขห่วงขา
    ring_number_field = ft.TextField(
        label="หมายเลขห่วงขา",
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

    # ช่องกรอกลักษณะพิเศษ
    special_traits_field = ft.TextField(
        label="ลักษณะพิเศษ",
        border=ft.InputBorder.OUTLINE,
        expand=True,
        text_style=text_style,
        label_style=text_style,
        min_lines=3,
        max_lines=5,
        multiline=True,
        content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
    )

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

    # จัดกลุ่มฟอร์มให้เป็นหมวดหมู่
    basic_info_section = ft.Column(
        [
            ft.Text("ข้อมูลพื้นฐาน", size=14, weight=ft.FontWeight.BOLD),
            rat_id_field,
            rat_gender_dropdown,
            rat_birth_date_field,
            ft.Row([weight_field, size_field], spacing=10),
            breed_name_field,
            status_dropdown,
        ]
    )

    parent_info_section = ft.Column(
        [
            ft.Text("ข้อมูลพ่อแม่พันธุ์", size=14, weight=ft.FontWeight.BOLD),
            father_id_field,
            mother_id_field,
        ]
    )

    location_info_section = ft.Column(
        [
            ft.Text("ตำแหน่งที่อยู่", size=14, weight=ft.FontWeight.BOLD),
            farm_dropdown,
            farm_ponds_field,
        ]
    )

    # ส่วนแสดงข้อมูลห่วงขา - จะเพิ่ม ring_number_field ในภายหลัง
    ring_info_section = ft.Column(
        [
            ft.Text("ข้อมูลห่วงขา", size=14, weight=ft.FontWeight.BOLD),
            has_ring_dropdown,
            # ring_number_field จะถูกเพิ่มหรือลบออกตาม value ของ has_ring_dropdown
        ]
    )

    other_info_section = ft.Column(
        [
            ft.Text("ข้อมูลอื่นๆ", size=14, weight=ft.FontWeight.BOLD),
            special_traits_field,
        ]
    )

    # ฟังก์ชันแสดง/ซ่อนช่องหมายเลขห่วงขาตามการเลือกมีห่วงขาหรือไม่
    def on_has_ring_change(e):
        print(f"has_ring_dropdown value: {has_ring_dropdown.value}")

        # ลบ ring_number_field ออกจาก ring_info_section (ถ้ามี)
        for i, control in enumerate(ring_info_section.controls):
            if isinstance(control, ft.TextField) and control.label == "หมายเลขห่วงขา":
                ring_info_section.controls.pop(i)
                break

        if has_ring_dropdown.value == "1":  # เลือก "มีห่วงขา"
            # รีเซ็ตค่า ring_number_field
            ring_number_field.value = ""
            ring_number_field.border_color = None
            ring_number_field.helper_text = ""
            ring_number_field.helper_style = None
            ring_number_field.visible = True

            # ถ้าผู้ใช้เลือกฟาร์มแล้ว ให้กำหนดหมายเลขห่วงขาอัตโนมัติ
            if farm_dropdown.value:
                farm_id = int(farm_dropdown.value)
                next_ring = get_max_ring()

                if next_ring is not None:
                    # กำหนดค่าเริ่มต้นเป็นเลขห่วงขาที่ว่างและมีค่าน้อยที่สุด
                    ring_number_field.value = str(next_ring)
                else:
                    # ถ้าห่วงขาเต็มแล้ว
                    error_text.value = "ห่วงขาในฟาร์มนี้เต็มแล้ว"
                    error_text.visible = True

            # เพิ่ม ring_number_field เข้าไปใน ring_info_section
            ring_info_section.controls.append(ring_number_field)

        # อัปเดตการแสดงผล
        list_view.update()
        print(
            f"Updated ring_info_section with {len(ring_info_section.controls)} controls"
        )

    # เชื่อมต่อ event handler
    has_ring_dropdown.on_change = on_has_ring_change

    def on_farm_change(e):
        if farm_dropdown.value:
            # ถ้าผู้ใช้เลือกที่จะใส่ห่วงขา (has_ring = 1)
            if has_ring_dropdown.value == "1":
                farm_id = int(farm_dropdown.value)
                next_ring = get_max_ring(farm_id)

                if next_ring is not None:
                    # กำหนดค่าเริ่มต้นเป็นเลขห่วงขาที่ว่างและมีค่าน้อยที่สุด
                    ring_number_field.value = str(next_ring)
                else:
                    # ถ้าห่วงขาเต็มแล้ว
                    error_text.value = "ห่วงขาในฟาร์มนี้เต็มแล้ว"
                    error_text.visible = True

        # อัปเดตการแสดงผล
        list_view.update()

    # เชื่อมต่อฟังก์ชัน on_farm_change กับ event on_change ของ farm_dropdown
    farm_dropdown.on_change = on_farm_change

    # ฟังก์ชันตรวจสอบความถูกต้องของฟอร์ม
    def validate_form():
        is_valid = True

        # กำหนดรายการฟิลด์ที่ต้องตรวจสอบ
        fields_to_validate = {
            rat_gender_dropdown: "",
            rat_birth_date_field: "",
            breed_name_field: "",
            status_dropdown: "",
            farm_dropdown: "",
            has_ring_dropdown: "",
        }

        # ตรวจสอบฟิลด์ที่จำเป็น
        for field, error_message in fields_to_validate.items():
            if not field.value:
                field.border_color = ft.Colors.RED_500
                field.helper_text = error_message
                field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                is_valid = False
            else:
                field.border_color = None
                field.helper_text = ""
                field.helper_style = None

        # ตรวจสอบรูปแบบวันที่
        if rat_birth_date_field.value and not validate_date(rat_birth_date_field.value):
            rat_birth_date_field.border_color = ft.Colors.RED_500
            rat_birth_date_field.helper_text = "รูปแบบวันที่ไม่ถูกต้อง (ปี-เดือน-วัน)"
            rat_birth_date_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
            is_valid = False

        # ตรวจสอบค่าน้ำหนัก (ถ้ามีการกรอก)
        if weight_field.value:
            try:
                weight = float(weight_field.value)
                if weight <= 0:
                    weight_field.border_color = ft.Colors.RED_500
                    weight_field.helper_text = "น้ำหนักต้องมากกว่า 0"
                    weight_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                    is_valid = False
                else:
                    weight_field.border_color = None
                    weight_field.helper_text = ""
                    weight_field.helper_style = None
            except ValueError:
                weight_field.border_color = ft.Colors.RED_500
                weight_field.helper_text = "น้ำหนักต้องเป็นตัวเลข"
                weight_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                is_valid = False

        # ตรวจสอบค่าขนาด (ถ้ามีการกรอก)
        if size_field.value:
            try:
                size = float(size_field.value)
                if size <= 0:
                    size_field.border_color = ft.Colors.RED_500
                    size_field.helper_text = "ขนาดต้องมากกว่า 0"
                    size_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                    is_valid = False
                else:
                    size_field.border_color = None
                    size_field.helper_text = ""
                    size_field.helper_style = None
            except ValueError:
                size_field.border_color = ft.Colors.RED_500
                size_field.helper_text = "ขนาดต้องเป็นตัวเลข"
                size_field.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                is_valid = False

        # ตรวจสอบกรณีมีห่วงขา
        if has_ring_dropdown.value == "1":
            # ตรวจสอบว่ามี ring_number_field อยู่ใน UI หรือไม่
            has_ring_field = False
            for control in ring_info_section.controls:
                if (
                    isinstance(control, ft.TextField)
                    and control.label == "หมายเลขห่วงขา"
                ):
                    has_ring_field = True
                    if not control.value:
                        control.border_color = ft.Colors.RED_500
                        control.helper_text = "กรุณากรอกหมายเลขห่วงขา"
                        control.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                        is_valid = False
                    else:
                        try:
                            ring_number = int(control.value)
                            if ring_number <= 0:
                                control.border_color = ft.Colors.RED_500
                                control.helper_text = "หมายเลขห่วงขาต้องมากกว่า 0"
                                control.helper_style = ft.TextStyle(
                                    color=ft.Colors.RED_500
                                )
                                is_valid = False
                            else:
                                # ตรวจสอบว่าหมายเลขห่วงขาถูกใช้ไปแล้วหรือไม่
                                if farm_dropdown.value:
                                    farm_id = int(farm_dropdown.value)
                                    if check_ring_used(farm_id, ring_number):
                                        control.border_color = ft.Colors.RED_500
                                        control.helper_text = "หมายเลขห่วงขานี้ถูกใช้ไปแล้ว"
                                        control.helper_style = ft.TextStyle(
                                            color=ft.Colors.RED_500
                                        )
                                        is_valid = False
                                    else:
                                        control.border_color = None
                                        control.helper_text = ""
                                        control.helper_style = None
                                else:
                                    control.border_color = None
                                    control.helper_text = ""
                                    control.helper_style = None
                        except ValueError:
                            control.border_color = ft.Colors.RED_500
                            control.helper_text = "หมายเลขห่วงขาต้องเป็นตัวเลข"
                            control.helper_style = ft.TextStyle(color=ft.Colors.RED_500)
                            is_valid = False
                    break

            if not has_ring_field:
                # ถ้าไม่มีฟิลด์ให้กรอกหมายเลขห่วงขา ให้เพิ่มเข้าไป
                ring_number_field.value = ""
                ring_info_section.controls.append(ring_number_field)
                error_text.value = "กรุณากรอกหมายเลขห่วงขา"
                error_text.visible = True
                is_valid = False

        # ตรวจสอบความถูกต้องโดยรวม
        if not is_valid:
            error_text.value = "กรุณากรอกข้อมูลให้ครบถ้วนและถูกต้อง"
            error_text.visible = True
        else:
            error_text.visible = False

        list_view.update()
        return is_valid

    # ฟังก์ชันล้างสถานะข้อผิดพลาดเมื่อมีการเปลี่ยนแปลงค่า
    def clear_error_on_change(e):
        control = e.control
        control.border_color = None
        control.helper_text = ""
        control.helper_style = None
        if error_text.visible:
            error_text.visible = False
            error_text.update()

    # เชื่อม event handler สำหรับการเปลี่ยนแปลงค่าทุกฟิลด์
    fields = [
        rat_id_field,
        rat_gender_dropdown,
        rat_birth_date_field,
        weight_field,
        size_field,
        breed_name_field,
        status_dropdown,
        father_id_field,
        mother_id_field,
        farm_dropdown,
        farm_ponds_field,
        ring_number_field,
        special_traits_field,
    ]

    for field in fields:
        field.on_change = clear_error_on_change

    # สร้าง form ให้ครบทุก field แบ่งเป็นส่วนๆ
    add_rat_form = ft.Column(
        [
            ft.Text("เพิ่มหนูใหม่", size=18, weight=ft.FontWeight.BOLD),
            error_text,
            ft.Divider(),
            basic_info_section,
            ft.Divider(),
            parent_info_section,
            ft.Divider(),
            location_info_section,
            ft.Divider(),
            ring_info_section,
            ft.Divider(),
            other_info_section,
            ft.Divider(),
            base_empty_box(2),
            ft.Column(
                [
                    base_button_gradient(
                        button_name="บันทึก", on_click=lambda e: save_rat_data(e)
                    ),
                    base_button_normal(
                        button_name="ยกเลิก",
                        on_click=lambda e: cancel_add_rat(e),
                        background_color=White,
                        text_color=Black,
                    ),
                ]
            ),
        ],
        spacing=15,
    )

    add_rat_container = ft.Card(
        content=ft.Container(
            padding=20,
            content=add_rat_form,
        ),
        expand=True,
        color=White,
        margin=ft.margin.only(top=-10),
    )

    def save_rat_data(e):
        global is_editing
        global editing_rat_id

        if is_editing and editing_rat_id:
            # กำลังแก้ไขข้อมูล - เรียกใช้ update_rat_data
            update_rat_data(e, editing_rat_id)
        else:
            if validate_form():
                try:
                    # กำหนดค่า farm_id
                    farm_id = int(farm_dropdown.value)

                    # กำหนดค่า pond_id (ถ้ามี)
                    pond_id = None
                    if farm_ponds_field.value:
                        # ตรวจสอบว่า pond_id ที่กรอกมีอยู่จริงหรือไม่
                        pond_id = int(farm_ponds_field.value)

                        # ตรวจสอบว่า pond_id ที่กรอกมีอยู่จริงหรือไม่
                        pond_id = get_pond_id_by_farm_id(pond_id, farm_id)
                        print(pond_id)
                        if not check_pond_exists(pond_id, farm_id):
                            farm_ponds_field.border_color = ft.Colors.RED_500
                            farm_ponds_field.helper_text = (
                                f"ไม่พบบ่อรหัส {pond_id} ในฟาร์มที่เลือก"
                            )
                            farm_ponds_field.helper_style = ft.TextStyle(
                                color=ft.Colors.RED_500
                            )
                            error_text.value = f"ไม่พบบ่อรหัส {pond_id} ในฟาร์มที่เลือก"
                            error_text.visible = True
                            list_view.update()
                            return

                    # กำหนดค่า ring_number (ถ้ามี)
                    ring_number = None
                    if has_ring_dropdown.value == "1":
                        # ค้นหา ring_number_field ใน UI
                        for control in ring_info_section.controls:
                            if (
                                isinstance(control, ft.TextField)
                                and control.label == "หมายเลขห่วงขา"
                            ):
                                if control.value:
                                    ring_number = int(control.value)
                                    # ตรวจสอบว่าหมายเลขห่วงขาถูกใช้ไปแล้วหรือไม่
                                    if check_ring_used(farm_id, ring_number):
                                        control.border_color = ft.Colors.RED_500
                                        control.helper_text = "หมายเลขห่วงขานี้ถูกใช้ไปแล้ว"
                                        control.helper_style = ft.TextStyle(
                                            color=ft.Colors.RED_500
                                        )
                                        error_text.value = "หมายเลขห่วงขานี้ถูกใช้ไปแล้ว"
                                        error_text.visible = True
                                        list_view.update()
                                        return
                                break

                    # เตรียมข้อมูลสำหรับบันทึก
                    rat_data = (
                        rat_id_field.value,  # rat_id
                        (
                            get_rat_id_by_ring_number(father_id_field.value)
                            if father_id_field.value
                            else None
                        ),  # father_id
                        (
                            get_rat_id_by_ring_number(mother_id_field.value)
                            if mother_id_field.value
                            else None
                        ),  # mother_id
                        rat_birth_date_field.value,  # birth_date
                        rat_gender_dropdown.value,  # gender
                        (
                            float(weight_field.value) if weight_field.value else None
                        ),  # weight
                        float(size_field.value) if size_field.value else None,  # size
                        breed_name_field.value,  # breed
                        status_dropdown.value,  # status
                        pond_id,  # pond_id
                        farm_id,  # farm_id
                        int(has_ring_dropdown.value),  # has_ring
                        ring_number,  # ring_number
                        (
                            special_traits_field.value
                            if special_traits_field.value
                            else None
                        ),  # special_traits
                    )

                    # บันทึกข้อมูล
                    result = add_rat_information(rat_data)

                    if result:
                        # บันทึกสำเร็จ กลับไปหน้าหลัก
                        reset_main_view()
                    else:
                        # บันทึกไม่สำเร็จ
                        error_text.value = "ไม่สามารถบันทึกข้อมูลได้ กรุณาตรวจสอบข้อมูลอีกครั้ง"
                        error_text.visible = True
                        list_view.update()

                except ValueError as ve:
                    # กรณีกรอกค่าไม่ใช่ตัวเลข
                    error_text.value = f"ข้อมูลไม่ถูกต้อง: {str(ve)}"
                    error_text.visible = True
                    list_view.update()
                except Exception as e:
                    # แสดงข้อผิดพลาดที่เกิดขึ้น
                    error_text.value = f"เกิดข้อผิดพลาด: {str(e)}"
                    error_text.visible = True
                    list_view.update()
                    print(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")

    def cancel_add_rat(e):
        global is_editing
        is_editing = False
        global editing_rat_id
        editing_rat_id = None
        reset_main_view()

    # แก้ไขฟังก์ชัน add_new
    def add_new(e):
        # เคลียร์ค่าใน fields
        for field in fields:
            if isinstance(field, ft.Dropdown):
                field.value = None
            else:
                field.value = ""
            field.border_color = None
            field.helper_text = ""
            field.helper_style = None

        # กำหนดค่า rat_id อัตโนมัติ
        rat_id_field.value = generate_rat_id()

        # ซ่อนช่องกรอกหมายเลขห่วงขาเริ่มต้น
        ring_number_field.visible = False

        # รีเซ็ตข้อความแจ้งเตือน
        error_text.value = ""
        error_text.visible = False

        # เปลี่ยนชื่อฟอร์มให้เหมาะสมกับการเพิ่มใหม่
        form_title = ft.Text("เพิ่มหนูใหม่", size=18, weight=ft.FontWeight.BOLD)
        if add_rat_form.controls and isinstance(add_rat_form.controls[0], ft.Text):
            add_rat_form.controls[0] = form_title

        # กำหนดสถานะว่ากำลังเพิ่มใหม่
        global is_editing
        is_editing = False
        global editing_rat_id
        editing_rat_id = None

        # แสดงฟอร์ม
        list_view.controls = [add_rat_container]
        list_view.update()

    def get_all_rat():
        # เรียกข้อมูลหนูทั้งหมดจากฐานข้อมูล
        rats = get_all_rat_data()  # ต้องมีฟังก์ชันนี้ใน database_service.py

        # ตัวแปรสถานะการแสดง filter
        is_filter_expanded = False

        def delete_rat(id):
            # ลบข้อมูลหนู และรีเฟรชหน้าจอ
            delete_rat_by_rat_id(id)

            rats = get_all_rat_data()
            filtered_rats = rats

            # อัปเดต UI
            rat_cards_column.controls = create_rat_cards()
            rat_cards_column.update()

        def toggle_filter(e):
            nonlocal is_filter_expanded
            is_filter_expanded = not is_filter_expanded
            filter_ui.visible = is_filter_expanded
            filter_toggle_button.icon = (
                ft.Icons.KEYBOARD_ARROW_UP
                if is_filter_expanded
                else ft.Icons.KEYBOARD_ARROW_DOWN
            )
            filter_header.update()
            filter_ui.update()

        filter_toggle_button = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_DOWN,
            icon_color=Grey,
            icon_size=20,
            on_click=toggle_filter,
            tooltip="เปิด/ปิดตัวกรอง",
        )

        # ฟังก์ชันภายในสำหรับการอัปเดตการกรอง
        def apply_filter(e=None, gender=None, status=None, farm=None):
            nonlocal filtered_rats, current_gender, current_status, current_farm

            # บันทึกค่าการกรองปัจจุบัน
            # สำหรับ gender ให้กำหนดเป็น None โดยตรงเมื่อเลือก "ทั้งหมด"
            current_gender = gender  # รับค่าตาม parameter (None, "male", หรือ "female")

            # สำหรับ status ให้ตรวจสอบว่าเป็น "all" หรือไม่
            if status == "all":
                current_status = None
            elif status is not None:  # ถ้าค่าไม่ใช่ None และไม่ใช่ "all"
                current_status = status

            # สำหรับ farm ให้ตรวจสอบว่าเป็น "all" หรือไม่
            if farm == "all":
                current_farm = None
            elif farm is not None:  # ถ้าค่าไม่ใช่ None และไม่ใช่ "all"
                current_farm = farm

            # กรองข้อมูลตามเงื่อนไข (เริ่มจากข้อมูลทั้งหมด)
            filtered_rats = rats

            # กรองตามเพศ
            if current_gender is not None:
                filtered_rats = [
                    r for r in filtered_rats if r.get("gender") == current_gender
                ]

            # กรองตามสถานะ
            if current_status is not None:
                filtered_rats = [
                    r for r in filtered_rats if r.get("status") == current_status
                ]

            # กรองตามฟาร์ม
            if current_farm is not None:
                filtered_rats = [
                    r for r in filtered_rats if str(r.get("farm_id")) == current_farm
                ]

            # อัปเดตข้อความแสดงจำนวนที่พบ
            result_count_text.value = f"พบ {len(filtered_rats)} รายการ"

            # อัปเดตสีปุ่มเพศ
            male_button.bgcolor = Deep_Purple if current_gender == "male" else White
            male_button.color = White if current_gender == "male" else Black
            female_button.bgcolor = Deep_Purple if current_gender == "female" else White
            female_button.color = White if current_gender == "female" else Black
            all_gender_button.bgcolor = Deep_Purple if current_gender is None else White
            all_gender_button.color = White if current_gender is None else Black

            # อัปเดตค่า dropdown
            status_dropdown.value = (
                current_status if current_status is not None else "all"
            )

            # รีเฟรชการแสดงผล
            filter_ui.update()
            rat_cards_column.controls = (
                create_rat_cards() if filtered_rats else [create_empty_result()]
            )
            rat_cards_column.update()

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
                            "ไม่พบข้อมูลหนูตามเงื่อนไขที่กำหนด",
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


        def get_ancestor_display(rat_id):
            """
            ฟังก์ชันสำหรับแสดงบรรพบุรุษ
            ถ้ามี has_ring แสดง ring_number
            ถ้าไม่มี แสดง rat_id
            """
            if rat_id is None:
                return 'ไม่ทราบ'
            
            # เรียกใช้ฟังก์ชันที่มีอยู่แล้ว
            rat_data = get_rat_by_rat_id(rat_id)
            
            if rat_data is None:
                return rat_id  # ถ้าไม่พบข้อมูล แสดง rat_id เดิม
            
            # ตรวจสอบ has_ring
            if rat_data.get('has_ring') == 1 and rat_data.get('ring_number') is not None:
                return f"ห่วงขา-{str(rat_data['ring_number'])}"
            else:
                return f"รหัส-{rat_id}"

        def create_rat_cards():
            cards = []
            for rat in filtered_rats:
                # กำหนดสีตามเพศ
                gender_color = (
                    ft.Colors.BLUE_500 if rat["gender"] == "male" else ft.Colors.RED_500
                )
                gender_text = "ตัวผู้" if rat["gender"] == "male" else "ตัวเมีย"

                # กำหนดสถานะการผสมพันธุ์
                breeding_status = "กำลังผสมพันธุ์"
                breeding_color = ft.Colors.RED_500

                if rat["status"] == "breeder2":
                    breeding_status = "พร้อมผสมพันธุ์"
                    breeding_color = ft.Colors.GREEN_500
                elif rat["status"] == "fertilize":
                    breeding_status = "ขุน"
                    breeding_color = ft.Colors.ORANGE_500

                # คำนวณอายุเป็นเดือน
                age_text = "ไม่ทราบ"
                try:
                    if "birth_date" in rat and rat["birth_date"]:
                        # ตรวจสอบรูปแบบวันที่ YYYY-MM-DD
                        birth_date_str = str(rat["birth_date"]).strip()

                        # แยกส่วนของวันที่
                        date_parts = birth_date_str.split("-")
                        if len(date_parts) == 3:
                            year = int(date_parts[0])
                            month = int(date_parts[1])
                            day = int(date_parts[2])

                            # สร้าง datetime object
                            birth_date = datetime(year, month, day)
                            today = datetime.now()

                            # คำนวณความแตกต่างของวันที่
                            delta = today - birth_date
                            age_in_days = delta.days

                            # คำนวณเป็นเดือน
                            age_in_months = age_in_days // 30

                            # ถ้าน้อยกว่า 1 เดือน แสดงเป็นวัน
                            if age_in_months < 1:
                                age_text = f"{age_in_days} วัน"
                            else:
                                age_text = f"{age_in_months} เดือน"
                except Exception as e:
                    age_text = "ไม่ทราบ"

                # *** ส่วนที่แก้ไข: แสดงบรรพบุรุษ ***
                father_display = get_ancestor_display(rat.get('father_id'))
                mother_display = get_ancestor_display(rat.get('mother_id'))
                ancestor_text = f"บรรพบุรุษ: {father_display} X {mother_display}"

                # สร้าง card สำหรับหนูแต่ละตัว
                rat_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            # ส่วนหัว: หมายเลขห่วงขาและเพศ
                                            ft.Row(
                                                [
                                                    ft.Row(
                                                        [
                                                            ft.Text(
                                                                f"หมายเลขห่วงขา: {rat.get('ring_number') if rat.get('ring_number') is not None else '-'}",
                                                                size=13,
                                                                weight=ft.FontWeight.BOLD,
                                                                color=Black,
                                                            ),
                                                            ft.Container(
                                                                content=ft.Text(
                                                                    gender_text,
                                                                    color=gender_color,
                                                                    size=10,
                                                                ),
                                                                margin=ft.margin.only(
                                                                    bottom=-4
                                                                ),
                                                            ),
                                                        ]
                                                    ),
                                                    # ปุ่มลบ (ขวาสุด)
                                                    ft.Column(
                                                        [
                                                            ft.Container(
                                                                content=ft.IconButton(
                                                                    icon=ft.Icons.DELETE_OUTLINE,
                                                                    icon_color=Grey,
                                                                    icon_size=13,
                                                                    tooltip="ลบ",
                                                                    on_click=lambda e, id=rat[
                                                                        "rat_id"
                                                                    ]: delete_rat(
                                                                        id
                                                                    ),
                                                                ),
                                                                margin=ft.margin.only(
                                                                    top=-15, right=-10
                                                                ),
                                                            ),
                                                            ft.Container(
                                                                content=ft.Text(
                                                                    breeding_status,
                                                                    size=10,
                                                                    color=breeding_color,
                                                                ),
                                                                margin=ft.margin.only(
                                                                    top=-20, left=-10
                                                                ),
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            ),
                                            # ข้อมูลพันธุ์
                                            ft.Container(
                                                content=ft.Text(
                                                    f"พันธุ์: {rat.get('breed', '-')}",
                                                    size=12,
                                                    color=Grey,
                                                ),
                                                margin=ft.margin.only(
                                                    top=-17, bottom=5
                                                ),
                                            ),
                                            # ข้อมูลบรรพบุรุษ (ส่วนที่แก้ไข)
                                            ft.Container(
                                                content=ft.Text(
                                                    ancestor_text,
                                                    size=12,
                                                    color=Grey,
                                                ),
                                                margin=ft.margin.only(
                                                    top=-17, bottom=5
                                                ),
                                            ),
                                            # ข้อมูลอายุ น้ำหนัก และบ่อเลี้ยง
                                            ft.Row(
                                                [
                                                    # อายุ
                                                    ft.Container(
                                                        content=ft.Column(
                                                            [
                                                                ft.Text(
                                                                    "อายุ",
                                                                    size=12,
                                                                    color=Grey,
                                                                ),
                                                                ft.Text(
                                                                    age_text,
                                                                    size=12,
                                                                    weight=ft.FontWeight.BOLD,
                                                                    color=Black,
                                                                ),
                                                            ],
                                                            horizontal_alignment=ft.CrossAxisAlignment.START,
                                                            spacing=5,
                                                        ),
                                                        expand=True,
                                                        border_radius=5,
                                                        bgcolor=White,
                                                        shadow=ft.BoxShadow(
                                                            spread_radius=1,
                                                            blur_radius=1,
                                                            color=ft.Colors.GREY_300,
                                                            offset=ft.Offset(0, 1),
                                                        ),
                                                        padding=ft.padding.all(10),
                                                    ),
                                                    # น้ำหนัก
                                                    ft.Container(
                                                        content=ft.Column(
                                                            [
                                                                ft.Text(
                                                                    "น้ำหนัก",
                                                                    size=12,
                                                                    color=Grey,
                                                                ),
                                                                ft.Text(
                                                                    f"{rat.get('weight', '0')} กรัม",
                                                                    size=12,
                                                                    weight=ft.FontWeight.BOLD,
                                                                    color=Black,
                                                                ),
                                                            ],
                                                            horizontal_alignment=ft.CrossAxisAlignment.START,
                                                            spacing=5,
                                                        ),
                                                        expand=True,
                                                        border_radius=5,
                                                        bgcolor=White,
                                                        shadow=ft.BoxShadow(
                                                            spread_radius=1,
                                                            blur_radius=1,
                                                            color=ft.Colors.GREY_300,
                                                            offset=ft.Offset(0, 1),
                                                        ),
                                                        padding=ft.padding.all(10),
                                                    ),
                                                    # บ่อเลี้ยง
                                                    ft.Container(
                                                        content=ft.Column(
                                                            [
                                                                ft.Text(
                                                                    "บ่อเลี้ยง",
                                                                    size=12,
                                                                    color=Grey,
                                                                ),
                                                                ft.Text(
                                                                    (
                                                                        f"บ่อ {rat.get('pond_id') or '-'}"
                                                                        if rat.get(
                                                                            "pond_id"
                                                                        )
                                                                        else "บ่อ -"
                                                                    ),
                                                                    size=12,
                                                                    weight=ft.FontWeight.BOLD,
                                                                    color=Black,
                                                                ),
                                                            ],
                                                            horizontal_alignment=ft.CrossAxisAlignment.START,
                                                            spacing=5,
                                                        ),
                                                        expand=True,
                                                        border_radius=5,
                                                        bgcolor=White,
                                                        shadow=ft.BoxShadow(
                                                            spread_radius=1,
                                                            blur_radius=1,
                                                            color=ft.Colors.GREY_300,
                                                            offset=ft.Offset(0, 1),
                                                        ),
                                                        padding=ft.padding.all(10),
                                                    ),
                                                ],
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            ),
                                        ]
                                    ),
                                    margin=ft.margin.only(left=15, right=15, top=5),
                                ),
                                # ปุ่มดูรายละเอียด (gradient background)
                                ft.Container(
                                    content=base_button_gradient_v2(
                                        button_name="ดูรายละเอียด",
                                        on_click=lambda e, id=rat[
                                            "rat_id"
                                        ]: view_rat_details(id),
                                    )
                                ),
                            ]
                        ),
                        border_radius=10,
                        bgcolor=White,
                    ),
                    elevation=2,
                    margin=ft.margin.only(bottom=15, left=5, right=5),
                )

                cards.append(rat_card)

            return cards

        # ตัวแปรเก็บค่าการกรองปัจจุบัน
        current_gender = None
        current_status = None
        current_farm = None
        filtered_rats = rats  # เริ่มต้นแสดงทั้งหมด

        # สร้าง UI สำหรับตัวกรอง
        # ปุ่มกรองตามเพศ
        all_gender_button = ft.ElevatedButton(
            "ทั้งหมด",
            bgcolor=Deep_Purple,  # เริ่มต้นเป็นสีเข้ม (เลือกอยู่)
            color=White,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
            ),
            on_click=lambda e: apply_filter(gender=None),
        )

        male_button = ft.ElevatedButton(
            "ตัวผู้",
            bgcolor=White,
            color=Black,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
            ),
            on_click=lambda e: apply_filter(gender="male"),
        )

        female_button = ft.ElevatedButton(
            "ตัวเมีย",
            bgcolor=White,
            color=Black,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5),
            ),
            on_click=lambda e: apply_filter(gender="female"),
        )

        # Dropdown สำหรับกรองตามสถานะ
        status_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("all", "ทั้งหมด"),
                ft.dropdown.Option("breeder1", "กำลังผสม"),
                ft.dropdown.Option("breeder2", "พร้อมผสม"),
                ft.dropdown.Option("fertilize", "ขุน"),
            ],
            value="all",
            on_change=lambda e: apply_filter(status=e.control.value),
            content_padding=ft.padding.only(left=10, right=5),
            text_size=12,
        )

        # ข้อความแสดงจำนวนที่พบ
        result_count_text = ft.Text(
            f"พบ {len(filtered_rats)} รายการ",
            size=12,
            color=Grey,
            italic=True,
        )

        # สร้างส่วนหัวที่มีปุ่มขยาย/ย่อ
        filter_header = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "รายการหนูทั้งหมด",
                        color=Black,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                "ตัวกรอง",
                                color=Grey,
                                size=12,
                            ),
                            filter_toggle_button,
                        ],
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(left=5, right=5, top=10, bottom=5),
        )

        # สร้าง UI ส่วนตัวกรอง
        filter_ui = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            # ส่วนกรองตามเพศ
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("เพศ", size=12, color=Grey),
                                        ft.Row(
                                            [
                                                all_gender_button,
                                                male_button,
                                                female_button,
                                            ],
                                            spacing=5,
                                        ),
                                    ]
                                ),
                                margin=ft.margin.only(right=10),
                            ),
                            # ส่วนกรองตามสถานะ
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("สถานะ", size=12, color=Grey),
                                        status_dropdown,
                                    ]
                                ),
                                expand=True,
                            ),
                        ]
                    ),
                    result_count_text,
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

        # สร้าง Column สำหรับแสดง rat cards
        rat_cards_column = ft.Column(
            create_rat_cards() if filtered_rats else [create_empty_result()],
            spacing=0,
        )

        # สร้างองค์ประกอบหลักของหน้าจอ
        rat_element = [
            # หัวข้อพร้อมปุ่มขยาย/ย่อ
            filter_header,
            # ส่วนตัวกรอง (อาจถูกซ่อน)
            filter_ui,
            # ส่วนแสดงรายการหนู
            rat_cards_column,
        ]

        return rat_element

    # ฟังก์ชันดูรายละเอียดหนู (ควรเพิ่มในโค้ดหลัก)
    def view_rat_details(rat_id):
        global edit_mode
        edit_mode = True
        # ดึงข้อมูลหนูจาก database
        rat = get_rat_by_rat_id(rat_id)

        if rat:
            # เรียกใช้ฟังก์ชันแก้ไขข้อมูลหนู
            edit_rat(rat_id)

    # ฟังก์ชันแก้ไขข้อมูลหนู
    def edit_rat(rat_id):
        # ดึงข้อมูลหนูจาก ID
        rat = get_rat_by_rat_id(rat_id)

        if rat is None:
            # ถ้าไม่พบข้อมูลหนู
            print(f"ไม่พบข้อมูลหนู ID: {rat_id}")
            return

        # รีเซ็ตข้อความแจ้งเตือน
        error_text.visible = False

        # รีเซ็ต ring_info_section
        ring_info_section.controls = [
            ft.Text("ข้อมูลห่วงขา", size=14, weight=ft.FontWeight.BOLD),
            has_ring_dropdown,
        ]

        # ใส่ข้อมูลหนูลงในฟอร์ม
        rat_id_field.value = rat["rat_id"]
        rat_gender_dropdown.value = rat["gender"]
        rat_birth_date_field.value = rat["birth_date"]
        weight_field.value = str(rat["weight"]) if rat["weight"] is not None else ""
        size_field.value = str(rat["size"]) if rat["size"] is not None else ""
        breed_name_field.value = rat["breed"]
        status_dropdown.value = rat["status"]
        father_id_field.value = rat["father_id"] if rat["father_id"] else ""
        mother_id_field.value = rat["mother_id"] if rat["mother_id"] else ""
        farm_dropdown.value = str(rat["farm_id"])
        farm_ponds_field.value = str(rat["pond_id"]) if rat["pond_id"] else ""
        has_ring_dropdown.value = "1" if rat["has_ring"] == 1 else "0"
        special_traits_field.value = (
            rat["special_traits"] if rat["special_traits"] else ""
        )

        # จัดการส่วนการแสดงข้อมูลห่วงขา
        if rat["has_ring"] == 1:
            ring_number_field.value = str(rat["ring_number"])
            ring_info_section.controls.append(ring_number_field)
            ring_number_field.visible = True
        else:
            ring_number_field.visible = False

        # เปลี่ยนชื่อฟอร์มให้เหมาะสมกับการแก้ไข
        form_title = ft.Text("รายละเอียดหนู", size=15, weight=ft.FontWeight.BOLD)
        if add_rat_form.controls and isinstance(add_rat_form.controls[0], ft.Text):
            add_rat_form.controls[0] = form_title

        # ตัวแปรบอกสถานะว่ากำลังแก้ไขหรือเพิ่มใหม่
        global is_editing
        is_editing = True
        global editing_rat_id
        editing_rat_id = rat_id

        # สร้างส่วนแผนภาพพันธุ์ประวัติ
        pedigree_chart = ft.Container(
            content=ft.Column(
                [
                    ft.Text("แผนภาพพันธุ์ประวัติ", size=14, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    ft.Container(
                        content=display_rat_pedigree_toggle(rat_id_field.value, 5),
                        expand=True,
                    ),
                ]
            ),
            bgcolor=White,
            border_radius=10,
            padding=10,
            margin=ft.margin.only(bottom=10),
            shadow=ft.BoxShadow(
                spread_radius=0.1,
                blur_radius=1,
                color=ft.Colors.GREY_300,
                offset=ft.Offset(0, 0),
            ),
            expand=True,
        )

        # แสดงฟอร์มแก้ไข
        list_view.controls = [pedigree_chart, add_rat_container]
        list_view.update()

    # ฟังก์ชันสำหรับอัปเดตข้อมูลหนู
    def update_rat_data(e, rat_id):

        try:
            # ดึงข้อมูลหนูเดิม
            current_rat = get_rat_by_rat_id(rat_id)
            if not current_rat:
                error_text.value = f"ไม่พบข้อมูลหนูรหัส {rat_id}"
                error_text.visible = True
                error_text.update()
                return

            # กำหนดค่า farm_id
            farm_id = int(farm_dropdown.value)

            # กำหนดค่า pond_id (ถ้ามี)
            pond_id = None
            if farm_ponds_field.value:
                pond_id = int(farm_ponds_field.value)

                # ตรวจสอบว่า pond_id ที่กรอกมีอยู่จริงหรือไม่
                pond_id = get_pond_id_by_farm_id(pond_id, farm_id)
                print(pond_id)
                if not check_pond_exists(pond_id, farm_id):
                    farm_ponds_field.border_color = ft.Colors.RED_500
                    farm_ponds_field.helper_text = f"ไม่พบบ่อรหัส {pond_id} ในฟาร์มที่เลือก"
                    farm_ponds_field.helper_style = ft.TextStyle(
                        color=ft.Colors.RED_500
                    )
                    error_text.value = f"ไม่พบบ่อรหัส {pond_id} ในฟาร์มที่เลือก"
                    error_text.visible = True
                    error_text.update()
                    return

            # กำหนดค่า ring_number (ถ้ามี)
            ring_number = None
            if has_ring_dropdown.value == "1" and ring_number_field.value:
                ring_number = int(ring_number_field.value)

                # ตรวจสอบว่าหมายเลขห่วงขาถูกใช้ไปแล้วหรือไม่
                # แต่ยกเว้นกรณีที่เป็นหมายเลขห่วงขาเดิมของหนูตัวนี้
                current_ring = current_rat.get("ring_number")

                # ตรวจสอบเฉพาะกรณีที่หมายเลขห่วงขาเปลี่ยนไปจากเดิม
                if ring_number != current_ring and check_ring_used(
                    farm_id, ring_number
                ):
                    ring_number_field.border_color = ft.Colors.RED_500
                    ring_number_field.helper_text = "หมายเลขห่วงขานี้ถูกใช้ไปแล้ว"
                    ring_number_field.helper_style = ft.TextStyle(
                        color=ft.Colors.RED_500
                    )
                    error_text.value = "หมายเลขห่วงขานี้ถูกใช้ไปแล้ว"
                    error_text.visible = True
                    error_text.update()
                    return

            # เตรียมข้อมูลสำหรับอัปเดต
            rat_data = (
                rat_id,  # rat_id (ไม่เปลี่ยนแปลง)
                (
                    get_rat_id_by_ring_number(father_id_field.value)
                    if father_id_field.value
                    else None
                ),  # father_id
                (
                    get_rat_id_by_ring_number(mother_id_field.value)
                    if mother_id_field.value
                    else None
                ),  # mother_id
                rat_birth_date_field.value,  # birth_date
                rat_gender_dropdown.value,  # gender
                float(weight_field.value) if weight_field.value else None,  # weight
                float(size_field.value) if size_field.value else None,  # size
                breed_name_field.value,  # breed
                status_dropdown.value,  # status
                pond_id,  # pond_id
                farm_id,  # farm_id
                int(has_ring_dropdown.value),  # has_ring
                ring_number,  # ring_number
                (
                    special_traits_field.value if special_traits_field.value else None
                ),  # special_traits
            )

            # อัปเดตข้อมูล
            result = update_rat_by_rat_id(rat_id, rat_data)

            if result:
                # อัปเดตสำเร็จ กลับไปหน้าหลัก
                reset_main_view()

            else:
                # อัปเดตไม่สำเร็จ
                error_text.value = "ไม่สามารถอัปเดตข้อมูลได้ กรุณาตรวจสอบข้อมูลอีกครั้ง"
                error_text.visible = True
                error_text.update()
        except ValueError as ve:
            # กรณีกรอกค่าไม่ใช่ตัวเลข
            error_text.value = f"ข้อมูลไม่ถูกต้อง: {str(ve)}"
            error_text.visible = True
            error_text.update()
        except Exception as e:
            # แสดงข้อผิดพลาดที่เกิดขึ้น
            error_text.value = f"เกิดข้อผิดพลาด: {str(e)}"
            error_text.visible = True
            error_text.update()
            print(f"เกิดข้อผิดพลาดในการอัปเดตข้อมูล: {e}")

    def build_main_content():
        return ft.Column(
            [
                ft.Container(
                    content=base_button_gradient(
                        button_name="เพิ่มหนูใหม่",
                        icon="ADD_CIRCLE_OUTLINE",
                        on_click=add_new,
                    ),
                    margin=ft.margin.only(bottom=10, top=1, left=5, right=5),
                ),
                ft.Container(
                    content=ft.Column(get_all_rat()),
                    margin=ft.margin.only(bottom=10),
                ),
            ]
        )

    rat_id_field.value = generate_rat_id()
    # สร้าง ListView หลัก
    list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.padding.all(20),
        controls=[build_main_content()] if target == "view" else [add_rat_container],
    )

    def reset_main_view():
        list_view.controls = [build_main_content()]
        list_view.update()

    return list_view
