from datetime import date
import flet as ft
from components.base_box import base_empty_box
from components.base_button import base_button_normal, base_button_normal_v2
from main_calculate.advice_breed import get_best_pair_breeding_per_pound
from storages.database_service import (
    add_breed_data,
    get_empty_pond_by_farm_id,
    get_rat_id_by_ring_number,
    update_pond_status,
    update_rat_pond,
    update_rat_status,
)
from styles.colors import Black, Deep_Purple, Neo_Mint, White


def breeding_ad():

    custom_weights = {"size": 25, "breeding": 25, "health": 25, "lineage": 25}

    # ตัวแปรควบคุมการแสดงส่วนตั้งค่า
    is_settings_expanded = False

    # สร้าง TextField สำหรับแต่ละน้ำหนัก
    size_weight_field = ft.TextField(
        label="ขนาดและน้ำหนัก",
        value=str(custom_weights["size"]),
        dense=True,
        text_size=13,
        content_padding=ft.padding.all(8),
    )

    breeding_weight_field = ft.TextField(
        label="จำนวนลูก",
        value=str(custom_weights["breeding"]),
        dense=True,
        text_size=13,
        content_padding=ft.padding.all(8),
    )

    health_weight_field = ft.TextField(
        label="สุขภาพ",
        value=str(custom_weights["health"]),
        dense=True,
        text_size=13,
        content_padding=ft.padding.all(8),
    )

    lineage_weight_field = ft.TextField(
        label="ความแข็งแกร่ง",
        value=str(custom_weights["lineage"]),
        dense=True,
        text_size=13,
        content_padding=ft.padding.all(8),
    )

    total_score_text = ft.Text("รวม: 100%", size=12, weight=ft.FontWeight.BOLD)
    error_text = ft.Text("", size=10, color=ft.Colors.RED)

    def toggle_settings(e):
        nonlocal is_settings_expanded
        is_settings_expanded = not is_settings_expanded
        settings_container.visible = is_settings_expanded
        settings_button.icon = (
            ft.Icons.SETTINGS if not is_settings_expanded else ft.Icons.CLOSE
        )
        list_view.update()

    def validate_and_update_total():
        """ตรวจสอบและอัพเดทคะแนนรวม"""
        try:
            size_val = int(size_weight_field.value or 0)
            breeding_val = int(breeding_weight_field.value or 0)
            health_val = int(health_weight_field.value or 0)
            lineage_val = int(lineage_weight_field.value or 0)

            total = size_val + breeding_val + health_val + lineage_val
            total_score_text.value = f"รวม: {total}%"

            if total != 100:
                total_score_text.color = ft.Colors.RED
                if total > 100:
                    error_text.value = f"คะแนนเกิน {total - 100} %"
                else:
                    error_text.value = f"คะแนนขาด {100 - total} %"
                error_text.visible = True
            else:
                total_score_text.color = ft.Colors.GREEN
                error_text.value = ""
                error_text.visible = False

        except ValueError:
            total_score_text.value = "รวม: --%"
            total_score_text.color = ft.Colors.RED
            error_text.value = "กรุณากรอกตัวเลขเท่านั้น"
            error_text.visible = True

        # ใช้ try-except เพื่อป้องกันข้อผิดพลาด
        try:
            if total_score_text.page is not None:
                total_score_text.update()
            if error_text.page is not None:
                error_text.update()
        except:
            # ถ้า update ไม่ได้ ให้ update ทั้ง list_view
            list_view.update()

    def on_weight_change(e):
        """เมื่อมีการเปลี่ยนแปลงค่าน้ำหนัก"""
        validate_and_update_total()

    # เพิ่ม event handlers
    size_weight_field.on_change = on_weight_change
    breeding_weight_field.on_change = on_weight_change
    health_weight_field.on_change = on_weight_change
    lineage_weight_field.on_change = on_weight_change

    def apply_weights(e):
        """นำน้ำหนักที่ตั้งค่าไปใช้"""
        try:
            size_val = int(size_weight_field.value or 0)
            breeding_val = int(breeding_weight_field.value or 0)
            health_val = int(health_weight_field.value or 0)
            lineage_val = int(lineage_weight_field.value or 0)

            total = size_val + breeding_val + health_val + lineage_val

            if total != 100:
                return  # ไม่ทำอะไรถ้าคะแนนไม่เท่ากับ 100

            # อัพเดทค่าน้ำหนัก
            custom_weights["size"] = size_val
            custom_weights["breeding"] = breeding_val
            custom_weights["health"] = health_val
            custom_weights["lineage"] = lineage_val

            # แค่ rebuild เฉพาะส่วนผลลัพธ์ ไม่ใช่ทั้งหมด
            rebuild_results()

        except ValueError:
            pass

    def reset_weights(e):
        """รีเซ็ตค่าน้ำหนักเป็นค่าเริ่มต้น"""
        size_weight_field.value = "25"
        breeding_weight_field.value = "25"
        health_weight_field.value = "25"
        lineage_weight_field.value = "25"

        # รีเซ็ต custom_weights ด้วย
        custom_weights["size"] = 25
        custom_weights["breeding"] = 25
        custom_weights["health"] = 25
        custom_weights["lineage"] = 25

        validate_and_update_total()
        
        # อัพเดทผลลัพธ์ด้วย
        rebuild_results()

    def rebuild_results():
        """สร้างผลลัพธ์ใหม่โดยไม่ rebuild TextField"""
        # ลบเฉพาะ cards ผลลัพธ์ (เก็บ header และ settings ไว้)
        header_and_settings = list_view.controls[0].controls[:3]  # header, settings, empty_box
        
        # สร้างผลลัพธ์ใหม่
        result = get_best_pair_breeding_per_pound(custom_weights)
        new_cards = []

        for index, pair in enumerate(result["selected_pairs"]):
            pair_data = pair["pair_info"]
            male_info = pair_data["male"]
            female_info = pair_data["female"]

            today = date.today()
            date_prefix = today.strftime("%Y-%m-%d")
            
            breeding_data = {
                "male_id": male_info["id"],
                "female_id": female_info["id"],
                "pond_id": get_empty_pond_by_farm_id(),
                "inbreeding_coef": float(pair_data["inbreeding_coef"]),
                "status": "breeding",
                "breeding_date": date_prefix,
            }

            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(
                                f"คู่ผสมที่ {index+1}", size=13, weight=ft.FontWeight.BOLD
                            ),
                            margin=ft.margin.only(top=10, left=10),
                        ),
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Container(
                                                content=ft.Text(
                                                    "พ่อพันธุ์",
                                                    size=12,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    f"{male_info['ring_number']}",
                                                    size=14,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    f"น้ำหนัก: {male_info['weight']} กรัม",
                                                    size=12,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                        ]
                                    ),
                                    expand=True,
                                    width=None,
                                    border_radius=5,
                                    padding=10,
                                    margin=ft.margin.only(bottom=15, left=10),
                                    bgcolor=ft.Colors.GREY_50,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0,
                                        blur_radius=0,
                                        color=Deep_Purple,
                                        offset=ft.Offset(-3, 0.1),
                                    ),
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Container(
                                                content=ft.Text(
                                                    "แม่พันธุ์",
                                                    size=12,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    f"{female_info['ring_number']}",
                                                    size=14,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    f"น้ำหนัก: {female_info['weight']} กรัม",
                                                    size=12,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                        ]
                                    ),
                                    expand=True,
                                    width=None,
                                    border_radius=5,
                                    padding=10,
                                    margin=ft.margin.only(bottom=15, right=10),
                                    bgcolor=ft.Colors.GREY_50,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0,
                                        blur_radius=0,
                                        color=Neo_Mint,
                                        offset=ft.Offset(-3, 0.1),
                                    ),
                                ),
                            ]
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"อัตราเลือดชิด: {pair_data['inbreeding_coef']}%",
                                size=10,
                                color=ft.Colors.GREY_600,
                            ),
                            margin=ft.margin.only(top=-15, left=10),
                        ),
                        ft.Container(
                            content=base_button_normal_v2(
                                button_name="เพิ่มคู่ผสมนี้",
                                icon="ADD",
                                on_click=lambda e, breeding_data=breeding_data: add_pair_to_breeding(
                                    breeding_data
                                ),
                            ),
                            height=40,
                        ),
                    ]
                ),
                expand=True,
                width=None,
                border_radius=5,
                margin=ft.margin.only(bottom=15, left=5, right=5),
                bgcolor=White,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color=ft.Colors.GREY_300,
                    offset=ft.Offset(0, 2),
                ),
            )
            new_cards.append(card)

        # อัพเดท controls โดยรวม header+settings กับ cards ใหม่
        list_view.controls[0].controls = header_and_settings + new_cards
        list_view.update()

    def add_pair_to_breeding(breeding_data):
        breeding_save = (
            breeding_data['male_id'],
            breeding_data['female_id'],
            breeding_data['pond_id'],
            breeding_data['inbreeding_coef'],
            breeding_data['status'],
            breeding_data['breeding_date'],
        )

        if add_breed_data(breeding_save):
            update_rat_pond(breeding_data['male_id'], breeding_data['pond_id']),
            update_rat_pond(breeding_data['female_id'], breeding_data['pond_id']),
            update_rat_status(breeding_data['male_id'], 'breeder1'),
            update_rat_status(breeding_data['female_id'], 'breeder1'),
            update_pond_status(1, breeding_data['pond_id'], 'work')
            # อัพเดทผลลัพธ์หลังจากเพิ่มคู่ผสม
            rebuild_results()
        else:
            print("ไม่สามารถเพิ่มข้อมูลการผสมพันธุ์ได้")

    # สร้างปุ่มตั้งค่า
    settings_button = ft.IconButton(
        icon=ft.Icons.SETTINGS,
        icon_size=20,
        tooltip="ตั้งค่าน้ำหนักคะแนน",
        on_click=toggle_settings,
    )

    # สร้างส่วนตั้งค่า - ย้ายออกมาจาก build_main_content
    settings_container = ft.Container(
        content=ft.Column(
            [
                ft.Text("ตั้งค่าน้ำหนักคะแนน", size=14, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Container(
                            content=size_weight_field,
                            expand=True,
                        ),
                        ft.Container(
                            content=breeding_weight_field,
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row(
                    [
                        ft.Container(
                            content=health_weight_field,
                            expand=True,
                        ),
                        ft.Container(
                            content=lineage_weight_field,
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row(
                    [
                        total_score_text,
                        error_text,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row(
                    [
                        ft.Container(
                            content=base_button_normal(
                                button_name="นำไปใช้",
                                on_click=apply_weights,
                                background_color=Neo_Mint,
                                text_color=White,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=base_button_normal(
                                button_name="รีเซ็ต",
                                on_click=reset_weights,
                                background_color=White,
                                text_color=Black,
                            ),
                            expand=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            spacing=10,
        ),
        padding=15,
        margin=ft.margin.only(bottom=10, left=5, right=5),
        bgcolor=White,
        border_radius=8,
        border=ft.border.all(1, ft.Colors.GREY_300),
        visible=is_settings_expanded,
    )

    def build_main_content():
        main_content = [
            # หัวข้อพร้อมปุ่มตั้งค่า
            ft.Row(
                [
                    ft.Text("คำแนะนำการผสมพันธุ์", weight=ft.FontWeight.BOLD, size=18),
                    settings_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            # ส่วนตั้งค่า
            settings_container,
            base_empty_box(5),
        ]

        result = get_best_pair_breeding_per_pound(custom_weights)

        for index, pair in enumerate(result["selected_pairs"]):
            pair_data = pair["pair_info"]
            male_info = pair_data["male"]
            female_info = pair_data["female"]

            today = date.today()
            date_prefix = today.strftime("%Y-%m-%d")
            
            breeding_data = {
                "male_id": male_info["id"],
                "female_id": female_info["id"],
                "pond_id": get_empty_pond_by_farm_id(),
                "inbreeding_coef": float(pair_data["inbreeding_coef"]),
                "status": "breeding",
                "breeding_date": date_prefix,
            }

            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Text(
                                f"คู่ผสมที่ {index+1}", size=13, weight=ft.FontWeight.BOLD
                            ),
                            margin=ft.margin.only(top=10, left=10),
                        ),
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Container(
                                                content=ft.Text(
                                                    "พ่อพันธุ์",
                                                    size=12,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    f"{male_info['ring_number']}",
                                                    size=14,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    f"น้ำหนัก: {male_info['weight']} กรัม",
                                                    size=12,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                        ]
                                    ),
                                    expand=True,
                                    width=None,
                                    border_radius=5,
                                    padding=10,
                                    margin=ft.margin.only(bottom=15, left=10),
                                    bgcolor=ft.Colors.GREY_50,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0,
                                        blur_radius=0,
                                        color=Deep_Purple,
                                        offset=ft.Offset(-3, 0.1),
                                    ),
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Container(
                                                content=ft.Text(
                                                    "แม่พันธุ์",
                                                    size=12,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    f"{female_info['ring_number']}",
                                                    size=14,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    f"น้ำหนัก: {female_info['weight']} กรัม",
                                                    size=12,
                                                    color=ft.Colors.GREY_600,
                                                ),
                                                margin=ft.margin.only(bottom=-5),
                                            ),
                                        ]
                                    ),
                                    expand=True,
                                    width=None,
                                    border_radius=5,
                                    padding=10,
                                    margin=ft.margin.only(bottom=15, right=10),
                                    bgcolor=ft.Colors.GREY_50,
                                    shadow=ft.BoxShadow(
                                        spread_radius=0,
                                        blur_radius=0,
                                        color=Neo_Mint,
                                        offset=ft.Offset(-3, 0.1),
                                    ),
                                ),
                            ]
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"อัตราเลือดชิด: {pair_data['inbreeding_coef']}%",
                                size=10,
                                color=ft.Colors.GREY_600,
                            ),
                            margin=ft.margin.only(top=-15, left=10),
                        ),
                        ft.Container(
                            content=base_button_normal_v2(
                                button_name="เพิ่มคู่ผสมนี้",
                                icon="ADD",
                                on_click=lambda e, breeding_data=breeding_data: add_pair_to_breeding(
                                    breeding_data
                                ),
                            ),
                            height=40,
                        ),
                    ]
                ),
                expand=True,
                width=None,
                border_radius=5,
                margin=ft.margin.only(bottom=15, left=5, right=5),
                bgcolor=White,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color=ft.Colors.GREY_300,
                    offset=ft.Offset(0, 2),
                ),
            )

            main_content.append(card)

        return ft.Column(
            main_content,
            expand=True,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    # สร้าง ListView หลัก
    list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.padding.all(10),
        controls=[build_main_content()],
    )

    return list_view