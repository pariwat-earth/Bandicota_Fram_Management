import flet as ft
from components.base_box import (
    base_emergency_report_box,
    base_empty_box,
    base_info_report_box,
    base_pairing_report_box,
)
from components.base_button import (
    base_button_with_icon,
)
from components.build_albino_trend_chart import build_albino_trend_chart
from main_calculate.notification import get_expire_rat_notifications
from storages.general_information import (
    get_amount_rat,
    get_breeding_information,
    get_breeding_rat,
    get_breeding_success_rate,
    get_current_breeding_pair,
)
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, Red

page_name = "ฟาร์มรัก"


def print_name(e):
    print(page_name)


def get_report_notification(
    change_content_callback=None, content_functions=None, nav_indices=None
):
    """
    สร้างการแจ้งเตือนรวมระหว่างหนูที่หมดอายุและแจ้งเตือนอื่นๆ
    """

    # ฟังก์ชันสำหรับเปลี่ยนไปหน้าการแจ้งเตือน
    def show_all_notifications_page(e):
        if change_content_callback and content_functions:
            nav_index = nav_indices.get("notifications") if nav_indices else None
            change_content_callback(content_functions["notifications"], nav_index)

    # ดึงการแจ้งเตือนหนูที่หมดอายุจากหน้าอื่น
    expire_notifications = []
    try:
        expire_notifications = get_expire_rat_notifications()
        # แปลง color string เป็น color object
        for notification in expire_notifications:
            if notification["color"] == "Red":
                notification["color"] = Red
            elif notification["color"] == "Neo_Mint":
                notification["color"] = Neo_Mint
    except:
        expire_notifications = []

    other_notifications = []

    # รวมการแจ้งเตือนทั้งหมด โดยให้หนูที่หมดอายุมาก่อน
    all_notifications = expire_notifications + other_notifications

    # เรียงลำดับตามความสำคัญ (emergency ก่อน normal)
    all_notifications.sort(key=lambda x: (0 if x["type"] == "emergency" else 1))

    # จำกัดจำนวนการแจ้งเตือนที่จะแสดง
    limit = 4
    notifications_to_show = all_notifications[:limit]

    # สร้าง UI elements
    notification_elements = [
        ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        "การแจ้งเตือน", size=15, color=Black, weight=ft.FontWeight.BOLD
                    ),
                    margin=10,
                ),
                ft.Container(
                    content=ft.TextButton(
                        "ดูทั้งหมด",
                        style=ft.ButtonStyle(
                            color=Deep_Purple,
                            text_style=ft.TextStyle(size=10),
                            padding=ft.padding.all(0),
                            overlay_color=ft.Colors.TRANSPARENT,
                            surface_tint_color=ft.Colors.TRANSPARENT,
                            shadow_color=ft.Colors.TRANSPARENT,
                            elevation=0,
                        ),
                        on_click=show_all_notifications_page,
                    ),
                    margin=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    ]

    if not notifications_to_show:
        notification_elements.append(
            ft.Container(
                content=ft.Text("ไม่มีการแจ้งเตือน", size=12, color=Grey),
                margin=10,
            )
        )
    else:
        for notification in notifications_to_show:
            notification_elements.append(
                ft.Row(
                    [
                        base_empty_box(2),
                        base_emergency_report_box(
                            topic=notification["topic"],
                            content=notification["content"],
                            color=notification["color"],
                        ),
                        base_empty_box(2),
                    ]
                )
            )
            notification_elements.append(base_empty_box(5))

    return notification_elements


def get_breeding_pair(
    change_content_callback=None, content_functions=None, nav_indices=None
):
    """
    แสดงการผสมพันธุ์ล่าสุด พร้อมปุ่มดูทั้งหมด
    """

    # ฟังก์ชันสำหรับเปลี่ยนไปหน้าการผสมพันธุ์
    def show_all_breeding_page(e):
        if change_content_callback and content_functions:
            nav_index = nav_indices.get("mating") if nav_indices else None
            change_content_callback(content_functions["mating"], nav_index)

    # จำกัดจำนวนการแจ้งเตือนที่จะแสดง
    limit = 2
    breeding_to_show = get_breeding_information()[:limit]

    breeding_elements = [
        ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        "การผสมพันธุ์ล่าสุด", size=15, color=Black, weight=ft.FontWeight.BOLD
                    ),
                    margin=10,
                ),
                ft.Container(
                    content=ft.TextButton(
                        "ดูทั้งหมด",
                        style=ft.ButtonStyle(
                            color=Deep_Purple,
                            text_style=ft.TextStyle(size=10),
                            padding=ft.padding.all(0),
                            overlay_color=ft.Colors.TRANSPARENT,
                            surface_tint_color=ft.Colors.TRANSPARENT,
                            shadow_color=ft.Colors.TRANSPARENT,
                            elevation=0,
                        ),
                        on_click=show_all_breeding_page,
                    ),
                    margin=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    ]

    if not breeding_to_show:
        breeding_elements.append(
            ft.Container(
                content=ft.Text("ไม่มีการผสมพันธุ์ล่าสุด", size=12, color=Grey),
                margin=10,
            )
        )
    else:
        for breeding in breeding_to_show:
            breeding_elements.append(
                ft.Row(
                    [
                        base_empty_box(2),
                        base_pairing_report_box(
                            topic=breeding["topic"],
                            content=breeding["content"],
                            result=breeding["result"],
                            color_base=breeding["color"],
                        ),
                        base_empty_box(2),
                    ]
                )
            )
            breeding_elements.append(base_empty_box(5))

    return breeding_elements


