import flet as ft
from components.base_button import (
    base_button_gradient,
    base_button_normal_v2,
)
from storages.database_service import (
    get_farm_by_farm_id,
    get_ponds_by_farm_id,
    get_rats_by_farm_and_pond,
    update_pond_status,
)
from storages.general_information import update_hmt_page
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, Red, White


def pond_page(farm_id):
    # ตัวแปรสำหรับเก็บ pond_id ที่กำลังแก้ไขสถานะ
    editing_pond_id = None

    # ฟังก์ชันสร้างการ์ดบ่อ
    def create_pond_card(pond):
        pond_id = pond["pond_id"]
        current_status = pond["status"]
        rats = get_rats_by_farm_and_pond(farm_id, pond_id)
        father_count = rats['father_ring_number'] if rats['father_ring_number'] is not None else "-"
        mother_count = rats['mother_ring_number'] if rats['mother_ring_number'] is not None else "-"

        # ตรวจสอบว่าการ์ดนี้กำลังอยู่ในโหมดแก้ไขหรือไม่
        is_editing = editing_pond_id == pond_id

        # สร้างสถานะของบ่อเป็นข้อความที่มีสี
        status_text = ""
        status_color = Black

        if current_status == "empty":
            status_text = "ว่าง"
            status_color = Neo_Mint
        elif current_status == "work":
            status_text = "ใช้งาน"
            status_color = ft.Colors.ORANGE
        elif current_status == "maintenance":
            status_text = "ซ่อมบำรุง"
            status_color = Red

        # ฟังก์ชันเมื่อกดปุ่มสถานะ
        def on_status_button_click(e):
            nonlocal editing_pond_id
            editing_pond_id = pond_id
            refresh_pond_list()

        # ฟังก์ชันเมื่อเลือกสถานะใหม่
        def on_status_change(e, new_status):
            if new_status != current_status:
                success = update_pond_status(farm_id, pond_id, new_status)

                if success and hasattr(e, "page") and e.page:
                    # แสดงข้อความแจ้งเตือน
                    e.page.snack_bar = ft.SnackBar(
                        content=ft.Text("บันทึกสถานะบ่อเรียบร้อยแล้ว"),
                        bgcolor=Neo_Mint,
                    )
                    e.page.snack_bar.open = True
                    e.page.update()

            # ปิดโหมดแก้ไข
            nonlocal editing_pond_id
            editing_pond_id = None
            # รีเฟรชหน้าจอเพื่อแสดงข้อมูลบ่อที่อัพเดตแล้ว
            refresh_pond_list()

        # ฟังก์ชันยกเลิกการแก้ไข
        def on_cancel(e):
            nonlocal editing_pond_id
            editing_pond_id = None
            refresh_pond_list()

        # สร้างเนื้อหาตามโหมดที่เลือก
        if is_editing:
            # โหมดแก้ไขสถานะ - แสดงตัวเลือกสถานะ
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.CIRCLE,
                                        color=Neo_Mint,
                                        size=12,
                                    ),
                                    ft.Text("ว่าง", size=12),
                                ],
                                spacing=2,
                            ),
                            on_click=lambda e: on_status_change(e, "empty"),
                            bgcolor=(
                                ft.Colors.GREY_50 if current_status == "empty" else None
                            ),
                            padding=4,
                            border_radius=5,
                            margin=ft.margin.only(bottom=1),
                        ),
                        # ตัวเลือกสถานะใช้งาน
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.CIRCLE,
                                        color=ft.Colors.ORANGE,
                                        size=12,
                                    ),
                                    ft.Text("ใช้งาน", size=12),
                                ],
                                spacing=5,
                            ),
                            on_click=lambda e: on_status_change(e, "work"),
                            bgcolor=(
                                ft.Colors.GREY_50 if current_status == "work" else None
                            ),
                            padding=4,
                            border_radius=5,
                            margin=ft.margin.only(bottom=1),
                        ),
                        # ตัวเลือกสถานะซ่อมบำรุง
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.CIRCLE,
                                        color=Red,
                                        size=12,
                                    ),
                                    ft.Text("ซ่อมบำรุง", size=12),
                                ],
                                spacing=5,
                            ),
                            on_click=lambda e: on_status_change(e, "maintenance"),
                            bgcolor=(
                                ft.Colors.GREY_50
                                if current_status == "maintenance"
                                else None
                            ),
                            padding=4,
                            border_radius=5,
                            margin=ft.margin.only(bottom=1),
                        ),
                        ft.Divider(height=1, color=ft.Colors.GREY_300, thickness=1),
                        ft.Container(
                            content=ft.Text("ยกเลิก", size=13, color=ft.Colors.GREY_500),
                            on_click=on_cancel,
                            padding=4,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                bgcolor=White,
                border_radius=6,
                margin=ft.margin.only(left=2, right=2, top=2, bottom=2),
                shadow=ft.BoxShadow(
                    spread_radius=0.1,
                    blur_radius=5,
                    color=ft.Colors.with_opacity(0.2, Grey),
                    offset=ft.Offset(0, 2),
                ),
                width=110,
            )
        else:
            # โหมดปกติ - แสดงข้อมูลบ่อ
            return ft.Container(
                content=ft.Column(
                    [
                        # ส่วนหัว: ชื่อบ่อและสถานะ
                        ft.Row(
                            [
                                # ชื่อบ่อ (ซ้าย)
                                ft.Container(
                                    content=ft.Text(
                                        f"{pond['pond_name']}",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    margin=10,
                                ),
                                # สถานะบ่อ (ขวา)
                                ft.Container(
                                    content=ft.Text(
                                        status_text,
                                        color=status_color,
                                        size=10,
                                    ),
                                    margin=10,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        # ส่วนข้อมูลพ่อพันธุ์-แม่พันธุ์
                        ft.Container(
                            content=ft.Row(
                                [
                                    # คอลัมน์ซ้าย: พ่อพันธุ์
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("พ่อพันธุ์", size=10, color=Grey),
                                                ft.Text(
                                                    f"{father_count}",
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=1,
                                        ),
                                        bgcolor=ft.Colors.GREY_100,
                                        padding=6,
                                        border_radius=10,
                                    ),
                                    # คอลัมน์ขวา: แม่พันธุ์
                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Text("แม่พันธุ์", size=10, color=Grey),
                                                ft.Text(
                                                    f"{mother_count}",
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=1,
                                        ),
                                        bgcolor=ft.Colors.GREY_100,
                                        padding=6,
                                        border_radius=10,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            margin=ft.margin.only(top=-15),
                        ),
                        # ส่วนปุ่มสถานะด้านล่าง
                        base_button_normal_v2(
                            button_name="สถานะ",
                            icon="EDIT_OUTLINED",
                            on_click=on_status_button_click,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=White,
                border_radius=6,
                margin=ft.margin.only(left=2, right=2, top=2, bottom=2),
                shadow=ft.BoxShadow(
                    spread_radius=0.1,
                    blur_radius=5,
                    color=ft.Colors.with_opacity(0.2, Grey),
                    offset=ft.Offset(0, 2),
                ),
                width=110,
            )

    # ฟังก์ชันดึงข้อมูลบ่อและเรียงลำดับตาม pond_id
    def get_sorted_ponds():
        ponds = get_ponds_by_farm_id(farm_id)
        # เรียงลำดับตาม pond_id
        sorted_ponds = sorted(ponds, key=lambda x: x.get("pond_id", 0))
        return sorted_ponds

    # ตัวแปรสำหรับการแบ่งหน้า
    current_page = 1
    items_per_page = 30

    # ฟังก์ชันรีเฟรชรายการบ่อ
    def refresh_pond_list():
        list_view.controls = [build_main_content()]
        list_view.update()

    # ฟังก์ชันเพื่อสร้างเนื้อหาส่วนแสดงบ่อและปุ่มเปลี่ยนหน้า
    def build_pond_content():
        all_ponds = get_sorted_ponds()
        total_ponds = len(all_ponds)
        total_pages = max(
            1, (total_ponds + items_per_page - 1) // items_per_page
        )  # อย่างน้อย 1 หน้า

        # ถ้าหน้าปัจจุบันเกินจำนวนหน้าทั้งหมด ให้กลับไปหน้าสุดท้าย
        nonlocal current_page
        if current_page > total_pages:
            current_page = total_pages

        # คำนวณ index เริ่มต้นและสิ้นสุดของบ่อที่จะแสดงในหน้าปัจจุบัน
        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_ponds)

        # เลือกบ่อที่จะแสดงในหน้าปัจจุบัน
        ponds_to_display = all_ponds[start_idx:end_idx] if all_ponds else []

        # สร้างการ์ดบ่อทั้งหมดที่จะแสดงในหน้านี้
        pond_cards = [create_pond_card(pond) for pond in ponds_to_display]

        # ใช้ Row ที่มี wrap=True เพื่อแสดงบ่อตามขนาดหน้าจอ
        pond_row = ft.Row(
            controls=pond_cards,
            wrap=True,
            spacing=5,
            run_spacing=10,
            alignment=ft.MainAxisAlignment.START,
        )

        # สร้างปุ่มเปลี่ยนหน้า
        def on_prev_page(e):
            nonlocal current_page
            if current_page > 1:
                current_page -= 1
                # รีเซ็ตการแก้ไขเมื่อเปลี่ยนหน้า
                nonlocal editing_pond_id
                editing_pond_id = None
                # สร้าง UI ใหม่ทั้งหมดแทนการอัพเดต
                list_view.controls = [build_main_content()]
                list_view.update()

        def on_next_page(e):
            nonlocal current_page
            if current_page < total_pages:
                current_page += 1
                # รีเซ็ตการแก้ไขเมื่อเปลี่ยนหน้า
                nonlocal editing_pond_id
                editing_pond_id = None
                # สร้าง UI ใหม่ทั้งหมดแทนการอัพเดต
                list_view.controls = [build_main_content()]
                list_view.update()

        # สร้าง pagination UI
        pagination_row = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=on_prev_page,
                    disabled=current_page <= 1,
                    tooltip="หน้าก่อนหน้า",
                ),
                ft.Text(f"หน้า {current_page} จาก {total_pages}", size=14),
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=on_next_page,
                    disabled=current_page >= total_pages,
                    tooltip="หน้าถัดไป",
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        # ส่งคืนทั้ง pond_row และ pagination_row
        return ft.Column(
            [
                ft.Container(
                    content=pond_row,
                    padding=10,
                    alignment=ft.alignment.center,  # เพิ่ม alignment
                    width=None,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_300, thickness=1),
                ft.Container(content=pagination_row, margin=ft.margin.only(top=5)),
            ],
            spacing=5,
        )


    # ฟังก์ชันสร้าง UI หลักทั้งหมด
    def build_main_content():
        return ft.Column(
            [
                # ft.Container(
                #     content=base_button_gradient(
                #         button_name="เพิ่มบ่อเลี้ยงใหม่",
                #         icon="ADD_CIRCLE",
                #         on_click=add_new_farm,
                #     ),
                #     margin=ft.margin.only(bottom=10, top=1, left=5, right=5),
                # ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("บ่อเลี้ยงทั้งหมด", size=15, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=5,
                    ),
                    margin=ft.margin.only(left=10),
                ),
                build_pond_content(),
            ],
            spacing=5,
            expand=True,
        )

    # สร้าง ListView หลัก
    list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.padding.only(top=20, bottom=20, left=5, right=5),
        controls=[build_main_content()],
    )

    return list_view
