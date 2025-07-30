import flet as ft
from storages.database_service import get_connection

# สีสำหรับใช้ในแอพ
WHITE = "#FFFFFF"
LIGHT_BLUE = "#ADD8E6"
LIGHT_GREEN = "#90EE90"
PINK = "#FFC0CB"
YELLOW = "#FFFF99"
RED = "#FF0000"
GREEN = "#008000"
ORANGE = "#FFA500"
GRAY = "#808080"

# ขนาดและระยะห่างของโหนด (ส่วนเดิม)
NODE_WIDTH = 120
NODE_HEIGHT = 80
HORIZONTAL_SPACING = 140
VERTICAL_SPACING = 100

pedigree_status_map = {
    "breeder1": "กำลังผสม",
    "breeder2": "พร้อมผสม",
    "fertilize": "ขุน",
    "dispose": "จำหน่าย",
}


def get_pedigree_tree():
    """ดึงข้อมูลพันธุ์ประวัติจากฐานข้อมูล (ส่วนเดิม)"""
    conn = get_connection()
    cursor = conn.cursor()

    pedigree = {}
    try:
        cursor.execute(
            """
                SELECT rat_id, father_id, mother_id, gender, status
                FROM rat
            """
        )

        for rat in cursor.fetchall():
            rat_id, father_id, mother_id, gender, status = rat
            pedigree[rat_id] = {
                "sire": father_id if father_id else "0",
                "dam": mother_id if mother_id else "0",
                "sex": gender,
                "status": status,
            }
    finally:
        conn.close()

    return pedigree


