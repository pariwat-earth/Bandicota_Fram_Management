import flet as ft
from components.app_bar import base_appbar
from pages.health_page import health_page
from pages.breeding_page import breeding_page
from pages.farmer_page import farmer_page
from pages.import_export_page import import_export_page
from pages.main_page import main_page
from pages.rat_page import rat_page
from pages.notifications_page import notifications_page
from pages.report_page import report_page  # เพิ่มการ import
from pages.advanced_report_page import advanced_report_page  # เพิ่มการ import
from storages.database_service import get_selected_farm_id
from storages.general_information import (
    get_current_page_name,
    get_managername,
    update_hmt_page,
    get_farm_name
)
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, White


def structure_screen():
    app_bar = base_appbar(title_name=get_farm_name())

    # Container สำหรับแสดง content
    content_container = ft.Container(
        expand=True,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )

    # ตัวแปรเก็บ navigation bar เพื่อใช้อ้างอิง
    navigation_bar = None

    # ฟังก์ชันสำหรับเปลี่ยน content และ update navigation
    def change_content(content_func, nav_index=None):
        # บันทึกหน้าปัจจุบัน
        page_name = ""

        if content_func == content_main:
            page_name = "main"
        elif content_func == content_pond:
            page_name = "ponds"
        elif content_func == content_farmer:
            page_name = "farmer"
        elif content_func == content_mating:
            page_name = "mating"
        elif content_func == content_mouse_info:
            page_name = "mouse_info"
        elif content_func == content_health:
            page_name = "health"
        elif content_func == content_report:
            page_name = "report"
        elif content_func == content_advanced_report:  # เพิ่มเงื่อนไข
            page_name = "advanced_report"
        elif content_func == content_import_export:
            page_name = "import_export"
        elif content_func == content_notifications:
            page_name = "notifications"

        # บันทึกชื่อหน้าปัจจุบันลงในฐานข้อมูล
        if page_name:
            update_hmt_page(page_name)

        content_container.content = content_func()
        content_container.update()

        # อัพเดท navigation bar ถ้ามีการส่ง index มา
        if nav_index is not None and navigation_bar:
            navigation_bar.selected_index = nav_index
            navigation_bar.update()

    # สร้าง content สำหรับแต่ละหน้า
    def content_main():
        return main_page(
            change_content,
            {
                "mating": content_mating,
                "mouse_info": content_add,
                "farmer": content_farmer,
                "health": content_health,
                "report": content_report,
                "advanced_report": content_advanced_report,  # เพิ่มการแจ้งเตือน
                "import_export": content_import_export,
                "notifications": content_notifications,
                "main": content_main,
            },
            {
                "mating": 1,
                "mouse_info": 2,
                "health": 4,
                "report": 4,
                "advanced_report": 4,  # เพิ่ม
                "notifications": 0,
                "main": 0,
            },
        )

    def content_mating():
        return breeding_page()

    def content_add():
        return rat_page("add")

    def content_mouse_info():
        return rat_page("view")

    def content_farmer():
        return farmer_page()

    def content_pond():
        from pages.pond_page import pond_page

        return pond_page()

    def content_health():
        return health_page()

    def content_report():
        # ส่ง callback และ functions เพื่อให้สามารถเรียกหน้า advanced report ได้
        return report_page(
            change_content,
            {
                "advanced_report": content_advanced_report,
                "report": content_report,
                "main": content_main,
            },
            {
                "advanced_report": 4,
                "report": 4,
                "main": 0,
            },
        )

    def content_advanced_report():  # เพิ่มฟังก์ชันใหม่
        return advanced_report_page()

    def content_import_export():
        return import_export_page()

    def content_notifications():
        return notifications_page(
            change_content,
            {
                "main": content_main,
                "notifications": content_notifications,
                "mating": content_mating,
                "mouse_info": content_mouse_info,
                "farmer": content_farmer,
                "health": content_health,
                "report": content_report,
                "advanced_report": content_advanced_report,  # เพิ่ม
                "import_export": content_import_export,
            },
            {
                "main": 0,
                "notifications": 0,
                "mating": 1,
                "mouse_info": 2,
                "farmer": 4,
                "health": 4,
                "report": 4,
                "advanced_report": 4,  # เพิ่ม
                "import_export": 4,
            },
            page=content_container.page if hasattr(content_container, "page") else None,
        )

    def page_setup():
        # ตั้งค่าหน้าเริ่มต้นตามที่บันทึกไว้ในฐานข้อมูล
        current_page = get_current_page_name()

        if current_page == "main":
            content_container.content = content_main()
            if navigation_bar:
                navigation_bar.selected_index = 0
        elif current_page == "mating":
            content_container.content = content_mating()
            if navigation_bar:
                navigation_bar.selected_index = 1
        elif current_page == "add":
            content_container.content = content_add()
            if navigation_bar:
                navigation_bar.selected_index = 2
        elif current_page == "mouse_info":
            content_container.content = content_mouse_info()
            if navigation_bar:
                navigation_bar.selected_index = 3
        elif current_page == "farmer":
            content_container.content = content_farmer()
            if navigation_bar:
                navigation_bar.selected_index = 4
        elif current_page == "pond_page":
            farm_id = get_selected_farm_id()
            if farm_id:
                from pages.pond_page import pond_page

                content_container.content = pond_page(farm_id)
            else:
                content_container.content = content_pond()
            if navigation_bar:
                navigation_bar.selected_index = 4
        elif current_page == "health":
            content_container.content = content_health()
            if navigation_bar:
                navigation_bar.selected_index = 4
        elif current_page == "report":
            content_container.content = content_report()
            if navigation_bar:
                navigation_bar.selected_index = 4
        elif current_page == "advanced_report":  # เพิ่มเงื่อนไข
            content_container.content = content_advanced_report()
            if navigation_bar:
                navigation_bar.selected_index = 4
        elif current_page == "import_export":
            content_container.content = content_import_export()
            if navigation_bar:
                navigation_bar.selected_index = 4
        elif current_page == "notifications":
            content_container.content = content_notifications()
            if navigation_bar:
                navigation_bar.selected_index = 0
        else:
            content_container.content = content_main()
            if navigation_bar:
                navigation_bar.selected_index = 0

    # ตั้งค่าหน้าเริ่มต้น
    page_setup()

    # สร้าง NavigationDrawer สำหรับเมนู
    def handle_drawer_item_click(page_func, nav_index=None):
        def on_click(e):
            change_content(page_func, nav_index)
            menu_drawer.open = False
            e.control.page.update()

        return on_click

    menu_drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("เมนูหลัก", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(
                            content=ft.Container(
                                gradient=ft.LinearGradient(
                                    begin=ft.alignment.center_left,
                                    end=ft.alignment.center_right,
                                    colors=[
                                        ft.Colors.with_opacity(0.1, Neo_Mint),
                                        ft.Colors.with_opacity(0.1, Deep_Purple),
                                    ],
                                ),
                                content=ft.ListTile(
                                    leading=ft.CircleAvatar(
                                        content=ft.Text(
                                            list(get_managername())[0],
                                            size=20,
                                            weight=ft.FontWeight.BOLD,
                                            color=White,
                                        ),
                                        bgcolor=Deep_Purple,
                                    ),
                                    title=ft.Text(
                                        get_managername(),
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=Black,
                                    ),
                                    subtitle=ft.Text(
                                        "ผู้จัดการฟาร์ม",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=Grey,
                                    ),
                                ),
                                border_radius=7,
                            )
                        ),
                        ft.Divider(),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.HOME_OUTLINED),
                            title=ft.Text("หน้าหลัก"),
                            on_click=handle_drawer_item_click(content_main, 0),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.CIRCLE_OUTLINED),
                            title=ft.Text("ฟาร์ม/บ่อเลี้ยง"),
                            on_click=handle_drawer_item_click(content_farmer, 4),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LIST_ALT),
                            title=ft.Text("ข้อมูลหนู"),
                            on_click=handle_drawer_item_click(content_mouse_info, 3),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.FAVORITE_OUTLINE_ROUNDED),
                            title=ft.Text("การผสมพันธุ์"),
                            on_click=handle_drawer_item_click(content_mating, 1),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.HEALTH_AND_SAFETY_OUTLINED),
                            title=ft.Text("สุขภาพหนู"),
                            on_click=handle_drawer_item_click(content_health, 4),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.INSERT_CHART_OUTLINED),
                            title=ft.Text("รายงานและสถิติ"),
                            on_click=handle_drawer_item_click(content_report, 4),
                        ),
                        # ft.ListTile(  # เพิ่มเมนูรายงานขั้นสูง
                        #     leading=ft.Icon(ft.Icons.ANALYTICS_OUTLINED),
                        #     title=ft.Text("รายงานขั้นสูง"),
                        #     on_click=handle_drawer_item_click(
                        #         content_advanced_report, 4
                        #     ),
                        # ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.LABEL_IMPORTANT_OUTLINE),
                            title=ft.Text("นำเข้า/ส่งออก"),
                            on_click=handle_drawer_item_click(content_import_export, 4),
                        ),
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED),
                            title=ft.Text("การแจ้งเตือน"),
                            on_click=handle_drawer_item_click(content_notifications, 0),
                        ),
                    ]
                ),
                padding=ft.padding.all(10),
                alignment=ft.alignment.top_left,
            ),
        ],
        bgcolor=White,
    )

    # ฟังก์ชันเปิด drawer
    def open_menu_drawer(page):
        page.end_drawer = menu_drawer
        menu_drawer.open = True
        page.update()

    # ฟังก์ชันสำหรับเปลี่ยนหน้า
    def on_navigation_change(e):
        selected_index = e.control.selected_index

        if selected_index == 0:
            change_content(content_main, 0)
        elif selected_index == 1:
            change_content(content_mating, 1)
        elif selected_index == 2:
            change_content(content_mouse_info, 2)
        elif selected_index == 3:
            open_menu_drawer(e.control.page)
            return

        content_container.update()

    def get_current_page_index():
        current_page = get_current_page_name()

        page_to_index = {
            "main": 0,
            "mating": 1,
            "mouse_info": 2,
            "farmer": 3,
            "pond_page": 3,
            "health": 3,
            "report": 3,
            "advanced_report": 3,  # เพิ่ม
            "import_export": 3,
            "notifications": 0,
        }
        return page_to_index.get(current_page, 0)

    # สร้าง Navigation Bar
    navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="หน้าหลัก"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.FAVORITE_OUTLINE_ROUNDED,
                selected_icon=ft.Icons.FAVORITE,
                label="ผสมพันธุ์",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.LIST_ALT, selected_icon=ft.Icons.LIST, label="ข้อมูลหนู"
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.MENU, selected_icon=ft.Icons.MENU, label="เมนู"
            ),
        ],
        bgcolor=White,
        on_change=on_navigation_change,
        selected_index=get_current_page_index(),
    )

    # สร้าง Container สำหรับ app_bar ที่จะขยายเต็มจอ
    app_bar_container = ft.ResponsiveRow(
        controls=[app_bar],
        expand=False,
        col={"xs": 12, "sm": 12, "md": 12, "lg": 12, "xl": 12},
    )

    # สร้าง Container หลักที่รวมทุกอย่าง
    main_container = ft.Container(
        content=ft.Column(
            controls=[app_bar_container, content_container, navigation_bar],
            spacing=0,
            expand=True,
            width=None,
        ),
        expand=True,
        padding=0,
        margin=0,
    )

    return main_container
