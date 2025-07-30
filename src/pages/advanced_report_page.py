import flet as ft
from datetime import datetime, timedelta
from components.base_button import base_button_normal, base_button_gradient
from components.base_box import base_info_report_box_v2
from storages.report_service import (
    get_monthly_breeding_summary,
    get_productivity_metrics,
    get_health_trend_data,
)
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, White, Red


def advanced_report_page():
    """หน้ารายงานขั้นสูง - รายละเอียดและวิเคราะห์เชิงลึก (Responsive with ListView)"""

    # ใช้ list เพื่อให้สามารถแก้ไขค่าได้ใน nested function
    current_tab = [0]  # 0: รายงานรายเดือน, 1: ประสิทธิภาพฟาร์ม, 2: วิเคราะห์แนวโน้ม

    # Container สำหรับเก็บ tab bar และ content
    tab_bar_container = ft.Container()
    content_container = ft.Container()

    def build_tab_bar():
        """สร้างแท็บบาร์ - Responsive ปุ่มขยายเต็มจอ"""
        tabs = [("รายงานรายเดือน", 0), ("ประสิทธิภาพ", 1), ("วิเคราะห์แนวโน้ม", 2)]

        tab_buttons = []
        for tab_name, tab_index in tabs:
            is_selected = tab_index == current_tab[0]

            # สร้างปุ่ม tab แต่ละอัน
            button = ft.Container(
                content=ft.Text(
                    tab_name,
                    size=12,
                    weight=(
                        ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL
                    ),
                    color=White if is_selected else Black,
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=Deep_Purple if is_selected else White,
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                border=ft.border.all(1, Deep_Purple) if not is_selected else None,
                ink=True,
                on_click=lambda e, idx=tab_index: switch_tab(idx),
                expand=True,  # ให้ปุ่มขยายเท่าๆ กัน
                alignment=ft.alignment.center,
            )
            tab_buttons.append(button)

        # ใช้ Row แทน ResponsiveRow เพื่อให้ปุ่มขยายเต็มจอ
        return ft.Row(
            tab_buttons,
            spacing=10,
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            expand=True,  # ให้ Row ขยายเต็มจอ
        )

    def switch_tab(tab_index):
        """เปลี่ยนแท็บ"""
        current_tab[0] = tab_index
        refresh_content()

    def build_monthly_report():
        """สร้างรายงานรายเดือน - Responsive"""
        monthly_data = get_monthly_breeding_summary(12)

        if not monthly_data:
            return ft.Container(
                content=ft.Text("ไม่มีข้อมูลรายงานรายเดือน", color=Grey, size=14),
                height=300,
                alignment=ft.alignment.center,
            )

        # สร้างตารางข้อมูล - responsive
        data_rows = []
        for data in monthly_data[-6:]:  # แสดง 6 เดือนล่าสุด
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(data["month"], size=11)),
                    ft.DataCell(ft.Text(str(data["total_breedings"]), size=11)),
                    ft.DataCell(ft.Text(str(data["successful_breedings"]), size=11)),
                    ft.DataCell(ft.Text(f"{data['success_rate']:.1f}%", size=11)),
                    ft.DataCell(ft.Text(str(data["total_pups"]), size=11)),
                    ft.DataCell(ft.Text(str(data["albino_pups"]), size=11)),
                ]
            )
            data_rows.append(row)

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("เดือน", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("ผสมทั้งหมด", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("สำเร็จ", weight=ft.FontWeight.BOLD, size=11)),
                ft.DataColumn(ft.Text("อัตราสำเร็จ", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("ลูกทั้งหมด", weight=ft.FontWeight.BOLD, size=10)),
                ft.DataColumn(ft.Text("หนูเผือก", weight=ft.FontWeight.BOLD, size=10)),
            ],
            rows=data_rows,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            heading_row_color=ft.Colors.GREY_100,
            column_spacing=30,  # ลดระยะห่างระหว่างคอลัมน์
        )

        # สรุปข้อมูลรวม
        total_breedings = sum(d["total_breedings"] for d in monthly_data)
        total_successful = sum(d["successful_breedings"] for d in monthly_data)
        total_pups = sum(d["total_pups"] for d in monthly_data)
        total_albino = sum(d["albino_pups"] for d in monthly_data)
        overall_success_rate = (
            (total_successful / total_breedings * 100) if total_breedings > 0 else 0
        )

        summary_cards = ft.ResponsiveRow(
            [
                ft.Container(
                    content=base_info_report_box_v2(
                        topic="รวมการผสม",
                        content=f"{total_breedings} ครั้ง",
                        color=Deep_Purple,
                    ),
                    col={"xs": 12, "sm": 6, "md": 3, "lg": 3},
                ),
                ft.Container(
                    content=base_info_report_box_v2(
                        topic="อัตราสำเร็จรวม",
                        content=f"{overall_success_rate:.1f}%",
                        color=Neo_Mint,
                    ),
                    col={"xs": 12, "sm": 6, "md": 3, "lg": 3},
                ),
                ft.Container(
                    content=base_info_report_box_v2(
                        topic="ลูกรวมทั้งหมด",
                        content=f"{total_pups} ตัว",
                        color=ft.Colors.GREEN,
                    ),
                    col={"xs": 12, "sm": 6, "md": 3, "lg": 3},
                ),
                ft.Container(
                    content=base_info_report_box_v2(
                        topic="หนูเผือกรวม", content=f"{total_albino} ตัว", color=Red
                    ),
                    col={"xs": 12, "sm": 6, "md": 3, "lg": 3},
                ),
            ],
            spacing=10,
        )

        return ft.Column(
            [
                ft.Text("รายงานการผสมพันธุ์รายเดือน", size=16, weight=ft.FontWeight.BOLD),
                summary_cards,
                ft.Container(height=20),
                ft.Container(
                    content=ft.ListView(
                        controls=[table],
                    ),
                    border_radius=10,
                    bgcolor=White,
                    padding=15,
                    shadow=ft.BoxShadow(
                        spread_radius=0.1,
                        blur_radius=4,
                        color=Grey,
                        offset=ft.Offset(0, 0),
                    ),
                ),
            ],
            spacing=15,
        )

    def build_productivity_report():
        """สร้างรายงานประสิทธิภาพฟาร์ม - Responsive"""
        metrics = get_productivity_metrics()

        # การ์ดแสดงประสิทธิภาพ
        efficiency_cards = ft.Column(
            [
                ft.Text("ประสิทธิภาพการใช้ทรัพยากร", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Container(
                            content=base_info_report_box_v2(
                                topic="การใช้ห่วงขา",
                                content=f"{metrics['ring_usage_rate']:.1f}%",
                                color=Neo_Mint,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=base_info_report_box_v2(
                                topic="การใช้บ่อเลี้ยง",
                                content=f"{metrics['pond_usage_rate']:.1f}%",
                                color=Deep_Purple,
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Row(
                    [
                        ft.Container(
                            content=base_info_report_box_v2(
                                topic="ห่วงขาที่ใช้",
                                content=f"{metrics['used_rings']}/{metrics['total_rings']} อัน",
                                color=ft.Colors.BLUE,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=base_info_report_box_v2(
                                topic="บ่อที่ใช้",
                                content=f"{metrics['used_ponds']}/{metrics['total_ponds']} บ่อ",
                                color=ft.Colors.GREEN,
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            spacing=15,
        )

        # อัตราส่วนเพศ
        gender_section = ft.Column(
            [
                ft.Text("อัตราส่วนเพศหนู", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "ตัวผู้",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE,
                                        ),
                                        ft.Text(
                                            f"{metrics['male_ratio']:.1f}%",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                bgcolor=ft.Colors.BLUE_50,
                                border_radius=10,
                                padding=20,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(
                                            "ตัวเมีย",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.PINK,
                                        ),
                                        ft.Text(
                                            f"{metrics['female_ratio']:.1f}%",
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                bgcolor=ft.Colors.PINK_50,
                                border_radius=10,
                                padding=20,
                            ),
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            spacing=15,
        )

        # แนะนำสำหรับการปรับปรุง
        recommendations = build_recommendations(metrics)

        return ft.Column(
            [
                efficiency_cards,
                ft.Container(height=20),
                gender_section,
                ft.Container(height=20),
                recommendations,
            ]
        )

    def build_recommendations(metrics):
        """สร้างส่วนคำแนะนำ"""
        recommendations = []

        if metrics["ring_usage_rate"] < 70:
            recommendations.append("• พิจารณาเพิ่มจำนวนหนูเพื่อใช้ห่วงขาให้เต็มประสิทธิภาพ")

        if metrics["pond_usage_rate"] < 80:
            recommendations.append("• มีบ่อเลี้ยงว่างมาก ควรเพิ่มการผสมพันธุ์")

        if abs(metrics["male_ratio"] - 50) > 10:
            recommendations.append("• อัตราส่วนเพศไม่สมดุล ควรปรับปรุงการคัดเลือกพ่อแม่พันธุ์")

        if not recommendations:
            recommendations.append("• ประสิทธิภาพฟาร์มอยู่ในเกณฑ์ดี")

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "คำแนะนำการปรับปรุง",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=Deep_Purple,
                    ),
                    ft.Column(
                        [ft.Text(rec, size=12, color=Black) for rec in recommendations]
                    ),
                ],
                spacing=10,
            ),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=15,
            border=ft.border.all(1, Deep_Purple),
        )

    def build_trend_analysis():
        """สร้างการวิเคราะห์แนวโน้ม - Responsive"""

        # เปรียบเทียบข้อมูล 3 เดือนล่าสุดกับ 3 เดือนก่อนหน้า
        current_period_data = get_health_trend_data("3M")

        if not current_period_data:
            return ft.Container(
                content=ft.Text("ไม่มีข้อมูลสำหรับวิเคราะห์แนวโน้ม", color=Grey, size=14),
                height=300,
                alignment=ft.alignment.center,
            )

        # คำนวณแนวโน้ม
        if len(current_period_data) >= 8:
            recent_avg = sum(current_period_data[-4:]) / 4  # 4 สัปดาห์ล่าสุด
            previous_avg = sum(current_period_data[:4]) / 4  # 4 สัปดาห์แรก
        else:
            recent_avg = (
                sum(current_period_data) / len(current_period_data)
                if current_period_data
                else 0
            )
            previous_avg = recent_avg

        trend_direction = (
            "เพิ่มขึ้น"
            if recent_avg > previous_avg
            else "ลดลง" if recent_avg < previous_avg else "คงที่"
        )
        trend_color = (
            Red
            if recent_avg > previous_avg
            else ft.Colors.GREEN if recent_avg < previous_avg else Grey
        )

        change_percent = (
            ((recent_avg - previous_avg) / previous_avg * 100)
            if previous_avg > 0
            else 0
        )

        # กราฟแนวโน้ม
        trend_chart = build_line_trend_chart(
            "แนวโน้มการป่วย 3 เดือนล่าสุด", current_period_data, Red
        )

        # สรุปการวิเคราะห์
        analysis_summary = ft.Container(
            content=ft.Column(
                [
                    ft.Text("สรุปการวิเคราะห์แนวโน้ม", size=16, weight=ft.FontWeight.BOLD),
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text("ทิศทางแนวโน้ม", size=12, color=Grey),
                                            ft.Text(
                                                trend_direction,
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=trend_color,
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    bgcolor=White,
                                    border_radius=8,
                                    padding=15,
                                ),
                                col={"xs": 12, "sm": 6, "md": 6, "lg": 6},
                            ),
                            ft.Container(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "อัตราการเปลี่ยนแปลง", size=12, color=Grey
                                            ),
                                            ft.Text(
                                                f"{abs(change_percent):.1f}%",
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=trend_color,
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    bgcolor=White,
                                    border_radius=8,
                                    padding=15,
                                ),
                                col={"xs": 12, "sm": 6, "md": 6, "lg": 6},
                            ),
                        ],
                        spacing=10,
                    ),
                    # คำแนะนำตามแนวโน้ม
                    ft.Container(
                        content=get_trend_recommendations(
                            trend_direction, change_percent
                        ),
                        margin=ft.margin.only(top=15),
                    ),
                ],
                spacing=15,
            ),
            bgcolor=ft.Colors.GREY_50,
            border_radius=10,
            padding=20,
        )

        return ft.Column(
            [
                analysis_summary,
                ft.Container(height=20),
                trend_chart,
            ]
        )

    def build_line_trend_chart(title, data, color):
        """สร้าง Line Chart สำหรับแนวโน้ม - Responsive ใช้ ft.LineChart"""
        if not data or len(data) == 0:
            return ft.Container(
                content=ft.Text("ไม่มีข้อมูล", color=Grey, size=14),
                height=200,
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

        # สร้าง LineChart - Responsive
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
                labels_size=30,  # ลดขนาดสำหรับ mobile
            ),
            bottom_axis=ft.ChartAxis(
                show_labels=True,
                labels_size=30,  # ลดขนาดสำหรับ mobile
            ),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
            min_y=0,
            max_y=max(data) * 1.1 if data else 10,  # เพิ่ม 10% เพื่อให้มีพื้นที่ด้านบน
            min_x=0,
            max_x=len(data) - 1 if len(data) > 1 else 1,
            bgcolor=ft.Colors.WHITE,
            expand=True,  # ให้ chart ขยายตาม container
            height=200,  # กำหนดความสูงสำหรับ mobile
        )

        return ft.ResponsiveRow(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                title, size=14, weight=ft.FontWeight.BOLD, color=Black
                            ),
                            ft.Container(
                                content=line_chart,
                                height=200,
                            ),
                            ft.Text(
                                "หน่วย: สัปดาห์",
                                size=10,
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
                        spread_radius=0.1,
                        blur_radius=2,
                        color=Grey,
                        offset=ft.Offset(0, 0),
                    ),
                    col={"xs": 12, "sm": 12, "md": 12, "lg": 12},  # เต็มจอทุกขนาด
                )
            ]
        )

    def get_trend_recommendations(direction, change_percent):
        """สร้างคำแนะนำตามแนวโน้ม"""
        if direction == "เพิ่มขึ้น" and change_percent > 20:
            return ft.Column(
                [
                    ft.Text(
                        "⚠️ คำเตือน: แนวโน้มการป่วยเพิ่มขึ้นอย่างมีนัยสำคัญ",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=Red,
                    ),
                    ft.Text("• ตรวจสอบสภาพแวดล้อมและการจัดการฟาร์ม", size=11, color=Black),
                    ft.Text("• พิจารณาเพิ่มมาตรการป้องกันโรค", size=11, color=Black),
                    ft.Text("• ปรึกษาสัตวแพทย์เพื่อวางแผนการรักษา", size=11, color=Black),
                ]
            )
        elif direction == "ลดลง":
            return ft.Column(
                [
                    ft.Text(
                        "✅ ข่าวดี: แนวโน้มการป่วยลดลง",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREEN,
                    ),
                    ft.Text("• รักษามาตรการดูแลที่ดีต่อไป", size=11, color=Black),
                    ft.Text("• ติดตามผลอย่างต่อเนื่อง", size=11, color=Black),
                ]
            )
        else:
            return ft.Column(
                [
                    ft.Text(
                        "ℹ️ แนวโน้มอยู่ในเกณฑ์ปกติ",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=Deep_Purple,
                    ),
                    ft.Text("• ดำเนินการตามแผนปกติ", size=11, color=Black),
                    ft.Text("• ติดตามสถานการณ์อย่างสม่ำเสมอ", size=11, color=Black),
                ]
            )

    def refresh_content():
        """รีเฟรชเนื้อหาตามแท็บที่เลือก"""
        # อัพเดท tab bar ก่อน
        tab_bar_container.content = build_tab_bar()

        # จากนั้นอัพเดท content
        if current_tab[0] == 0:
            content_container.content = build_monthly_report()
        elif current_tab[0] == 1:
            content_container.content = build_productivity_report()
        elif current_tab[0] == 2:
            content_container.content = build_trend_analysis()

        # อัพเดท UI
        if hasattr(tab_bar_container, "page") and tab_bar_container.page is not None:
            tab_bar_container.update()
        if hasattr(content_container, "page") and content_container.page is not None:
            content_container.update()

    # สร้างเนื้อหาเริ่มต้น
    tab_bar_container.content = build_tab_bar()
    refresh_content()

    # ใช้ ListView แทน Column เพื่อให้เลื่อนได้
    return ft.ListView(
        controls=[
            # Tab Bar
            ft.Container(content=tab_bar_container, margin=ft.margin.only(bottom=20)),
            # Content
            content_container,
            # ช่องว่างด้านล่าง
            ft.Container(height=50),
        ],
        expand=True,
        spacing=0,
        padding=ft.padding.only(top=20, bottom=20, left=10, right=10),
        auto_scroll=False,
    )