def truncate_text(text, max_len=10):
    """ตัดข้อความที่ยาวเกินและแทนที่ด้วย ... (ส่วนเดิม)"""
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def create_rat_card(rat_id, sex, status, is_selected=False, is_common=False):
    """สร้างการ์ดหนู"""
    sex_text = "Male" if sex == "male" else "Female"
    status_text = pedigree_status_map.get(status, status)

    # กำหนดสีตามเพศและสถานะ
    bg_color = (
        LIGHT_GREEN
        if is_selected
        else (YELLOW if is_common else (LIGHT_BLUE if sex == "male" else PINK))
    )
    border_color = (
        GREEN
        if is_selected
        else (ORANGE if is_common else (RED if status == "dispose" else bg_color))
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    truncate_text(rat_id),
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(sex_text, size=12, text_align=ft.TextAlign.CENTER),
                ft.Text(status_text, size=12, text_align=ft.TextAlign.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        # width=NODE_WIDTH,
        height=NODE_HEIGHT,
        bgcolor=bg_color,
        border=ft.border.all(2, border_color),
        border_radius=5,
        alignment=ft.alignment.center,
    )


def display_rat_pedigree_toggle(rat_id, max_generations=5):
    """
    แสดงแผนภูมิพันธุ์ประวัติของหนูแบบ toggle ด้วย Container และ IconButton

    Parameters:
    -----------
    rat_id : str
        รหัสหนูที่ต้องการดูพันธุ์ประวัติ
    max_generations : int, optional
        จำนวนรุ่นสูงสุดที่จะแสดงในแผนภูมิ (default: 5)

    Returns:
    --------
    ft.Column
        คอมโพเนนต์แสดงพันธุ์ประวัติแบบ toggle
    """
    pedigree = get_pedigree_tree()

    if rat_id not in pedigree:
        return ft.Text(f"Error: ไม่พบข้อมูลหนูรหัส {rat_id} ในระบบ")

    # สร้าง toggle tree ด้วย column และ container
    toggle_tree = ft.Column([], scroll=ft.ScrollMode.AUTO)

    # ฟังก์ชันสำหรับสร้าง toggle node สำหรับแต่ละหนู
    def create_toggle_node(rat_id, generation=0, prefix=""):
        if rat_id == "0" or rat_id not in pedigree or generation >= max_generations:
            return None

        # ดึงข้อมูลหนู
        rat_data = pedigree[rat_id]
        sex = rat_data.get("sex", "unknown")
        status = rat_data.get("status", "unknown")
        sire_id = rat_data.get("sire", "0")
        dam_id = rat_data.get("dam", "0")

        # กำหนดสีตามเพศและสถานะ
        bg_color = (
            LIGHT_GREEN if generation == 0 else (LIGHT_BLUE if sex == "male" else PINK)
        )
        border_color = (
            GREEN if generation == 0 else RED if status == "dispose" else bg_color
        )

        # แปลงสถานะเป็นข้อความที่อ่านได้
        status_text = pedigree_status_map.get(status, status)

        # สร้างตัวแปรเก็บข้อมูลลูก
        ancestors_content = ft.Column([], visible=False)

        # เตรียมสร้างลูก (พ่อและแม่) ถ้ามี
        has_ancestors = False
        if generation < max_generations:
            # หาพ่อ
            if sire_id != "0" and sire_id in pedigree:
                has_ancestors = True
                sire_node = create_toggle_node(sire_id, generation + 1, "พ่อ - ")
                if sire_node:
                    ancestors_content.controls.append(sire_node)

            # หาแม่
            if dam_id != "0" and dam_id in pedigree:
                has_ancestors = True
                dam_node = create_toggle_node(dam_id, generation + 1, "แม่ - ")
                if dam_node:
                    ancestors_content.controls.append(dam_node)

        # สร้างไอคอนสำหรับ toggle ถ้ามีบรรพบุรุษ
        toggle_icon = ft.Icon(
            name=ft.Icons.ARROW_RIGHT if has_ancestors else ft.Icons.PERSON,
            color=ft.Colors.BLACK,
            size=16,
        )

        # ฟังก์ชันสำหรับเปิด/ปิดบรรพบุรุษ
        def toggle_ancestors(e):
            ancestors_content.visible = not ancestors_content.visible
            toggle_icon.name = (
                ft.Icons.ARROW_DROP_DOWN
                if ancestors_content.visible
                else ft.Icons.ARROW_RIGHT
            )
            toggle_tree.update()

        # สร้าง Container แสดงข้อมูลหนู
        node_container = ft.Container(
            content=ft.Row(
                [
                    (
                        toggle_icon if has_ancestors else ft.Container(width=16)
                    ),  # ใช้ Container เป็น placeholder ถ้าไม่มีบรรพบุรุษ
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"{prefix}รหัส: {rat_id}",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{'ผู้' if sex == 'male' else 'เมีย'}",
                                        size=10,
                                        color=(
                                            ft.Colors.RED
                                            if sex != "male"
                                            else ft.Colors.BLUE
                                        ),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                spacing=10,
                            ),
                        ]
                    ),
                ],
                spacing=5,
            ),
            padding=10,
            bgcolor=bg_color,
            border=ft.border.all(2, border_color),
            border_radius=10,
            margin=ft.margin.only(left=generation * 20),  # เยื้องซ้ายตามระดับ
            on_click=(
                toggle_ancestors if has_ancestors else None
            ),  # เพิ่ม on_click เมื่อมีบรรพบุรุษ
            animate=300,  # เพิ่มการ animate เมื่อมีการเปลี่ยนแปลง
            tooltip=(
                "คลิกเพื่อดู/ซ่อนบรรพบุรุษ" if has_ancestors else None
            ),  # เพิ่ม tooltip เมื่อมีบรรพบุรุษ
        )

        # สร้าง Column สำหรับเก็บ node และลูกของมัน
        node_column = ft.Column(
            [
                node_container,
                ancestors_content,  # เพิ่มส่วนบรรพบุรุษที่จะแสดง/ซ่อนได้
            ]
        )

        # ถ้าเป็นรุ่นแรก (รุ่นที่เลือก) ให้เปิดแสดงบรรพบุรุษทันที
        if generation == 0 and has_ancestors:
            ancestors_content.visible = True
            toggle_icon.name = ft.Icons.ARROW_DROP_DOWN

        return node_column

    # สร้าง toggle tree เริ่มจากหนูที่เลือก
    root_node = create_toggle_node(rat_id)
    if root_node:
        toggle_tree.controls.append(root_node)

    # สร้างแผนภูมิและเส้นเชื่อม
    all_ancestors = []  # เก็บรหัสบรรพบุรุษทั้งหมด

    # ฟังก์ชันหาบรรพบุรุษทั้งหมด
    def collect_ancestors(rat_id, generation=0):
        if rat_id == "0" or rat_id not in pedigree or generation >= max_generations:
            return

        all_ancestors.append(rat_id)

        # หาบรรพบุรุษของพ่อ
        sire_id = pedigree[rat_id]["sire"]
        if sire_id != "0" and sire_id in pedigree:
            collect_ancestors(sire_id, generation + 1)

        # หาบรรพบุรุษของแม่
        dam_id = pedigree[rat_id]["dam"]
        if dam_id != "0" and dam_id in pedigree:
            collect_ancestors(dam_id, generation + 1)

    # เก็บรหัสบรรพบุรุษทั้งหมด
    collect_ancestors(rat_id)

    # ตรวจสอบการผสมเลือดชิด
    duplicated_ancestors = []

    # ฟังก์ชันนับเส้นทางระหว่างโหนด
    def count_paths(from_id, to_id, visited=None):
        if visited is None:
            visited = set()

        if from_id == to_id:
            return 1

        if from_id in visited or from_id == "0" or from_id not in pedigree:
            return 0

        visited.add(from_id)

        paths = 0
        # เช็คเส้นทางผ่านพ่อ
        sire_id = pedigree[from_id]["sire"]
        if sire_id != "0" and sire_id in pedigree:
            paths += count_paths(sire_id, to_id, visited.copy())

        # เช็คเส้นทางผ่านแม่
        dam_id = pedigree[from_id]["dam"]
        if dam_id != "0" and dam_id in pedigree:
            paths += count_paths(dam_id, to_id, visited.copy())

        return paths

    # หาบรรพบุรุษที่ปรากฏซ้ำ
    for ancestor in all_ancestors:
        if ancestor == rat_id:
            continue

        # นับจำนวนเส้นทางจากบรรพบุรุษไปยังหนูตัวหลัก
        paths_count = count_paths(ancestor, rat_id)

        if paths_count > 1:
            duplicated_ancestors.append((ancestor, paths_count))

    # สร้างคำอธิบายสัญลักษณ์ (legend)
    legend = ft.Row(
        [
            ft.Row(
                [
                    ft.Container(
                        width=20, height=20, bgcolor=LIGHT_GREEN, border_radius=5
                    ),
                    ft.Text("หนูตัวที่เลือก", size=12),
                ],
            ),
            ft.Row(
                [
                    ft.Container(
                        width=20, height=20, bgcolor=LIGHT_BLUE, border_radius=5
                    ),
                    ft.Text("ตัวผู้", size=12),
                ],
            ),
            ft.Row(
                [
                    ft.Container(width=20, height=20, bgcolor=PINK, border_radius=5),
                    ft.Text("ตัวเมีย", size=12),
                ],
            ),
            ft.Row(
                [
                    ft.Container(
                        width=20,
                        height=20,
                        bgcolor=WHITE,
                        border=ft.border.all(2, RED),
                        border_radius=5,
                    ),
                    ft.Text("จำหน่าย", size=12),
                ],
            ),
            ft.Row(
                [
                    ft.Container(
                        width=20,
                        height=20,
                        bgcolor=YELLOW,
                        border=ft.border.all(2, ORANGE),
                        border_radius=5,
                    ),
                    ft.Text("บรรพบุรุษซ้ำ", size=12),
                ],
                visible=bool(duplicated_ancestors),
            ),
        ],
        spacing=5,
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )

    # เพิ่มคำแนะนำการใช้งาน
    usage_hint = ft.Text(
        "กดที่หนูแต่ละตัวเพื่อดู/ซ่อนบรรพบุรุษ",
        size=12,
        italic=True,
        color=ft.Colors.GREY_700,
    )

    # รวมทุกส่วนเข้าด้วยกัน
    return ft.Container(
        content=ft.Column(
            [
                usage_hint,
                ft.Container(
                    content=toggle_tree,
                    padding=10,
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    bgcolor=WHITE,
                    expand=True,
                ),
                ft.Divider(),
                legend,
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        expand=True,
    )


def check_mating_compatibility_toggle(animal1_id, animal2_id, max_generations=4):
    """
    ตรวจสอบความเข้ากันได้ของการผสมพันธุ์แบบ toggle โดยใช้ Container

    Parameters:
    -----------
    animal1_id : str
        รหัสหนูตัวที่ 1
    animal2_id : str
        รหัสหนูตัวที่ 2
    max_generations : int, optional
        จำนวนรุ่นสูงสุดที่จะตรวจสอบ (default: 4)

    Returns:
    --------
    ft.Column
        คอมโพเนนต์แสดงผลการตรวจสอบ
    """
    pedigree = get_pedigree_tree()

    if animal1_id not in pedigree or animal2_id not in pedigree:
        return ft.Text("Error: ไม่พบข้อมูลหนูในระบบ")

    # สร้างโครงสร้างข้อมูลสำหรับหาบรรพบุรุษของทั้งสองตัว
    ancestors1 = {}  # {rat_id: generation}
    ancestors2 = {}  # {rat_id: generation}

    # ฟังก์ชันหาบรรพบุรุษ
    def find_ancestors(rat_id, ancestors_dict, generation=0):
        if rat_id == "0" or rat_id not in pedigree or generation >= max_generations:
            return

        # บันทึกบรรพบุรุษ
        ancestors_dict[rat_id] = generation

        # หาบรรพบุรุษพ่อ
        father_id = pedigree[rat_id]["sire"]
        if father_id != "0" and father_id in pedigree:
            find_ancestors(father_id, ancestors_dict, generation + 1)

        # หาบรรพบุรุษแม่
        mother_id = pedigree[rat_id]["dam"]
        if mother_id != "0" and mother_id in pedigree:
            find_ancestors(mother_id, ancestors_dict, generation + 1)

    # หาบรรพบุรุษของหนูทั้งสองตัว
    find_ancestors(animal1_id, ancestors1)
    find_ancestors(animal2_id, ancestors2)

    # หาบรรพบุรุษร่วม
    common_ancestors = []
    for ancestor_id in set(ancestors1.keys()) & set(ancestors2.keys()):
        if ancestor_id != animal1_id and ancestor_id != animal2_id:
            common_ancestors.append(
                (
                    ancestor_id,
                    ancestors1[ancestor_id],  # รุ่นใน animal1
                    ancestors2[ancestor_id],  # รุ่นใน animal2
                )
            )

    # สร้าง tree สำหรับหนูทั้งสองตัว
    animal1_tree = ft.Column([], scroll=ft.ScrollMode.AUTO)
    animal2_tree = ft.Column([], scroll=ft.ScrollMode.AUTO)

    # ฟังก์ชันสำหรับสร้าง toggle node สำหรับแต่ละหนู
    def create_toggle_node(rat_id, tree, generation=0, prefix=""):
        if rat_id == "0" or rat_id not in pedigree or generation >= max_generations:
            return None

        # ดึงข้อมูลหนู
        rat_data = pedigree[rat_id]
        sex = rat_data.get("sex", "unknown")
        status = rat_data.get("status", "unknown")
        sire_id = rat_data.get("sire", "0")
        dam_id = rat_data.get("dam", "0")

        # กำหนดสีตามเพศและสถานะ
        is_common = any(rat_id == a[0] for a in common_ancestors)
        bg_color = (
            LIGHT_GREEN
            if generation == 0
            else (YELLOW if is_common else (LIGHT_BLUE if sex == "male" else PINK))
        )
        border_color = (
            GREEN
            if generation == 0
            else (ORANGE if is_common else (RED if status == "dispose" else bg_color))
        )

        # แปลงสถานะเป็นข้อความที่อ่านได้
        status_text = pedigree_status_map.get(status, status)

        # สร้างตัวแปรเก็บข้อมูลลูก
        ancestors_content = ft.Column([], visible=False)

        # เตรียมสร้างลูก (พ่อและแม่) ถ้ามี
        has_ancestors = False
        if generation < max_generations:
            # หาพ่อ
            if sire_id != "0" and sire_id in pedigree:
                has_ancestors = True
                sire_node = create_toggle_node(sire_id, tree, generation + 1, "พ่อ - ")
                if sire_node:
                    ancestors_content.controls.append(sire_node)

            # หาแม่
            if dam_id != "0" and dam_id in pedigree:
                has_ancestors = True
                dam_node = create_toggle_node(dam_id, tree, generation + 1, "แม่ - ")
                if dam_node:
                    ancestors_content.controls.append(dam_node)

        # สร้างไอคอนสำหรับ toggle ถ้ามีบรรพบุรุษ
        toggle_icon = ft.Icon(
            name=ft.Icons.ARROW_RIGHT if has_ancestors else ft.Icons.PERSON,
            color=ft.Colors.BLACK,
            size=16,
        )

        # ฟังก์ชันสำหรับเปิด/ปิดบรรพบุรุษ
        def toggle_ancestors(e):
            ancestors_content.visible = not ancestors_content.visible
            toggle_icon.name = (
                ft.Icons.ARROW_DROP_DOWN
                if ancestors_content.visible
                else ft.Icons.ARROW_RIGHT
            )
            tree.update()  # อัปเดตเฉพาะ tree ที่เกี่ยวข้อง

        # สร้าง Container แสดงข้อมูลหนู
        node_container = ft.Container(
            content=ft.Row(
                [
                    (
                        toggle_icon if has_ancestors else ft.Container(width=16)
                    ),  # ใช้ Container เป็น placeholder ถ้าไม่มีบรรพบุรุษ
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Text(
                                        f"{prefix}รหัส: {rat_id}",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        f"{'ผู้' if sex == 'male' else 'เมีย'}",
                                        size=10,
                                        color=(
                                            ft.Colors.RED
                                            if sex != "male"
                                            else ft.Colors.BLUE
                                        ),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                spacing=10,
                            ),
                        ]
                    ),
                ],
                spacing=5,
            ),
            padding=10,
            bgcolor=bg_color,
            border=ft.border.all(2, border_color),
            border_radius=10,
            margin=ft.margin.only(left=generation * 20),  # เยื้องซ้ายตามระดับ
            on_click=(
                toggle_ancestors if has_ancestors else None
            ),  # เพิ่ม on_click เมื่อมีบรรพบุรุษ
            animate=300,  # เพิ่มการ animate เมื่อมีการเปลี่ยนแปลง
            tooltip=(
                "คลิกเพื่อดู/ซ่อนบรรพบุรุษ" if has_ancestors else None
            ),  # เพิ่ม tooltip เมื่อมีบรรพบุรุษ
        )

        # สร้าง Column สำหรับเก็บ node และลูกของมัน
        node_column = ft.Column(
            [
                node_container,
                ancestors_content,  # เพิ่มส่วนบรรพบุรุษที่จะแสดง/ซ่อนได้
            ]
        )

        # ถ้าเป็นรุ่นแรก (รุ่นที่เลือก) ให้เปิดแสดงบรรพบุรุษทันที
        if generation == 0 and has_ancestors:
            ancestors_content.visible = True
            toggle_icon.name = ft.Icons.ARROW_DROP_DOWN

        return node_column

    # สร้าง tree สำหรับหนูทั้งสองตัว
    root1_node = create_toggle_node(animal1_id, animal1_tree)
    if root1_node:
        animal1_tree.controls.append(root1_node)

    root2_node = create_toggle_node(animal2_id, animal2_tree)
    if root2_node:
        animal2_tree.controls.append(root2_node)

    # สร้างข้อมูลสรุป
    summary_info = []
    summary_info.append(f"ผลการตรวจสอบความเข้ากันได้ของการผสมพันธุ์")
    summary_info.append(f"หนูรหัส {animal1_id} และ {animal2_id}")

    if common_ancestors:
        summary_info.append("\nพบบรรพบุรุษร่วมกัน:")
        for ancestor_id, gen1, gen2 in common_ancestors:
            summary_info.append(
                f"- {ancestor_id}: อยู่ในรุ่นที่ {gen1 + 1} ของหนูตัวแรก และรุ่นที่ {gen2 + 1} ของหนูตัวที่สอง"
            )
        summary_info.append(
            "\nคำเตือน: การผสมพันธุ์ระหว่างหนูที่มีบรรพบุรุษร่วมกันอาจนำไปสู่การผสมเลือดชิด (inbreeding)"
        )
    else:
        summary_info.append("\nไม่พบบรรพบุรุษร่วมกันในรุ่นที่ตรวจสอบ")

    # สร้างคำอธิบายสัญลักษณ์ (legend)
    legend = ft.Row(
        [
            ft.Row(
                [
                    ft.Container(
                        width=20, height=20, bgcolor=LIGHT_GREEN, border_radius=5
                    ),
                    ft.Text("หนูที่เลือก", size=12),
                ],
                spacing=5,
            ),
            ft.Row(
                [
                    ft.Container(
                        width=20, height=20, bgcolor=LIGHT_BLUE, border_radius=5
                    ),
                    ft.Text("ตัวผู้", size=12),
                ],
                spacing=5,
            ),
            ft.Row(
                [
                    ft.Container(width=20, height=20, bgcolor=PINK, border_radius=5),
                    ft.Text("ตัวเมีย", size=12),
                ],
                spacing=5,
            ),
            ft.Row(
                [
                    ft.Container(
                        width=20,
                        height=20,
                        bgcolor=YELLOW,
                        border=ft.border.all(2, ORANGE),
                        border_radius=5,
                    ),
                    ft.Text("บรรพบุรุษร่วม", size=12),
                ],
                spacing=5,
                visible=bool(common_ancestors),
            ),
        ],
        spacing=5,
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )

    # เพิ่มคำแนะนำการใช้งาน
    usage_hint = ft.Text(
        "คลิกที่หนูแต่ละตัวเพื่อดู/ซ่อนบรรพบุรุษ",
        size=12,
        italic=True,
        color=ft.Colors.GREY_700,
    )

    # รวมทุกส่วนเข้าด้วยกัน
    return ft.Column(
        [
            usage_hint,  # เพิ่มคำแนะนำการใช้งาน
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("หนูตัวที่ 1:", size=14, weight=ft.FontWeight.BOLD),
                        animal1_tree,
                        ft.Divider(),
                        ft.Text("หนูตัวที่ 2:", size=14, weight=ft.FontWeight.BOLD),
                        animal2_tree,
                    ]
                ),
                padding=10,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                bgcolor=WHITE,
                expand=True,
            ),
            ft.Divider(),
            ft.Text("\n".join(summary_info), text_align=ft.TextAlign.LEFT),
            legend,
        ],
        spacing=5,
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )


