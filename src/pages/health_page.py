import flet as ft
from datetime import date, datetime
from components.base_button import base_button_gradient, base_button_normal
from components.base_box import base_empty_box
from storages.database_service import (
    add_sick_rat,
    delete_health_record,
    get_all_health_records,
    get_health_record_by_id,
    get_health_records_by_rat_id,
    get_rats_for_health_check,
    update_health_record,
)
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, Red, White


def health_page():
    """หน้าจัดการสุขภาพหนู"""

    # ตัวแปรสถานะ
    current_view = "main"  # main, add_health, edit_health, history
    current_filter = "all"  # all, sick, recovering, monitoring
    editing_health_id = None
    viewing_rat_id = None

    # ข้อความแสดงข้อผิดพลาด
    error_text = ft.Text(
        "",
        color=ft.Colors.RED_500,
        size=12,
        visible=False,
    )

    text_style = ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=Grey)

    def build_add_health():
        """ฟอร์มเพิ่ม/แก้ไขข้อมูลสุขภาพ - Responsive"""

        # ดึงรายชื่อหนูสำหรับ dropdown
        rats = get_rats_for_health_check()
        rat_options = [
            ft.dropdown.Option(
                rat["rat_id"], f"{rat['rat_id']} - ห่วงขา {rat['ring_number'] or 'ไม่มี'}"
            )
            for rat in rats
        ]

        # Fields - Responsive
        rat_dropdown = ft.Dropdown(
            label="เลือกหนู",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            text_style=text_style,
            label_style=text_style,
            options=rat_options,
            content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        )

        record_date_field = ft.TextField(
            label="วันที่ตรวจ",
            value=date.today().strftime("%Y-%m-%d"),
            border=ft.InputBorder.OUTLINE,
            expand=True,
            text_style=text_style,
            label_style=text_style,
            content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        )

        symptoms_field = ft.TextField(
            label="อาการ",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            text_style=text_style,
            label_style=text_style,
            multiline=True,
            # min_lines=3,
            max_lines=5,
            content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        )

        treatment_field = ft.TextField(
            label="การรักษา",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            text_style=text_style,
            label_style=text_style,
            multiline=True,
            # min_lines=3,
            max_lines=5,
            content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        )

        treated_by_field = ft.TextField(
            label="ผู้รักษา",
            value="สัตวแพทย์ประจำฟาร์ม",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            text_style=text_style,
            label_style=text_style,
            content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        )

        results_dropdown = ft.Dropdown(
            label="สถานะการรักษา",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            text_style=text_style,
            label_style=text_style,
            value="sick",
            options=[
                ft.dropdown.Option("sick", "ป่วย"),
                ft.dropdown.Option("recovering", "พักฟื้น"),
                ft.dropdown.Option("monitoring", "เฝ้าระวัง"),
                ft.dropdown.Option("healed", "หายแล้ว"),
                ft.dropdown.Option("dead", "เสียชีวิต"),
            ],
            content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        )

        # ถ้าเป็นการแก้ไข ให้โหลดข้อมูลเดิม
        if current_view == "edit_health" and editing_health_id:
            health_record = get_health_record_by_id(editing_health_id)
            if health_record:
                rat_dropdown.value = health_record["rat_id"]
                rat_dropdown.disabled = True  # ไม่ให้เปลี่ยนหนู
                record_date_field.value = health_record["record_date"]
                symptoms_field.value = health_record["symptoms"]
                treatment_field.value = health_record["treatment"]
                treated_by_field.value = health_record["treated_by"]
                results_dropdown.value = health_record["results"]

        def save_health_data(e):
            """บันทึกข้อมูลสุขภาพ""" 
            try:
                # ตรวจสอบข้อมูล
                if not rat_dropdown.value:
                    show_error("กรุณาเลือกหนู")
                    return
                if not symptoms_field.value:
                    show_error("กรุณากรอกอาการ")
                    return
                if not treatment_field.value:
                    show_error("กรุณากรอกการรักษา")
                    return
                
                field_value = record_date_field.value if record_date_field.value else date.today()

                if isinstance(field_value, str):
                    record_date = datetime.strptime(field_value, "%Y-%m-%d").date()
                else:
                    record_date = field_value

                update_date = record_date.strftime("%Y-%m-%d")

                if current_view == "add_health":

                    # เพิ่มข้อมูลใหม่
                    sick_data = [
                        update_date,
                        rat_dropdown.value,
                        symptoms_field.value,
                        treatment_field.value,
                        treated_by_field.value,
                        results_dropdown.value,  # เพิ่มสถานะการรักษา
                    ]

                    result = add_sick_rat(sick_data)

                    if result["success"]:
                        show_success(result["message"])
                        switch_to_main()
                    else:
                        show_error(result["message"])

                elif current_view == "edit_health":
                    # แก้ไขข้อมูล
                    health_data = {
                        "record_date": update_date,
                        "symptoms": symptoms_field.value,
                        "treatment": treatment_field.value,
                        "treated_by": treated_by_field.value,
                        "results": results_dropdown.value,
                    }

                    
                    result = update_health_record(editing_health_id, health_data)

                    if result["success"]:
                        show_success(result["message"])
                        switch_to_main()
                    else:
                        show_error(result["message"])

            except ValueError:
                show_error("รูปแบบวันที่ไม่ถูกต้อง")
            except Exception as e:
                show_error(f"เกิดข้อผิดพลาด: {str(e)}")

        def cancel_action(e):
            """ยกเลิกการเพิ่ม/แก้ไข"""
            switch_to_main()

        # สร้างฟอร์ม - Responsive Layout
        form_title = "เพิ่มข้อมูลสุขภาพ" if current_view == "add_health" else "แก้ไขข้อมูลสุขภาพ"

        return ft.ResponsiveRow([
            ft.Container(
                content=ft.Column([
                    ft.Text(form_title, size=18, weight=ft.FontWeight.BOLD),
                    error_text,
                    ft.Divider(),
                    
                    # ข้อมูลพื้นฐาน - Responsive
                    ft.Text("ข้อมูลการตรวจ", size=14, weight=ft.FontWeight.BOLD),
                    ft.ResponsiveRow([
                        ft.Container(rat_dropdown, col={"sm": 12, "md": 6, "lg": 6}),
                        ft.Container(record_date_field, col={"sm": 12, "md": 6, "lg": 6}),
                    ]),
                    
                    ft.Divider(),
                    
                    # ข้อมูลการรักษา - Responsive
                    ft.Text("ข้อมูลการรักษา", size=14, weight=ft.FontWeight.BOLD),
                    ft.ResponsiveRow([
                        ft.Container(symptoms_field, col={"sm": 12, "md": 12, "lg": 6}),
                        ft.Container(treatment_field, col={"sm": 12, "md": 12, "lg": 6}),
                    ]),
                    ft.ResponsiveRow([
                        ft.Container(treated_by_field, col={"sm": 12, "md": 6, "lg": 6}),
                        ft.Container(results_dropdown, col={"sm": 12, "md": 6, "lg": 6}),
                    ]),
                    
                    ft.Divider(),
                    base_empty_box(2),
                    
                    # ปุ่ม - Responsive
                    ft.Column([
                        ft.Container(
                            content=base_button_gradient(
                                button_name="บันทึก",
                                on_click=save_health_data,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=base_button_normal(
                                button_name="ยกเลิก",
                                on_click=cancel_action,
                                background_color=White,
                                text_color=Black,
                            ),
                            expand=True,
                        ),
                    ]),
                ], spacing=15),
                padding=20,
                expand=True,
                border_radius=5,
                bgcolor=White,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=1,
                    color=ft.Colors.GREY_300,
                    offset=ft.Offset(0, 1),
                ),
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)

    def build_history():
        """แสดงประวัติการรักษาของหนูตัวหนึ่ง - Responsive"""
        if not viewing_rat_id:
            return ft.Text("ไม่พบข้อมูล")

        history = get_health_records_by_rat_id(viewing_rat_id)

        def back_to_main(e):
            switch_to_main()

        if not history:
            return ft.ResponsiveRow([
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=back_to_main,
                                icon_color=Deep_Purple,
                            ),
                            ft.Text(
                                f"ประวัติการรักษา - หนู {viewing_rat_id}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]),
                        ft.Container(
                            content=ft.Text("ไม่มีประวัติการรักษา", color=Grey, size=14),
                            alignment=ft.alignment.center,
                            height=200,
                        ),
                    ]),
                    col={"sm": 12, "md": 10, "lg": 8}
                )
            ], alignment=ft.MainAxisAlignment.CENTER)

        history_cards = []
        for record in history:
            # กำหนดสีตามสถานะ
            status_color = (
                Red if record["results"] == "sick"
                else ft.Colors.ORANGE if record["results"] == "recovering"
                else ft.Colors.BLUE if record["results"] == "monitoring"
                else ft.Colors.GREEN if record["results"] == "healed"
                else ft.Colors.BLACK if record["results"] == "dead"
                else ft.Colors.GREY
            )

            status_text = {
                "sick": "ป่วย",
                "recovering": "พักฟื้น",
                "monitoring": "เฝ้าระวัง",
                "healed": "หายแล้ว",
                "dead": "เสียชีวิต",
            }.get(record["results"], record["results"])

            card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(
                                f"วันที่: {record['record_date']}",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(
                                content=ft.Text(status_text, color=status_color, size=10),
                                bgcolor=ft.Colors.with_opacity(0.1, status_color),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=12,
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(f"อาการ: {record['symptoms']}", size=12, color=Grey),
                        ft.Text(f"การรักษา: {record['treatment']}", size=12, color=Grey),
                        ft.Text(f"ผู้รักษา: {record['treated_by']}", size=11, color=Grey),
                    ]),
                    padding=15,
                ),
                margin=ft.margin.only(bottom=10),
            )
            history_cards.append(card)

        return ft.ResponsiveRow([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=back_to_main,
                            icon_color=Deep_Purple,
                        ),
                        ft.Text(
                            f"ประวัติการรักษา - หนู {viewing_rat_id}",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ]),
                    ft.Column(history_cards),
                ]),
                col={"sm": 12, "md": 10, "lg": 8}
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

    def build_main_content():
        """เนื้อหาหลัก - Responsive"""

        def add_new_health(e):
            """เปิดฟอร์มเพิ่มข้อมูลสุขภาพ"""
            nonlocal current_view
            current_view = "add_health"
            refresh_view()

        def apply_filter(filter_type):
            """กรองข้อมูลตามสถานะ"""
            nonlocal current_filter
            current_filter = filter_type
            
            # อัพเดทสีปุ่มก่อน
            update_filter_buttons()
            
            # จากนั้นรีเฟรชการ์ด
            refresh_cards()

        def update_filter_buttons():
            """อัพเดทสีปุ่มกรองตามสถานะปัจจุบัน"""
            # อัพเดทสีปุ่ม "ทั้งหมด"
            filter_buttons.controls[0].content.bgcolor = Deep_Purple if current_filter == "all" else White
            filter_buttons.controls[0].content.color = White if current_filter == "all" else Black
            
            # อัพเดทสีปุ่ม "ป่วย"
            filter_buttons.controls[1].content.bgcolor = Deep_Purple if current_filter == "sick" else White
            filter_buttons.controls[1].content.color = White if current_filter == "sick" else Black
            
            # อัพเดทสีปุ่ม "พักฟื้น"
            filter_buttons.controls[2].content.bgcolor = Deep_Purple if current_filter == "recovering" else White
            filter_buttons.controls[2].content.color = White if current_filter == "recovering" else Black
            
            # อัพเดทสีปุ่ม "เฝ้าระวัง"
            filter_buttons.controls[3].content.bgcolor = Deep_Purple if current_filter == "monitoring" else White
            filter_buttons.controls[3].content.color = White if current_filter == "monitoring" else Black
            
            # อัพเดท UI
            filter_buttons.update()

        def edit_health_record(health_id):
            """แก้ไขข้อมูลการรักษา"""
            nonlocal current_view, editing_health_id
            current_view = "edit_health"
            editing_health_id = health_id
            refresh_view()

        

        def view_full_history(rat_id):
            """ดูประวัติการรักษาทั้งหมด"""
            nonlocal current_view, viewing_rat_id
            current_view = "history"
            viewing_rat_id = rat_id
            refresh_view()

        def delete_health(health_id):
            delete_health_record(health_id)
            refresh_view()

        # ปุ่มกรอง - Responsive
        filter_buttons = ft.Row([
            ft.Container(
                content=ft.ElevatedButton(
                    "ทั้งหมด",
                    bgcolor=Deep_Purple if current_filter == "all" else White,
                    color=White if current_filter == "all" else Black,
                    on_click=lambda e: apply_filter("all"),
                ),
                expand=True
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    "ป่วย",
                    bgcolor=Deep_Purple if current_filter == "sick" else White,
                    color=White if current_filter == "sick" else Black,
                    on_click=lambda e: apply_filter("sick"),
                ),
                expand=True
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    "พักฟื้น",
                    bgcolor=Deep_Purple if current_filter == "recovering" else White,
                    color=White if current_filter == "recovering" else Black,
                    on_click=lambda e: apply_filter("recovering"),
                ),
                expand=True
            ),
            ft.Container(
                content=ft.ElevatedButton(
                    "เฝ้าระวัง",
                    bgcolor=Deep_Purple if current_filter == "monitoring" else White,
                    color=White if current_filter == "monitoring" else Black,
                    on_click=lambda e: apply_filter("monitoring"),
                ),
                expand=True
            ),
        ])

        # สร้างการ์ดแสดงข้อมูล - Responsive Grid
        def create_health_cards():
            records = get_all_health_records()

            # กรองตามสถานะ
            if current_filter != "all":
                records = [r for r in records if r["results"] == current_filter]

            if not records:
                return ft.ResponsiveRow([
                    ft.Container(
                        content=ft.Text("ไม่มีข้อมูลสุขภาพ", color=Grey, size=14),
                        alignment=ft.alignment.center,
                        height=200,
                        col=12
                    )
                ])

            cards = []
            for record in records:
                # คำนวณอายุ
                age_text = "ไม่ทราบ"
                try:
                    if record["birth_date"]:
                        birth_date = datetime.strptime(str(record["birth_date"]), "%Y-%m-%d")
                        age_days = (datetime.now() - birth_date).days
                        age_months = age_days // 30
                        age_text = f"{age_months} เดือน" if age_months >= 1 else f"{age_days} วัน"
                except:
                    pass

                # สถานะและสี
                status_color = (
                    Red if record["results"] == "sick"
                    else ft.Colors.ORANGE if record["results"] == "recovering"
                    else ft.Colors.BLUE if record["results"] == "monitoring"
                    else ft.Colors.GREEN if record["results"] == "healed"
                    else ft.Colors.BLACK if record["results"] == "dead"
                    else ft.Colors.GREY
                )

                status_text = {
                    "sick": "ป่วย",
                    "recovering": "พักฟื้น",
                    "monitoring": "เฝ้าระวัง",
                    "healed": "หายแล้ว",
                    "dead": "เสียชีวิต",
                }.get(record["results"], record["results"])
                
                gender_text = "ตัวผู้" if record["gender"] == "male" else "ตัวเมีย"
                gender_color = ft.Colors.BLUE_500 if record["gender"] == "male" else ft.Colors.RED_500

                card = ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                # หัวการ์ด
                                ft.Row([
                                    ft.Text(
                                        f"ห่วงขา: {record['ring_number'] or 'ไม่มี'}",
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(gender_text, color=gender_color, size=10),
                                    ft.Container(
                                        content=ft.Text(status_text, color=status_color, size=10),
                                        bgcolor=ft.Colors.with_opacity(0.1, status_color),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=12,
                                    ),
                                    ft.Container(
                                        content=ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_color=Grey,
                                            icon_size=13,
                                            tooltip="ลบ",
                                            on_click=lambda e, id=record[
                                                "health_id"
                                            ]: delete_health(
                                                id
                                            ),
                                        ),
                                        margin=ft.margin.only(
                                            top=-15, right=-10
                                        ),
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                
                                # ข้อมูลหนู
                                ft.Text(f"สายพันธุ์: {record['breed'] or '-'}", size=12, color=Grey),
                                
                                # ข้อมูลสถานที่และอายุ - Responsive
                                ft.Row([
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Text("อายุ", size=12, color=Grey),
                                            ft.Text(age_text, size=12, weight=ft.FontWeight.BOLD),
                                        ], horizontal_alignment=ft.CrossAxisAlignment.START),
                                        padding=ft.padding.all(8),
                                        bgcolor=ft.Colors.GREY_100,
                                        border_radius=5,
                                        expand=True,
                                    ),
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Text("ตรวจล่าสุด", size=12, color=Grey),
                                            ft.Text(record["record_date"], size=12, weight=ft.FontWeight.BOLD),
                                        ], horizontal_alignment=ft.CrossAxisAlignment.START),
                                        padding=ft.padding.all(8),
                                        bgcolor=ft.Colors.GREY_100,
                                        border_radius=5,
                                        expand=True,
                                    ),
                                ]),
                                
                                # ปุ่มจัดการ - Responsive
                                ft.ResponsiveRow([
                                    ft.Container(
                                        content=ft.ElevatedButton(
                                            "บันทึกการรักษา",
                                            style=ft.ButtonStyle(bgcolor=Deep_Purple, color=White),
                                            on_click=lambda e, health_id=record["health_id"]: edit_health_record(health_id),
                                        ),
                                        col={"xs": 12, "sm": 6, "md": 6}
                                    ),
                                    ft.Container(
                                        content=ft.TextButton(
                                            "ประวัติทั้งหมด",
                                            style=ft.ButtonStyle(color=Deep_Purple, bgcolor=White),
                                            on_click=lambda e, rat_id=record["rat_id"]: view_full_history(rat_id),
                                        ),
                                        col={"xs": 12, "sm": 6, "md": 6}
                                    ),
                                ]),
                            ]),
                            padding=15,
                        ),
                        margin=ft.margin.only(bottom=10, right=5, left=5),
                    ),
                    expand=True,
                )
                cards.append(card)

            return ft.ResponsiveRow(cards)

        # สร้าง UI หลัก
        health_cards_container = ft.Container()

        def refresh_cards():
            """รีเฟรชการ์ด"""
            health_cards_container.content = create_health_cards()
            health_cards_container.update()

        # เริ่มต้นแสดงการ์ด
        health_cards_container.content = create_health_cards()

        return ft.Column([
            # ปุ่มเพิ่มข้อมูลใหม่ - Responsive
            ft.ResponsiveRow([
                ft.Container(
                    content=base_button_gradient(
                        button_name="บันทึกตรวจสุขภาพ",
                        icon="ADD_CIRCLE_OUTLINE",
                        on_click=add_new_health,
                    ),
                    expand=True,
                    margin=ft.margin.only(bottom=10, top=1),
                ),
            ]),
            
            # ส่วนกรอง - Responsive
            ft.Container(
                content=ft.Column([
                    filter_buttons,
                ]),
                padding=10,
                bgcolor=White,
                border_radius=10,
                margin=ft.margin.only(bottom=10),
                shadow=ft.BoxShadow(
                    spread_radius=0.1,
                    blur_radius=4,
                    color=Grey,
                    offset=ft.Offset(0, 0),
                ),
            ),
            
            # รายการข้อมูลสุขภาพ
            ft.Container(
                content=ft.Text("รายการข้อมูลสุขภาพ", size=15, weight=ft.FontWeight.BOLD, color=Black),
                margin=ft.margin.only(bottom=10)
            ),
            health_cards_container,
        ])

    def show_error(message):
        """แสดงข้อความแจ้งเตือนข้อผิดพลาด"""
        error_text.value = message
        error_text.visible = True
        error_text.color = ft.Colors.RED_500
        list_view.update()

    def show_success(message):
        """แสดงข้อความแจ้งเตือนสำเร็จ"""
        error_text.value = message
        error_text.visible = True
        error_text.color = ft.Colors.GREEN_500
        list_view.update()

    def switch_to_main():
        """กลับไปหน้าหลัก"""
        nonlocal current_view, editing_health_id, viewing_rat_id
        current_view = "main"
        editing_health_id = None
        viewing_rat_id = None
        error_text.visible = False
        refresh_view()

    def refresh_view():
        """รีเฟรชหน้าจอตามสถานะปัจจุบัน"""
        if current_view == "main":
            list_view.controls = [build_main_content()]
    def refresh_view():
        """รีเฟรชหน้าจอตามสถานะปัจจุบัน"""
        if current_view == "main":
            list_view.controls = [build_main_content()]
        elif current_view == "add_health":
            list_view.controls = [build_add_health()]
        elif current_view == "edit_health":
            list_view.controls = [build_add_health()]
        elif current_view == "history":
            list_view.controls = [build_history()]

        list_view.update()

    # สร้าง ListView หลัก
    list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.padding.only(top=20, bottom=20, left=5, right=5),
        controls=[build_main_content()],
    )

    return list_view