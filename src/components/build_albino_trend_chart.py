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
from main_calculate.notification import get_expire_rat_notifications
from storages.general_information import (
    get_amount_rat,
    get_breeding_information,
    get_breeding_rat,
    get_breeding_success_rate,
    get_current_breeding_pair,
)
from storages.report_service import get_albino_trend_data  # เพิ่ม import
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, Red

page_name = "ฟาร์มรัก"


def print_name(e):
    print(page_name)


def build_albino_trend_chart():
    """สร้างกราฟแนวโน้มหนูเผือกตาแดงสำหรับหน้าหลัก - Responsive LineChart"""
    # ดึงข้อมูลแนวโน้ม 1 เดือนล่าสุด
    albino_data = get_albino_trend_data("1M")

    # ถ้าไม่มีข้อมูล หรือข้อมูลเป็น 0 ทั้งหมด ให้ใช้ sample data
    # if not albino_data or len(albino_data) == 0 or all(x == 0 for x in albino_data):
    #     # ใช้ sample data สำหรับ 1 เดือน (30 วัน)
    #     albino_data = [2, 1, 3, 0, 1, 2, 0, 3, 1, 2, 4, 1, 0, 2, 3, 
    #                   1, 2, 0, 1, 3, 2, 1, 0, 2, 1, 3, 0, 1, 2, 1]

    # สร้าง data points สำหรับ LineChart
    data_points = []
    for i, value in enumerate(albino_data):
        data_points.append(ft.LineChartDataPoint(x=i, y=value))

    # สร้าง LineChartData
    line_data = ft.LineChartData(
        data_points=data_points,
        stroke_width=3,
        color=ft.Colors.ORANGE,  # สีส้มสำหรับหนูเผือก
        curved=True,
        stroke_cap_round=True,
        point=True,  # แสดงจุดข้อมูล
    )

    # สร้าง LineChart with responsive sizing
    line_chart = ft.LineChart(
        data_series=[line_data],
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE)),
        horizontal_grid_lines=ft.ChartGridLines(
            color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE),
            width=1,
        ),
        vertical_grid_lines=ft.ChartGridLines(
            color=ft.Colors.with_opacity(0.2, ft.Colors.ON_SURFACE),
            width=1,
        ),
        left_axis=ft.ChartAxis(
            show_labels=True,
            labels_size=30,  # ลดขนาดป้ายแกนสำหรับ mobile
        ),
        bottom_axis=ft.ChartAxis(
            show_labels=True,
            labels_size=30,  # ลดขนาดป้ายแกนสำหรับ mobile
        ),
        tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
        min_y=0,
        max_y=max(albino_data) * 1.1 if albino_data else 10,  # เพิ่ม 10% เพื่อให้มีพื้นที่ด้านบน
        min_x=0,
        max_x=len(albino_data) - 1 if len(albino_data) > 1 else 1,
        bgcolor=ft.Colors.WHITE,
        expand=True,  # ให้ chart ขยายตาม container
        height=180,     # กำหนดความสูงคงที่
    )

    return ft.Container(
        content=ft.ResponsiveRow([
            ft.Container(
                content=ft.Column([
                    # LineChart - responsive
                    ft.Container(
                        content=line_chart,
                        height=180,
                        expand=True,
                    ),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                expand=True),
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                padding=15,
                shadow=ft.BoxShadow(
                    spread_radius=0.1, 
                    blur_radius=4, 
                    color=Grey, 
                    offset=ft.Offset(0, 2)
                ),
                col={"xs": 12, "sm": 12, "md": 12, "lg": 12},  # เต็มจอทุกขนาด
                expand=True,
            )
        ]),
        margin=ft.margin.symmetric(horizontal=10),
        expand=True,
    )
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
        ft.ResponsiveRow(
            [
                ft.Container(
                    content=base_button_with_icon(
                        "ผสมพันธุ์ใหม่", "FAVORITE", on_mating_click
                    ),
                    col={"xs": 12, "sm": 6, "md": 3, "lg": 3},
                ),
                ft.Container(
                    content=base_button_with_icon(
                        "เพิ่มหนูใหม่", "ADD_CIRCLE", on_add_click
                    ),
                    col={"xs": 12, "sm": 6, "md": 3, "lg": 3},
                ),
                ft.Container(
                    content=base_button_with_icon(
                        "บันทึกสุขภาพ", "LOCAL_HOSPITAL", on_health_click
                    ),
                    col={"xs": 12, "sm": 6, "md": 3, "lg": 3},
                ),
                ft.Container(
                    content=base_button_with_icon(
                        "รายงานและสถิติ", "LIBRARY_BOOKS", on_report_click
                    ),
                    col={"xs": 12, "sm": 6, "md": 3, "lg": 3},
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
        ft.ResponsiveRow(
            [
                ft.Container(
                    content=base_info_report_box(
                        topic="จำนวนหนูทั้งหมด",
                        content=get_amount_rat(),
                        units="ตัว",
                        color=Neo_Mint,
                    ),
                    col={"xs": 12, "sm": 6, "md": 6, "lg": 6},
                ),
                ft.Container(
                    content=base_info_report_box(
                        topic="จำนวนหนูที่ผสมพันธุ์",
                        content=get_breeding_rat(),
                        units="ตัว",
                        color=Deep_Purple,
                    ),
                    col={"xs": 12, "sm": 6, "md": 6, "lg": 6},
                ),
            ]
        ),
        base_empty_box(5),
        ft.ResponsiveRow(
            [
                ft.Container(
                    content=base_info_report_box(
                        topic="คู่ผสมพันธุ์ปัจจุบัน",
                        content=get_current_breeding_pair(),
                        units="คู่",
                        color=Neo_Mint,
                    ),
                    col={"xs": 12, "sm": 6, "md": 6, "lg": 6},
                ),
                ft.Container(
                    content=base_info_report_box(
                        topic="อัตราความสำเร็จ",
                        content=get_breeding_success_rate(),
                        units="%",
                        color=Deep_Purple,
                    ),
                    col={"xs": 12, "sm": 6, "md": 6, "lg": 6},
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
            # แทนที่ base_chart() ด้วยกราฟแนวโน้มหนูเผือกใหม่
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