def generate_pedigree_chart(rat_id_field):
    """
    สร้าง Container สำหรับแสดงแผนภาพพันธุ์ประวัติ

    Parameters:
    -----------
    rat_id_field : ft.TextField
        TextField ที่เก็บค่า rat_id

    Returns:
    --------
    ft.Container
        Container ที่มีแผนภาพพันธุ์ประวัติ
    """
    if not rat_id_field.value:
        return ft.Container(
            content=ft.Text("กรุณาระบุรหัสหนูก่อนแสดงพันธุ์ประวัติ"),
            bgcolor=WHITE,
            border_radius=10,
            padding=10,
        )

    # สร้างส่วนแผนภาพพันธุ์ประวัติแบบ toggle
    return ft.Container(
        content=ft.Column(
            [
                ft.Text("แผนภาพพันธุ์ประวัติแบบ Toggle", size=14, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                ft.Text(
                    f"แสดงแผนภาพพันธุ์ประวัติของหนูรหัส {rat_id_field.value}",
                    text_align=ft.TextAlign.LEFT,
                ),
                display_rat_pedigree_toggle(rat_id_field.value, 5),  # แสดง 5 รุ่น
            ],
            expand=True,
        ),
        bgcolor=WHITE,
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


def generate_mating_compatibility_chart(animal1_id_field, animal2_id_field):
    """
    สร้าง Container สำหรับแสดงการตรวจสอบความเข้ากันได้ของการผสมพันธุ์

    Parameters:
    -----------
    animal1_id_field : ft.TextField
        TextField ที่เก็บค่า animal1_id
    animal2_id_field : ft.TextField
        TextField ที่เก็บค่า animal2_id

    Returns:
    --------
    ft.Container
        Container ที่มีผลการตรวจสอบความเข้ากันได้
    """
    if not animal1_id_field.value or not animal2_id_field.value:
        return ft.Container(
            content=ft.Text("กรุณาระบุรหัสหนูทั้งสองตัวก่อนตรวจสอบความเข้ากันได้"),
            bgcolor=WHITE,
            border_radius=10,
            padding=10,
        )

    # สร้างส่วนแผนภาพการตรวจสอบความเข้ากันได้แบบ toggle
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "ผลการตรวจสอบความเข้ากันได้แบบ Toggle",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_300),
                ft.Text(
                    f"ความสัมพันธ์ทางพันธุกรรมระหว่างหนูรหัส {animal1_id_field.value} และ {animal2_id_field.value}",
                    text_align=ft.TextAlign.LEFT,
                ),
                check_mating_compatibility_toggle(
                    animal1_id_field.value, animal2_id_field.value, 4  # แสดง 4 รุ่น
                ),
            ]
        ),
        bgcolor=WHITE,
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


