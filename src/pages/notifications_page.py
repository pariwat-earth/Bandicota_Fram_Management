import flet as ft
from components.base_box import base_empty_box, base_emergency_report_box
from main_calculate.notification import (
    get_expire_rat_notifications,
    handle_single_expire_rat,
    process_all_expire_rats,
    show_expire_rat,
)
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, Red, White

page_name = "การแจ้งเตือน"


def notifications_page(
    change_content_callback=None, content_functions=None, nav_indices=None, page=None
):
    """
    หน้าแสดงการแจ้งเตือนแบบ Responsive สำหรับคู่ผสมพันธุ์
    """

    def refresh_page():
        """รีเฟรชหน้าการแจ้งเตือน"""
        if change_content_callback and content_functions:
            nav_index = nav_indices.get("notifications") if nav_indices else None
            change_content_callback(content_functions["notifications"], nav_index)

    def show_snack_bar(message, type="info"):
        """แสดง SnackBar"""
        if not page:
            return

        color = (
            ft.Colors.GREEN
            if type == "success"
            else ft.Colors.RED if type == "error" else ft.Colors.BLUE
        )

        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=White), bgcolor=color, duration=3000
        )
        page.snack_bar.open = True
        page.update()

    def handle_single_pair_action(pair_data):
        """จัดการการดำเนินการกับคู่ผสมพันธุ์ตัวเดียว"""
        try:
            result = handle_single_expire_rat(pair_data)

            if result.get("success"):
                show_snack_bar(
                    f"ดำเนินการกับการผสมพันธุ์ {pair_data['breeding_id']} เรียบร้อยแล้ว",
                    "success",
                )
                ft.Timer(1.5, lambda: refresh_page())
            else:
                show_snack_bar(
                    f"เกิดข้อผิดพลาด: {result.get('message', 'ไม่ทราบสาเหตุ')}", "error"
                )

        except Exception as e:
            show_snack_bar(f"เกิดข้อผิดพลาด: {str(e)}", "error")

    def handle_all_pairs_action(e):
        """จัดการการดำเนินการกับคู่ผสมพันธุ์ทั้งหมด"""

        def confirm_action(confirm_e):
            page.dialog.open = False
            page.update()

            if confirm_e.control.text == "ยืนยัน":
                try:
                    result = process_all_expire_rats()

                    if result.get("success"):
                        show_snack_bar(
                            result.get("message", "ดำเนินการเรียบร้อย"), "success"
                        )
                        ft.Timer(1.5, lambda: refresh_page())
                    else:
                        show_snack_bar(
                            f"เกิดข้อผิดพลาด: {result.get('message', 'ไม่ทราบสาเหตุ')}",
                            "error",
                        )

                except Exception as e:
                    show_snack_bar(f"เกิดข้อผิดพลาด: {str(e)}", "error")

        page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("ยืนยันการดำเนินการ"),
            content=ft.Text(
                "คุณต้องการดำเนินการกับคู่ผสมพันธุ์ทั้งหมดแบบอัตโนมัติหรือไม่?\n\n• ประสิทธิภาพลดลง: แยกคู่\n• ไม่ยอมผสมพันธุ์: แยกคู่ + กำจัดตามเงื่อนไข\n• ผสมพันธุ์สำเร็จมาก: แยกคู่ + กำจัดตามเงื่อนไข"
            ),
            actions=[
                ft.TextButton("ยกเลิก", on_click=confirm_action),
                ft.TextButton("ยืนยัน", on_click=confirm_action),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True
        page.update()

    def get_color_object(color_name):
        """แปลง color name เป็น color object"""
        color_map = {
            "Red": Red,
            "Neo_Mint": Neo_Mint,
            "ft.Colors.ORANGE_700": ft.Colors.ORANGE_700,
            "Grey": Grey,
        }
        return color_map.get(color_name, Grey)

    def create_pair_card(notification):
        """สร้างการ์ดสำหรับแสดงข้อมูลคู่ผสมพันธุ์"""
        pair_data = notification["pair_data"]

        # สีตามประเภท
        if notification["type"] == "emergency":
            card_color = ft.Colors.RED_50
            border_color = Red
        elif notification["type"] == "warning":
            card_color = ft.Colors.ORANGE_50
            border_color = ft.Colors.ORANGE_700
        else:
            card_color = ft.Colors.GREEN_50
            border_color = Neo_Mint

        # ข้อมูลหนูพ่อและแม่
        father_info = f"พ่อพันธุ์:"
        mother_info = f"แม่พันธุ์:"

        if pair_data.get("father_ring_number"):
            father_info += f" - ห่วงขา: {pair_data['father_ring_number']}"
        else:
            father_info += " - ไม่มีห่วงขา"

        if pair_data.get("mother_ring_number"):
            mother_info += f" - ห่วงขา: {pair_data['mother_ring_number']}"
        else:
            mother_info += " - ไม่มีห่วงขา"

        # ปุ่มดำเนินการ
        action_button = ft.ElevatedButton(
            # notification["action_text"],
            " ",
            icon=ft.Icons.AUTO_MODE,
            on_click=lambda _: handle_single_pair_action(pair_data),
            style=ft.ButtonStyle(
                bgcolor=border_color,
                color=White,
            ),
        )

        return ft.Container(
            content=ft.Column(
                [
                    # Header การผสมพันธุ์
                    ft.Row(
                        [
                            ft.Text(
                                f"การผสมพันธุ์ ID: {pair_data['breeding_id']}",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=border_color,
                            ),
                            action_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    # ข้อมูลหนูพ่อและแม่
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(father_info, size=12, color=Black),
                                    ft.Text(mother_info, size=12, color=Black),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Text(
                                f"สาเหตุ: {pair_data['reason']}",
                                size=12,
                                color=ft.Colors.GREY_700,
                                italic=True,
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                spacing=10,
            ),
            padding=15,
            margin=ft.margin.symmetric(horizontal=10, vertical=5),
            bgcolor=card_color,
            border=ft.border.all(1, border_color),
            border_radius=10,
            expand=True,
        )

    # ดึงข้อมูลการแจ้งเตือน
    notifications = []
    summary = {}
    try:
        notifications = get_expire_rat_notifications()
        expire_result = show_expire_rat()
        if expire_result.get("success"):
            summary = {
                "declining_count": expire_result.get("declining_count", 0),
                "unsuccessful_count": expire_result.get("unsuccessful_count", 0),
                "successful_count": expire_result.get("successful_count", 0),
                "total_count": expire_result.get("total_count", 0),
            }
    except Exception as e:
        print(f"Error loading notifications: {e}")
        notifications = []
        summary = {}

    # จัดกลุ่มการแจ้งเตือนตามประเภท
    emergency_notifications = [
        n for n in notifications if n["type"] == "emergency"
    ]  # ไม่ยอมผสมพันธุ์
    warning_notifications = [
        n for n in notifications if n["type"] == "warning"
    ]  # ประสิทธิภาพลดลง
    normal_notifications = [
        n for n in notifications if n["type"] == "normal"
    ]  # ผสมพันธุ์สำเร็จมาก

    # สร้าง UI แบบ Responsive
    def build_responsive_layout():
        controls = []

        # Header
        controls.extend(
            [
                base_empty_box(10),
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    "การแจ้งเตือนการจัดการคู่ผสมพันธุ์",
                                    size=20,
                                    color=Black,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                            col={"sm": 12},
                        )
                    ]
                ),
                base_empty_box(15),
            ]
        )

        # สรุปจำนวน - Responsive Cards
        if summary.get("total_count", 0) > 0:
            controls.append(
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Icon(ft.Icons.CLOSE, color=Red, size=28),
                                            ft.Text(
                                                f"{summary.get('unsuccessful_count', 0)}",
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=Red,
                                            ),
                                            ft.Text(
                                                "ไม่ยอมผสมพันธุ์",
                                                size=11,
                                                color=Grey,
                                                text_align=ft.TextAlign.CENTER,
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5,
                                    ),
                                    padding=12,
                                )
                            ),
                            col={"xs": 12, "sm": 6, "md": 4},
                        ),
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Icon(
                                                ft.Icons.TRENDING_DOWN,
                                                color=ft.Colors.ORANGE_700,
                                                size=28,
                                            ),
                                            ft.Text(
                                                f"{summary.get('declining_count', 0)}",
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.ORANGE_700,
                                            ),
                                            ft.Text(
                                                "ประสิทธิภาพลดลง",
                                                size=11,
                                                color=Grey,
                                                text_align=ft.TextAlign.CENTER,
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5,
                                    ),
                                    padding=12,
                                )
                            ),
                            col={"xs": 12, "sm": 6, "md": 4},
                        ),
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Icon(
                                                ft.Icons.STAR, color=Neo_Mint, size=28
                                            ),
                                            ft.Text(
                                                f"{summary.get('successful_count', 0)}",
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=Neo_Mint,
                                            ),
                                            ft.Text(
                                                "ผสมพันธุ์สำเร็จมาก",
                                                size=11,
                                                color=Grey,
                                                text_align=ft.TextAlign.CENTER,
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5,
                                    ),
                                    padding=12,
                                )
                            ),
                            col={"xs": 12, "sm": 12, "md": 4},
                        ),
                    ]
                )
            )
            controls.append(base_empty_box(20))

        # ปุ่มควบคุม - Responsive
        button_row = []
        if summary.get("total_count", 0) > 0:
            button_row.append(
                ft.Container(
                    content=ft.ElevatedButton(
                        "ดำเนินการทั้งหมดอัตโนมัติ",
                        icon=ft.Icons.AUTO_MODE,
                        on_click=handle_all_pairs_action,
                        style=ft.ButtonStyle(
                            bgcolor=Deep_Purple,
                            color=White,
                        ),
                    ),
                    expand=True,
                )
            )

        controls.append(ft.ResponsiveRow(button_row))
        controls.append(base_empty_box(15))

        # แสดงการแจ้งเตือน
        if summary.get("total_count", 0) == 0:
            controls.append(
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(
                                        ft.Icons.NOTIFICATIONS_OFF, size=50, color=Grey
                                    ),
                                    ft.Text("ไม่มีการแจ้งเตือน", size=16, color=Grey),
                                    ft.Text(
                                        "ระบบจะแจ้งเตือนเมื่อมีคู่ผสมพันธุ์ที่ต้องดำเนินการ",
                                        size=12,
                                        color=Grey,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            height=200,
                            col={"sm": 12},
                        )
                    ]
                )
            )
        else:
            controls.append(base_empty_box(20))

            # 1. การแจ้งเตือนด่วน (ไม่ยอมผสมพันธุ์)
            if emergency_notifications:
                controls.append(
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=ft.Text(
                                    f"ด่วน - ไม่ยอมผสมพันธุ์ ({len(emergency_notifications)} คู่)",
                                    size=16,
                                    color=Red,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                col={"sm": 12},
                            )
                        ]
                    )
                )

                for notification in emergency_notifications:
                    controls.append(
                        ft.ResponsiveRow(
                            [
                                ft.Container(
                                    content=create_pair_card(notification),
                                    expand=True,
                                )
                            ]
                        )
                    )

                controls.append(base_empty_box(15))

            # 2. การแจ้งเตือนระวัง (ประสิทธิภาพลดลง)
            if warning_notifications:
                controls.append(
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=ft.Text(
                                    f"ระวัง - ประสิทธิภาพลดลง ({len(warning_notifications)} คู่)",
                                    size=16,
                                    color=ft.Colors.ORANGE_700,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                col={"sm": 12},
                            )
                        ]
                    )
                )

                for notification in warning_notifications:
                    controls.append(
                        ft.Row(
                            [
                                ft.Container(
                                    content=create_pair_card(notification),
                                    expand=True,
                                )
                            ]
                        )
                    )

                controls.append(base_empty_box(15))

            # 3. การแจ้งเตือนปกติ (ผสมพันธุ์สำเร็จมาก)
            if normal_notifications:
                controls.append(
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=ft.Text(
                                    f"ปกติ - ผสมพันธุ์สำเร็จมาก ({len(normal_notifications)} คู่)",
                                    size=16,
                                    color=Neo_Mint,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                col={"sm": 12},
                            )
                        ]
                    )
                )

                for notification in normal_notifications:
                    controls.append(
                        ft.Row(
                            [
                                ft.Container(
                                    content=create_pair_card(notification),
                                    expand=True,
                                )
                            ]
                        )
                    )

        controls.append(base_empty_box(50))  # Bottom padding
        return controls

    return ft.ListView(
        controls=build_responsive_layout(),
        expand=True,
        spacing=0,
        padding=ft.padding.all(10),
        auto_scroll=False,
    )