def main_page(change_content_callback=None, content_functions=None, nav_indices=None):

    # ฟังก์ชันสำหรับ handle การกดปุ่ม
    def on_mating_click(e):
        if change_content_callback and content_functions:
            nav_index = nav_indices.get("mating") if nav_indices else None
            change_content_callback(content_functions["mating"], nav_index)

    def on_add_click(e):
        if change_content_callback and content_functions:
            nav_index = nav_indices.get("mouse_info") if nav_indices else None
            change_content_callback(content_functions["mouse_info"], nav_index)

    def on_health_click(e):
        if change_content_callback and content_functions:
            nav_index = nav_indices.get("health") if nav_indices else None
            change_content_callback(content_functions["health"], nav_index)

    def on_report_click(e):
        if change_content_callback and content_functions:
            nav_index = nav_indices.get("report") if nav_indices else None
            change_content_callback(content_functions["report"], nav_index)

    controls = [
        base_empty_box(5),
        # แถวหลัก - 4 ปุ่มใหญ่ทำให้ responsive
        ft.Row(
            [
                ft.Container(
                    content=base_button_with_icon(
                        "ผสมพันธุ์ใหม่", "FAVORITE", on_mating_click
                    ),
                    expand=True,
                ),
                ft.Container(
                    content=base_button_with_icon(
                        "เพิ่มหนูใหม่", "ADD_CIRCLE", on_add_click
                    ),
                    expand=True,
                ),
                ft.Container(
                    content=base_button_with_icon(
                        "บันทึกสุขภาพ", "LOCAL_HOSPITAL", on_health_click
                    ),
                    expand=True,
                ),
                ft.Container(
                    content=base_button_with_icon(
                        "รายงานและสถิติ", "LIBRARY_BOOKS", on_report_click
                    ),
                    expand=True,
                ),
            ]
        ),
        base_empty_box(5),
        ft.Container(
            content=ft.Text(
                "ภาพรวมฟาร์ม", size=15, color=Black, weight=ft.FontWeight.BOLD
            ),
            margin=10,
        ),
        # ภาพรวมฟาร์ม - responsive
        ft.Row(
            [
                ft.Container(
                    content=base_info_report_box(
                        topic="จำนวนหนูทั้งหมด",
                        content=get_amount_rat(),
                        units="ตัว",
                        color=Neo_Mint,
                    ),
                    expand=True,
                ),
                ft.Container(
                    content=base_info_report_box(
                        topic="จำนวนหนูที่ผสมพันธุ์",
                        content=get_breeding_rat(),
                        units="ตัว",
                        color=Deep_Purple,
                    ),
                    expand=True,
                ),
            ]
        ),
        base_empty_box(5),
        ft.Row(
            [
                ft.Container(
                    content=base_info_report_box(
                        topic="คู่ผสมพันธุ์ปัจจุบัน",
                        content=get_current_breeding_pair(),
                        units="คู่",
                        color=Neo_Mint,
                    ),
                    expand=True,
                ),
                ft.Container(
                    content=base_info_report_box(
                        topic="อัตราความสำเร็จ",
                        content=get_breeding_success_rate(),
                        units="%",
                        color=Deep_Purple,
                    ),
                    expand=True,
                ),
            ]
        ),
    ]

    # เพิ่ม notifications
    controls.extend(
        get_report_notification(change_content_callback, content_functions, nav_indices)
    )

    # เพิ่ม breeding pair
    controls.extend(
        get_breeding_pair(change_content_callback, content_functions, nav_indices)
    )

    controls.extend(
        [
            base_empty_box(5),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            "แนวโน้มหนูเผือกตาแดง",
                            size=15,
                            color=Black,
                            weight=ft.FontWeight.BOLD,
                        ),
                        margin=10,
                    ),
                    ft.Container(
                        content=ft.TextButton(
                            "ดูรายงานเต็ม",
                            style=ft.ButtonStyle(
                                color=Deep_Purple,
                                text_style=ft.TextStyle(size=10),
                                padding=ft.padding.all(0),
                                overlay_color=ft.Colors.TRANSPARENT,
                                surface_tint_color=ft.Colors.TRANSPARENT,
                                shadow_color=ft.Colors.TRANSPARENT,
                                elevation=0,
                            ),
                            on_click=lambda e: on_report_click(e),
                        ),
                        margin=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            build_albino_trend_chart(),
            base_empty_box(20),
        ]
    )

    return ft.ListView(
        controls=controls,
        expand=True,
        spacing=0,
        padding=ft.padding.all(10),
        auto_scroll=False,
    )