# ส่วนแสดงผลตัวอย่าง - คงส่วนนี้ไว้เหมือนเดิม แต่เปลี่ยนเมธอดข้างใน
class PedigreePage(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.bgcolor = WHITE
        self.padding = 20
        self.border_radius = 10
        self.shadow = ft.BoxShadow(
            spread_radius=0.1,
            blur_radius=1,
            color=ft.Colors.GREY_300,
            offset=ft.Offset(0, 0),
        )

        # สร้างส่วนแสดงพันธุ์ประวัติ
        self.rat_id_field = ft.TextField(
            label="รหัสหนู",
            hint_text="กรอกรหัสหนูที่ต้องการดูข้อมูล",
            # width=200,
        )

        self.pedigree_container = ft.Container(
            content=ft.Text("กรุณากรอกรหัสหนูและกดปุ่มแสดงข้อมูล"),
            padding=10,
            bgcolor=WHITE,
            border_radius=10,
            expand=True,
        )

        # ส่วนของการตรวจสอบความเข้ากันได้
        self.rat1_id_field = ft.TextField(
            label="รหัสหนูตัวที่ 1",
            hint_text="กรอกรหัสหนูตัวที่ 1",
            # width=200,
        )

        self.rat2_id_field = ft.TextField(
            label="รหัสหนูตัวที่ 2",
            hint_text="กรอกรหัสหนูตัวที่ 2",
            # width=200,
        )

        self.compatibility_container = ft.Container(
            content=ft.Text("กรุณากรอกรหัสหนูทั้งสองตัวและกดปุ่มตรวจสอบ"),
            padding=10,
            bgcolor=WHITE,
            border_radius=10,
            expand=True,
        )

        # สร้างปุ่มและอีเวนต์
        self.show_pedigree_button = ft.ElevatedButton(
            "แสดงพันธุ์ประวัติ",
            on_click=self.show_pedigree,
        )

        self.check_compatibility_button = ft.ElevatedButton(
            "ตรวจสอบความเข้ากันได้",
            on_click=self.check_compatibility,
        )

        # จัดวางองค์ประกอบหน้าจอ
        self.content = ft.Column(
            [
                # ส่วนแสดงพันธุ์ประวัติ
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("ข้อมูลพันธุ์ประวัติ", size=18, weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            ft.Row(
                                [
                                    self.rat_id_field,
                                    self.show_pedigree_button,
                                ]
                            ),
                            self.pedigree_container,
                        ]
                    ),
                    bgcolor=WHITE,
                    border_radius=10,
                    padding=20,
                    margin=10,
                    shadow=ft.BoxShadow(
                        spread_radius=0.1,
                        blur_radius=1,
                        color=ft.Colors.GREY_300,
                        offset=ft.Offset(0, 0),
                    ),
                    expand=True,
                ),
                # ส่วนตรวจสอบความเข้ากันได้
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "ตรวจสอบความเข้ากันได้ของการผสมพันธุ์",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Divider(),
                            ft.Row(
                                [
                                    self.rat1_id_field,
                                    self.rat2_id_field,
                                    self.check_compatibility_button,
                                ]
                            ),
                            self.compatibility_container,
                        ]
                    ),
                    bgcolor=WHITE,
                    border_radius=10,
                    padding=20,
                    margin=10,
                    shadow=ft.BoxShadow(
                        spread_radius=0.1,
                        blur_radius=1,
                        color=ft.Colors.GREY_300,
                        offset=ft.Offset(0, 0),
                    ),
                    expand=True,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def show_pedigree(self, e):
        """แสดงพันธุ์ประวัติของหนูแบบ toggle"""
        # สร้างการโหลด
        self.pedigree_container.content = ft.ProgressRing()
        self.page.update()

        # สร้างแผนภาพพันธุ์ประวัติแบบ toggle
        try:
            self.pedigree_container.content = display_rat_pedigree_toggle(
                self.rat_id_field.value, 5
            )
            self.page.update()
        except Exception as ex:
            self.pedigree_container.content = ft.Text(f"เกิดข้อผิดพลาด: {str(ex)}")
            self.page.update()

    def check_compatibility(self, e):
        """ตรวจสอบความเข้ากันได้ของการผสมพันธุ์แบบ toggle"""
        # สร้างการโหลด
        self.compatibility_container.content = ft.ProgressRing()
        self.page.update()

        # สร้างแผนภาพตรวจสอบความเข้ากันได้แบบ toggle
        try:
            self.compatibility_container.content = check_mating_compatibility_toggle(
                self.rat1_id_field.value, self.rat2_id_field.value, 4
            )
            self.page.update()
        except Exception as ex:
            self.compatibility_container.content = ft.Text(f"เกิดข้อผิดพลาด: {str(ex)}")
            self.page.update()
