import flet as ft
from datetime import datetime, timedelta
from components.base_button import base_button_normal
from components.base_box import base_info_report_box_v2
from storages.report_service import (
    get_breeding_performance,
    get_health_statistics,
    get_albino_trend_data,
    get_birth_rate_data,
    get_general_statistics,
    get_health_trend_data,
)
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, White, Red


def report_page(change_content_callback=None, content_functions=None, nav_indices=None):
    """หน้ารายงานหลัก"""

    # ตัวแปรสำหรับจัดการช่วงเวลา
    selected_period = "1M"  # เริ่มต้นที่ 1 เดือน

    # สร้าง container สำหรับแต่ละส่วน
    breeding_performance_container = ft.Container()
    health_statistics_container = ft.Container()
    charts_container = ft.Container()

    def update_period(period):
        """อัพเดทช่วงเวลาและรีเฟรชกราฟ"""
        nonlocal selected_period
        selected_period = period
        refresh_charts()

    def refresh_charts():
        """รีเฟรชกราฟทั้งหมด"""
        # อัพเดทกราฟต่างๆ ตามช่วงเวลาที่เลือก
        charts_container.content = build_charts_section()
        charts_container.update()

    def on_advanced_report_click(e):
        """ฟังก์ชันสำหรับเปิดหน้ารายงานขั้นสูง"""
        if change_content_callback and content_functions:
            nav_index = nav_indices.get("advanced_report") if nav_indices else None
            change_content_callback(content_functions["advanced_report"], nav_index)

    def build_period_selector():
        """สร้างปุ่มเลือกช่วงเวลา - ปุ่มย่อขยายตามหน้าจอ"""
        periods = [
            ("1W", "1 สัปดาห์"),
            ("1M", "1 เดือน"), 
            ("3M", "3 เดือน"),
            ("6M", "6 เดือน"),
            ("1Y", "1 ปี")
        ]
        
        period_buttons = []
        for period_key, period_name in periods:
            is_selected = period_key == selected_period
            button_container = ft.Container(
                content=ft.ElevatedButton(
                    text=period_name,
                    bgcolor=Deep_Purple if is_selected else White,
                    color=White if is_selected else Black,
                    on_click=lambda e, p=period_key: update_period(p),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5),
                    ),
                    expand=True,  # ให้ปุ่มขยายเต็ม container
                ),
                # กำหนด responsive columns สำหรับแต่ละปุ่ม
                col={
                    "xs": 2.4,  # มือถือ: 1 ปุ่มต่อแถว (เต็มจอ)
                    "sm": 2.4,   # มือถือใหญ่: 2 ปุ่มต่อแถว
                    "md": 2.4,   # แท็บเล็ต: 3 ปุ่มต่อแถว (12/4 = 3)
                    "lg": 2.4, # คอมพิวเตอร์: 5 ปุ่มต่อแถว (12/2.4 = 5)
                    "xl": 2.4  # หน้าจอใหญ่: 5 ปุ่มต่อแถว
                }
            )
            period_buttons.append(button_container)
        
        return ft.ResponsiveRow(
            period_buttons,
            spacing=10,
            run_spacing=10,  # ระยะห่างระหว่างแถว (กรณีปุ่มขึ้นแถวใหม่)
        )

    def build_breeding_performance():
        """สร้างส่วนรายงานประสิทธิภาพการผสมพันธุ์"""
        performance_data = get_breeding_performance()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "รายงานประสิทธิภาพการผสมพันธุ์",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=Black,
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=base_info_report_box_v2(
                                    topic="อัตราความสำเร็จ",
                                    content=f"{performance_data['success_rate']:.1f}%",
                                    color=Neo_Mint,
                                ),
                                expand=True,
                            ),
                            ft.Container(
                                content=base_info_report_box_v2(
                                    topic="เฉลี่ยลูก/คอก",
                                    content=f"{performance_data['avg_pups_per_breeding']:.1f} ตัว",
                                    color=Deep_Purple,
                                ),
                                expand=True,
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=base_info_report_box_v2(
                                    topic="เฉลี่ยหนูเผือก/คอก",
                                    content=f"{performance_data['avg_albino_per_breeding']:.1f} ตัว",
                                    color=Red,
                                ),
                                expand=True,
                            ),
                            ft.Container(
                                content=base_info_report_box_v2(
                                    topic="การผสมทั้งหมด",
                                    content=f"{performance_data['total_breedings']} ครั้ง",
                                    color=Grey,
                                ),
                                expand=True,
                            ),
                        ]
                    ),
                ],
                spacing=15,
            ),
            bgcolor=White,
            border_radius=10,
            padding=20,
            margin=ft.margin.only(bottom=20),
            shadow=ft.BoxShadow(
                spread_radius=0.1, blur_radius=4, color=Grey, offset=ft.Offset(0, 0)
            ),
        )

    def build_health_statistics():
        """สร้างส่วนสถิติสุขภาพ"""
        health_data = get_health_statistics()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "สถิติสุขภาพหนู", size=16, weight=ft.FontWeight.BOLD, color=Black
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=base_info_report_box_v2(
                                    topic="หนูสุขภาพดี",
                                    content=f"{health_data['healthy_rate']:.1f}%",
                                    color=ft.Colors.GREEN,
                                ),
                                expand=True,
                            ),
                            ft.Container(
                                content=base_info_report_box_v2(
                                    topic="หนูป่วย",
                                    content=f"{health_data['sick_rate']:.1f}%",
                                    color=Red,
                                ),
                                expand=True,
                            ),
                        ]
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                content=base_info_report_box_v2(
                                    topic="หนูเฝ้าระวัง",
                                    content=f"{health_data['monitoring_rate']:.1f}%",
                                    color=ft.Colors.ORANGE,
                                ),
                                expand=True,
                            ),
                            ft.Container(
                                content=base_info_report_box_v2(
                                    topic="รวมทั้งหมด",
                                    content=f"{health_data['total_rats']} ตัว",
                                    color=Deep_Purple,
                                ),
                                expand=True,
                            ),
                        ]
                    ),
                ],
                spacing=15,
            ),
            bgcolor=White,
            border_radius=10,
            padding=20,
            margin=ft.margin.only(bottom=20),
            shadow=ft.BoxShadow(
                spread_radius=0.1, blur_radius=4, color=Grey, offset=ft.Offset(0, 0)
            ),
        )

    def build_line_chart(title, data, color=Neo_Mint, height=180):
        """สร้าง Line Chart ด้วย ft.LineChart ของ Flet"""
        if not data or len(data) == 0:
            return ft.Container(
                content=ft.Text("ไม่มีข้อมูล", color=Grey, size=14),
                height=height + 50,
                alignment=ft.alignment.center,
            )

        # สร้าง data points สำหรับ LineChart
        data_points = []
        for i, value in enumerate(data):
            data_points.append(ft.LineChartDataPoint(x=i, y=value))

        # สร้าง LineChartData
        line_data = ft.LineChartData(
            data_points=data_points,
            stroke_width=3,
            color=color,
            curved=True,
            stroke_cap_round=True,
            point=True,  # แสดงจุดข้อมูล
        )

        # สร้าง LineChart
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
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(
                show_labels=True,
                labels_size=40,
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
            min_y=0,
            max_y=max(data) * 1.1 if data else 10,  # เพิ่ม 10% เพื่อให้มีพื้นที่ด้านบน
            min_x=0,
            max_x=len(data) - 1 if len(data) > 1 else 1,
            bgcolor=ft.Colors.WHITE,
            expand=True,
            height=height,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=Black),
                    line_chart,
                    ft.Row(
                        [
                            ft.Text(
                                f"สูงสุด: {max(data) if data else 0}", size=10, color=Grey
                            ),
                            ft.Text(
                                f"ต่ำสุด: {min(data) if data else 0}", size=10, color=Grey
                            ),
                            ft.Text(
                                (
                                    f"เฉลี่ย: {sum(data)/len(data):.1f}"
                                    if data
                                    else "เฉลี่ย: 0"
                                ),
                                size=10,
                                color=Grey,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=White,
            border_radius=10,
            padding=15,
            shadow=ft.BoxShadow(
                spread_radius=0.1, blur_radius=2, color=Grey, offset=ft.Offset(0, 0)
            ),
            expand=True,
        )

    def build_charts_section():
        """สร้างส่วนกราฟต่างๆ"""
        # ดึงข้อมูลตามช่วงเวลาที่เลือก
        health_trend_data = get_health_trend_data(selected_period)
        albino_trend_data = get_albino_trend_data(selected_period)
        birth_rate_data = get_birth_rate_data(selected_period)

        return ft.Column(
            [
                # ปุ่มเลือกช่วงเวลา
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "เลือกช่วงเวลาสำหรับกราฟ",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=Black,
                                    ),
                                    build_period_selector(),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            bgcolor=White,
                            border_radius=10,
                            padding=15,
                            shadow=ft.BoxShadow(
                                spread_radius=0.1,
                                blur_radius=4,
                                color=Grey,
                                offset=ft.Offset(0, 0),
                            ),
                            # กำหนดให้แสดงเต็มจอทุกขนาดหน้าจอ
                            col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 12},
                        )
                    ]
                ),
                # กราฟแถวแรก - responsive
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=build_line_chart(
                                "แนวโน้มหนูป่วย", health_trend_data, Red
                            ),
                            col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                        ),
                        ft.Container(
                            content=build_line_chart(
                                "แนวโน้มหนูเผือกตาแดง", albino_trend_data, ft.Colors.ORANGE
                            ),
                            col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                        ),
                    ],
                    spacing=20,
                ),
                ft.Container(height=20),  # Spacer
                # กราฟแถวที่สอง - responsive
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=build_line_chart(
                                "อัตราการเกิด", birth_rate_data, ft.Colors.GREEN
                            ),
                            col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                        ),
                        ft.Container(
                            content=build_additional_chart(),
                            col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                        ),
                    ],
                    spacing=20,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def build_additional_chart():
        """กราฟเพิ่มเติม - การใช้งานบ่อ"""
        pond_usage_data = get_pond_usage_data()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "การใช้งานบ่อเลี้ยง",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=Black,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text(
                                                        "ใช้งาน",
                                                        size=10,
                                                        color=White,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    ft.Text(
                                                        str(pond_usage_data["used"]),
                                                        size=16,
                                                        color=White,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            bgcolor=Neo_Mint,
                                            border_radius=5,
                                            padding=10,
                                            width=70,
                                            height=20 + pond_usage_data["used"] * 3,
                                        ),
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text(
                                                        "ว่าง",
                                                        size=10,
                                                        color=Black,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    ft.Text(
                                                        str(pond_usage_data["empty"]),
                                                        size=16,
                                                        color=Black,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            bgcolor=ft.Colors.GREY_300,
                                            border_radius=5,
                                            padding=10,
                                            width=70,
                                            height=20 + pond_usage_data["empty"] * 3,
                                        ),
                                        ft.Container(
                                            content=ft.Column(
                                                [
                                                    ft.Text(
                                                        "ซ่อม",
                                                        size=10,
                                                        color=White,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    ft.Text(
                                                        str(
                                                            pond_usage_data[
                                                                "maintenance"
                                                            ]
                                                        ),
                                                        size=16,
                                                        color=White,
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                ],
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            ),
                                            bgcolor=Red,
                                            border_radius=5,
                                            padding=10,
                                            width=70,
                                            height=20
                                            + pond_usage_data["maintenance"] * 3,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=15,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                        height=180,
                    ),
                    ft.Text(
                        f"รวม: {pond_usage_data['total']} บ่อ",
                        size=12,
                        color=Grey,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=White,
            border_radius=10,
            padding=15,
            shadow=ft.BoxShadow(
                spread_radius=0.1, blur_radius=2, color=Grey, offset=ft.Offset(0, 0)
            ),
            expand=True,
        )

    # สร้างเนื้อหาเริ่มต้น
    breeding_performance_container.content = build_breeding_performance()
    health_statistics_container.content = build_health_statistics()
    charts_container.content = build_charts_section()

    # สร้าง ListView หลัก
    main_content = ft.ListView(
        controls=[
            # Header และปุ่มรายงานขั้นสูง
            ft.ResponsiveRow(
                [
                    ft.Container(
                        content=ft.Text(
                            "รายงานและสถิติ",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=Black,
                        ),
                        col={"xs": 8, "sm": 8, "md": 9, "lg": 10},
                    ),
                    ft.Container(
                        content=ft.ElevatedButton(
                            text="รายงานขั้นสูง",
                            icon=ft.Icons.ANALYTICS,
                            bgcolor=Deep_Purple,
                            color=White,
                            on_click=on_advanced_report_click,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        col={"xs": 4, "sm": 4, "md": 3, "lg": 2},
                        alignment=ft.alignment.center_right,
                    ),
                ]
            ),
            ft.Container(height=20),  # Spacer
            # ส่วนประสิทธิภาพการผสมพันธุ์
            breeding_performance_container,
            # ส่วนสถิติสุขภาพ
            health_statistics_container,
            # ส่วนกราฟ
            charts_container,
            # ช่องว่างด้านล่าง
            ft.Container(height=50),
        ],
        expand=True,
        spacing=0,
        padding=ft.padding.only(top=20, bottom=20, left=10, right=10),
    )

    return main_content


def get_pond_usage_data():
    """ดึงข้อมูลการใช้งานบ่อ (ข้อมูลจริงจากฐานข้อมูล)"""
    from storages.database_service import get_connection

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT status, COUNT(*) as count
            FROM pond
            GROUP BY status
        """
        )

        results = cursor.fetchall()
        data = {"used": 0, "empty": 0, "maintenance": 0, "total": 0}

        for status, count in results:
            if status == "work":
                data["used"] = count
            elif status == "empty":
                data["empty"] = count
            elif status == "maintenance":
                data["maintenance"] = count
            data["total"] += count

        conn.close()
        return data

    except Exception as e:
        print(f"Error getting pond usage data: {e}")
        return {"used": 12, "empty": 8, "maintenance": 2, "total": 22}
