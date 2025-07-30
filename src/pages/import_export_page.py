import flet as ft
import threading
import time
from datetime import datetime
from components.base_button import base_button_gradient, base_button_normal
from components.base_box import base_empty_box
from storages.database_service import (
    export_all_rats,
    export_rat_with_ancestors,
    get_all_farm,
    get_all_rat_data,
)
from storages.general_information import (
    analyze_csv_for_ring_changes,
    get_export_history,
    get_import_history,
    import_rat_from_csv,
)
from styles.colors import Black, Deep_Purple, Grey, Neo_Mint, Red, White


def import_export_page():
    """หน้าจัดการนำเข้า/ส่งออกข้อมูล"""

    # ตัวแปรสถานะ
    current_view = "main"  # main, import, export, history
    selected_file_path = None

    # ข้อความแสดงผลลัพธ์
    result_container = ft.Container(
        content=ft.Text("", size=12, visible=False),
        padding=10,
        border_radius=8,
        margin=ft.margin.only(bottom=10),
        visible=False,
    )

    text_style = ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color=Grey)

    # สร้าง FilePicker หลักที่จะใช้ทั้งหมด
    file_picker = ft.FilePicker(on_result=lambda e: handle_file_pick(e))

    selected_file_text = ft.Text("ยังไม่ได้เลือกไฟล์", size=12, color=Grey)
    
    # สร้าง Container สำหรับ ring notification (เริ่มต้นซ่อนไว้)
    ring_notification_container = ft.Container(
        visible=False,
        margin=ft.margin.only(top=10, bottom=10),
    )

    def validate_csv_content(file_path):
        """ตรวจสอบเนื้อหา CSV รายละเอียด"""
        try:
            import pandas as pd
            
            # อ่านไฟล์ CSV
            df = pd.read_csv(file_path)
            
            # ตรวจสอบ columns ที่จำเป็น
            required_columns = ['rat_id', 'father_id', 'mother_id', 'birth_date', 'gender', 
                              'weight', 'size', 'breed', 'status', 'pond_id', 'farm_id', 
                              'has_ring', 'ring_number', 'special_traits', 'generation']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {"success": False, "message": f"ขาด columns: {', '.join(missing_columns)}"}
            
            # ตรวจสอบข้อมูลในแต่ละแถว
            for index, row in df.iterrows():
                row_num = index + 2  # +2 เพราะ index เริ่มจาก 0 และมี header
                
                # ตรวจสอบเพศ
                if pd.notna(row['gender']):
                    gender = str(row['gender']).strip().lower()
                    if gender not in ['male', 'female']:
                        return {"success": False, "message": f"แถว {row_num}: เพศต้องเป็น 'male' หรือ 'female' (พบ: '{row['gender']}')"} 
                
                # ตรวจสอบวันที่
                if pd.notna(row['birth_date']):
                    try:
                        pd.to_datetime(row['birth_date'])
                    except:
                        return {"success": False, "message": f"แถว {row_num}: รูปแบบวันที่ไม่ถูกต้อง ต้องเป็น YYYY-MM-DD (พบ: '{row['birth_date']}')"} 
                
                # ตรวจสอบน้ำหนัก
                if pd.notna(row['weight']):
                    try:
                        float(row['weight'])
                    except:
                        return {"success": False, "message": f"แถว {row_num}: น้ำหนักต้องเป็นตัวเลข (พบ: '{row['weight']}')"} 
                
                # ตรวจสอบขนาด
                if pd.notna(row['size']):
                    try:
                        float(row['size'])
                    except:
                        return {"success": False, "message": f"แถว {row_num}: ขนาดต้องเป็นตัวเลข (พบ: '{row['size']}')"} 
            
            return {"success": True, "message": "ไฟล์ผ่านการตรวจสอบเนื้อหา"}
            
        except Exception as e:
            return {"success": False, "message": f"ไม่สามารถตรวจสอบเนื้อหาไฟล์ได้: {str(e)[:100]}"}


    def validate_csv_basic(file_path):
        """ตรวจสอบไฟล์ CSV เบื้องต้น"""
        try:
            # ตรวจสอบว่าไฟล์มีอยู่จริง
            import os
            if not os.path.exists(file_path):
                return {"success": False, "message": "ไม่พบไฟล์ที่เลือก"}
            
            # ตรวจสอบว่าเป็นไฟล์ CSV
            if not file_path.lower().endswith('.csv'):
                return {"success": False, "message": "ไฟล์ต้องเป็นนามสกุล .csv"}
            
            # ลองอ่านไฟล์ดู
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if not first_line.strip():
                        return {"success": False, "message": "ไฟล์ว่างเปล่า"}
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        first_line = f.readline()
                except UnicodeDecodeError:
                    return {"success": False, "message": "ไฟล์มีปัญหาเรื่อง encoding กรุณาบันทึกเป็น UTF-8"}
            
            # ตรวจสอบเนื้อหารายละเอียด
            content_check = validate_csv_content(file_path)
            if not content_check["success"]:
                return content_check
            
            return {"success": True, "message": "ไฟล์ผ่านการตรวจสอบเบื้องต้น"}
            
        except PermissionError:
            return {"success": False, "message": "ไม่สามารถเข้าถึงไฟล์ได้ ไฟล์อาจถูกเปิดอยู่ในโปรแกรมอื่น"}
        except Exception as e:
            return {"success": False, "message": f"เกิดข้อผิดพลาดในการตรวจสอบไฟล์: {str(e)[:100]}"}

    def handle_file_pick(e):
        nonlocal selected_file_path
        if e.files:
            selected_file_path = e.files[0].path
            selected_file_text.value = f"เลือกไฟล์: {e.files[0].name}"
            selected_file_text.color = Black
            
            # ตรวจสอบไฟล์เบื้องต้นก่อน
            validation_result = validate_csv_basic(selected_file_path)
            if validation_result["success"]:
                # ไฟล์ผ่านการตรวจสอบเบื้องต้น ดำเนินการวิเคราะห์ต่อ
                update_ring_notification()
            else:
                # ไฟล์มีปัญหา แสดง error notification
                create_error_notification(validation_result["message"])
        else:
            selected_file_path = None
            selected_file_text.value = "ยังไม่ได้เลือกไฟล์"
            selected_file_text.color = Grey
            # ซ่อน ring notification เมื่อไม่มีไฟล์
            ring_notification_container.visible = False
            ring_notification_container.update()
        selected_file_text.update()

    def show_result(message, type="info"):
        """แสดงผลลัพธ์"""
        colors = {
            "success": ft.Colors.GREEN,
            "error": ft.Colors.RED,
            "warning": ft.Colors.ORANGE,
            "info": ft.Colors.BLUE,
        }
        result_container.content.value = message
        result_container.content.color = colors.get(type, ft.Colors.BLUE)
        result_container.content.visible = True
        result_container.bgcolor = ft.Colors.with_opacity(0.1, colors.get(type, ft.Colors.BLUE))
        result_container.visible = True
        result_container.update()

    def show_result(message, type="info"):
        """แสดงผลลัพธ์"""
        colors = {
            "success": ft.Colors.GREEN,
            "error": ft.Colors.RED,
            "warning": ft.Colors.ORANGE,
            "info": ft.Colors.BLUE,
        }
        result_container.content.value = message
        result_container.content.color = colors.get(type, ft.Colors.BLUE)
        result_container.content.visible = True
        result_container.bgcolor = ft.Colors.with_opacity(0.1, colors.get(type, ft.Colors.BLUE))
        result_container.visible = True
        result_container.update()
    
    def start_import_process():
        """ฟังก์ชันนำเข้าข้อมูล"""

        if not selected_file_path:
            show_result("กรุณาเลือกไฟล์ CSV ก่อน", "error")
            return

        # ตรวจสอบไฟล์อีกครั้งก่อนนำเข้า
        validation_result = validate_csv_basic(selected_file_path)
        if not validation_result["success"]:
            show_result(f"ไฟล์มีปัญหา: {validation_result['message']}", "error")
            return

        farms = get_all_farm()
        if not farms:
            show_result("ไม่พบข้อมูลฟาร์ม", "error")
            return
        
        farm_id = farms[0]["farm_id"]

        try:
            show_result("กำลังนำเข้าข้อมูล...", "info")
            result = import_rat_from_csv(selected_file_path)

            if result["success"]:
                show_result(result["message"], "success")
            else:
                # ปรับปรุงข้อความ error ให้เข้าใจง่ายขึ้น
                error_msg = result["message"]
                if "column" in error_msg.lower():
                    show_result("ไฟล์ CSV ขาด column ที่จำเป็น กรุณาตรวจสอบรูปแบบไฟล์", "error")
                elif "date" in error_msg.lower():
                    show_result("รูปแบบวันที่ไม่ถูกต้อง กรุณาใช้รูปแบบ YYYY-MM-DD", "error")
                elif "gender" in error_msg.lower():
                    show_result("ข้อมูลเพศไม่ถูกต้อง กรุณาใช้ 'male' หรือ 'female'", "error")
                else:
                    show_result(f"เกิดข้อผิดพลาดในการนำเข้า: {error_msg}", "error")

        except FileNotFoundError:
            show_result("ไม่พบไฟล์ที่เลือก กรุณาเลือกไฟล์ใหม่", "error")
        except PermissionError:
            show_result("ไม่สามารถเข้าถึงไฟล์ได้ กรุณาปิดไฟล์ในโปรแกรมอื่นแล้วลองใหม่", "error")
        except UnicodeDecodeError:
            show_result("ไฟล์มีปัญหาเรื่อง encoding กรุณาบันทึกไฟล์เป็น UTF-8", "error")
        except Exception as e:
            error_str = str(e)
            if "pandas" in error_str.lower():
                show_result("ไฟล์ CSV มีรูปแบบที่ไม่ถูกต้อง กรุณาตรวจสอบไฟล์", "error")
            elif "memory" in error_str.lower():
                show_result("ไฟล์มีขนาดใหญ่เกินไป กรุณาแบ่งไฟล์เป็นชิ้นเล็กลง", "error")
            else:
                show_result(f"เกิดข้อผิดพลาด: {error_str[:150]}{'...' if len(error_str) > 150 else ''}", "error")

    def create_error_notification(error_message):
        """สร้าง error notification (ใช้ UI เดิม แค่เปลี่ยนเนื้อหา)"""
        ring_notification_container.content = ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ERROR, size=15, color=ft.Colors.RED),
                    ft.Container(
                        content=ft.Text(
                            f"❌ ไฟล์มีปัญหา: {error_message}",
                            size=13,
                            color=ft.Colors.RED,
                        ),
                    ),
                ]),
            ),
        ])
        ring_notification_container.visible = True
        ring_notification_container.update()

    def update_ring_notification():
        """อัปเดต ring notification เมื่อมีการเลือกไฟล์ (ปรับปรุง error handling)"""
        if not selected_file_path:
            ring_notification_container.visible = False
            ring_notification_container.update()
            return
            
        try:
            # ใช้ไฟล์ที่เลือกแทนที่จะใช้ hardcoded filename
            result = analyze_csv_for_ring_changes(selected_file_path)
            
            # ตรวจสอบว่าฟังก์ชันส่งผลลัพธ์อย่างไร
            if isinstance(result, dict) and not result.get("success", True):
                create_error_notification(result.get("message", "ไม่สามารถวิเคราะห์ไฟล์ได้"))
                return
                
            ring_changes_data = result["details"]["ring_changes"]
            
            if ring_changes_data:
                ring_notification_container.content = create_ring_notification_content(ring_changes_data)
                ring_notification_container.visible = True
            else:
                ring_notification_container.visible = False
                
        except KeyError as e:
            if "details" in str(e):
                create_error_notification("ไฟล์ CSV ไม่มีข้อมูลที่ต้องการ")
            else:
                create_error_notification(f"ข้อมูลในไฟล์ไม่ครบถ้วน: {str(e)}")
        except FileNotFoundError:
            create_error_notification("ไม่พบไฟล์ที่เลือก")
        except PermissionError:
            create_error_notification("ไม่สามารถเข้าถึงไฟล์ได้")
        except UnicodeDecodeError:
            create_error_notification("ไฟล์มีปัญหาเรื่อง encoding")
        except Exception as e:
            error_str = str(e)
            if "column" in error_str.lower():
                create_error_notification("ไฟล์ขาด column ที่จำเป็น")
            elif "pandas" in error_str.lower():
                create_error_notification("รูปแบบไฟล์ไม่ถูกต้อง")
            elif "date" in error_str.lower():
                create_error_notification("รูปแบบวันที่ไม่ถูกต้อง")
            else:
                create_error_notification(f"ไม่สามารถวิเคราะห์ไฟล์ได้: {error_str[:100]}")
            
        ring_notification_container.update()

    def create_ring_notification_content(ring_changes_data):
        """สร้างเนื้อหาการแจ้งเตือนการเปลี่ยนห่วงขา (ไม่แก้ไข UI)"""
        if not ring_changes_data:
            return ft.Container()

        # สร้างรายการการเปลี่ยนแปลง
        change_cards = []
        for change in ring_changes_data:
            # รองรับทั้งรูปแบบเก่าและใหม่
            rat_id = change.get('rat_id', 'ไม่ระบุ')
            original_ring = change.get('original_ring')
            new_ring = change.get('new_ring')
            reason = change.get('reason', '')
            action = change.get('action', '')
            row_num = change.get('row', '')
            
            # สร้างข้อความแสดงผล
            if new_ring is None:
                # กรณียกเลิกการใส่ห่วงขา
                if original_ring is None:
                    change_text = f"หนู {rat_id}: ยกเลิกการใส่ห่วงขา ({reason})"
                else:
                    change_text = f"หนู {rat_id}: ยกเลิกห่วงขา {original_ring} ({reason})"
                icon_name = ft.Icons.CANCEL
                color = ft.Colors.RED
                bg_color = ft.Colors.RED_50
            else:
                # กรณีเปลี่ยนหมายเลขห่วงขา
                if original_ring is None:
                    change_text = f"หนู {original_ring}: กำหนดห่วงขา {new_ring}"
                else:
                    change_text = f"หนู {original_ring}: เปลี่ยนห่วงขาเป็น {new_ring}"
                
                
                icon_name = ft.Icons.SYNC
                color = ft.Colors.ORANGE
                bg_color = ft.Colors.ORANGE_50
            
            # เพิ่มหมายเลขแถวถ้ามี
            if row_num:
                change_text = f"แถว {row_num - 1}: {change_text}"
            
            change_cards.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Container(
                                    content=ft.Text(
                                        change_text, 
                                        size=12, 
                                        color=color, 
                                        weight=ft.FontWeight.W_500,
                                    )
                                ),
                            ]),
                        ]),
                        padding=5,
                        border_radius=2,
                        bgcolor=bg_color,
                        expand=True,
                    ),
                )
            )

        # สร้าง summary message
        total_changes = len(ring_changes_data)
        success_changes = len([c for c in ring_changes_data if c.get('new_ring') is not None])
        cancelled_changes = total_changes - success_changes
        
        summary_text = f"มีการเปลี่ยนแปลง {total_changes} รายการ"
        if cancelled_changes > 0:
            summary_text += f" (เปลี่ยนแปลง {success_changes} รายการ, ยกเลิก {cancelled_changes} รายการ)"

        # ส่งคืน UI content (ไม่เปลี่ยนแปลง UI)
        return ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.WARNING, size=15, color=ft.Colors.ORANGE),
                    ft.Container(
                        content=ft.Text(
                            f"แจ้งเตือน: {summary_text}",
                            size=13,
                            color=ft.Colors.ORANGE,
                        ),
                    ),
                ]),
            ),
            ft.Container(
                content=ft.Column(change_cards, scroll=ft.ScrollMode.AUTO),
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=8,
                padding=5,
            ),
        ])
    
    def cancel_import():
        """ยกเลิกการนำเข้าและล้าง error ทั้งหมด"""
        nonlocal selected_file_path
        
        # ซ่อน result container
        result_container.visible = False
        result_container.update()
        
        # รีเซ็ตการเลือกไฟล์
        selected_file_path = None
        selected_file_text.value = "ยังไม่ได้เลือกไฟล์"
        selected_file_text.color = Grey
        selected_file_text.update()
        
        # ซ่อน ring notification
        ring_notification_container.visible = False
        ring_notification_container.update()
        
        # กลับไปหน้าหลัก
        switch_to_main()

    def cancel_export():
        """ยกเลิกการส่งออกและล้าง error ทั้งหมด"""
        # ซ่อน result container
        result_container.visible = False
        result_container.update()
        
        # กลับไปหน้าหลัก
        switch_to_main()

    def build_import_section():
        """ส่วนนำเข้าข้อมูล"""
        farms = get_all_farm()
        farm_options = [
            ft.dropdown.Option(str(farm["farm_id"]), farm["farm_name"])
            for farm in farms
        ]

        farm_dropdown = ft.Dropdown(
            label="เลือกฟาร์มที่จะนำเข้าข้อมูล",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            text_style=text_style,
            label_style=text_style,
            options=farm_options,
            value=str(farms[0]["farm_id"]) if farms else None,
            content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        )

        def pick_file(e):
            file_picker.pick_files(
                dialog_title="เลือกไฟล์ CSV",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["csv"],
            )

        return ft.ResponsiveRow([
            ft.Container(
                content=ft.Column([
                    ft.Text("นำเข้าข้อมูลหนู", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("เลือกไฟล์ CSV", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton(
                            "เลือกไฟล์",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=pick_file,
                            style=ft.ButtonStyle(bgcolor=Neo_Mint, color=White),
                        ),
                        selected_file_text,
                    ]),
                    ring_notification_container,  # ใช้ container เดิม
                    ft.Container(
                        content=ft.Column([
                            ft.Text("รูปแบบไฟล์ CSV ที่รองรับ:", size=12, weight=ft.FontWeight.BOLD, color=Deep_Purple),
                            ft.Text("• rat_id, father_id, mother_id, birth_date", size=11, color=Grey),
                            ft.Text("• gender, weight, size, breed, status", size=11, color=Grey),
                            ft.Text("• pond_id, has_ring, ring_number, special_traits", size=11, color=Grey),
                            ft.Text("• วันที่ให้ใช้รูปแบบ: YYYY-MM-DD", size=11, color=Grey),
                            ft.Text("• เพศ: male หรือ female", size=11, color=Grey),
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=8,
                        margin=ft.margin.only(top=10, bottom=10),
                    ),
                    ft.Divider(),
                    ft.ResponsiveRow([
                        ft.Container(
                            content=base_button_gradient(
                                button_name="เริ่มนำเข้า",
                                icon="UPLOAD",
                                on_click=lambda e: start_import_process(),
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=base_button_normal(
                                button_name="ยกเลิก",
                                on_click=lambda e: cancel_import(),
                                background_color=White,
                                text_color=Black,
                            ),
                            expand=True,
                        ),
                    ]),
                ], spacing=15),
                padding=20,
                expand=True,
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

    def build_export_section():
        """ส่วนส่งออกข้อมูล"""
        rats = get_all_rat_data()
        rat_options = [
            ft.dropdown.Option(rat["rat_id"], f"{rat['rat_id']} - ห่วงขา {rat.get('ring_number', 'ไม่มี')}")
            for rat in rats
        ]

        export_type_dropdown = ft.Dropdown(
            label="ประเภทการส่งออก",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            text_style=text_style,
            label_style=text_style,
            options=[
                ft.dropdown.Option("all", "ข้อมูลหนูทั้งหมด"),
                ft.dropdown.Option("single", "หนูตัวเดียวและบรรพบุรุษ"),
            ],
            value="all",
            content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        )

        rat_dropdown = ft.Dropdown(
            label="เลือกหนู",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            text_style=text_style,
            label_style=text_style,
            options=rat_options,
            visible=False,
            content_padding=ft.padding.only(left=10, top=5, right=10, bottom=5),
        )

        def on_export_type_change(e):
            rat_dropdown.visible = export_type_dropdown.value == "single"
            rat_dropdown.update()

        export_type_dropdown.on_change = on_export_type_change

        def start_export(e):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if export_type_dropdown.value == "all":
                    filename = f"rats_all_{timestamp}.csv"
                    show_result("กำลังส่งออกข้อมูลหนูทั้งหมด...", "info")
                    result = export_all_rats(filename)
                elif export_type_dropdown.value == "single":
                    if not rat_dropdown.value:
                        show_result("กรุณาเลือกหนูที่ต้องการส่งออก", "error")
                        return
                    filename = f"rat_{rat_dropdown.value}_ancestors_{timestamp}.csv"
                    show_result(f"กำลังส่งออกข้อมูลหนู {rat_dropdown.value} และบรรพบุรุษ...", "info")
                    result = export_rat_with_ancestors(rat_dropdown.value, filename)
                else:
                    show_result("กรุณาเลือกประเภทการส่งออก", "error")
                    return

                if result["success"]:
                    show_result(f"{result['message']}\nไฟล์: {filename}", "success")
                else:
                    show_result(result["message"], "error")
            except Exception as e:
                show_result(f"เกิดข้อผิดพลาด: {str(e)}", "error")

        return ft.ResponsiveRow([
            ft.Container(
                content=ft.Column([
                    ft.Text("ส่งออกข้อมูลหนู", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text("ประเภทการส่งออก", size=14, weight=ft.FontWeight.BOLD),
                    export_type_dropdown,
                    rat_dropdown,
                    ft.Container(
                        content=ft.Column([
                            ft.Text("รูปแบบไฟล์ที่ส่งออก:", size=12, weight=ft.FontWeight.BOLD, color=Deep_Purple),
                            ft.Text("• ไฟล์ CSV พร้อม UTF-8 BOM encoding", size=11, color=Grey),
                            ft.Text("• สามารถเปิดด้วย Excel ได้ทันที", size=11, color=Grey),
                            ft.Text("• รวมข้อมูลครบถ้วนทุกฟิลด์", size=11, color=Grey),
                        ]),
                        padding=10,
                        bgcolor=ft.Colors.GREEN_50,
                        border_radius=8,
                        margin=ft.margin.only(top=10, bottom=10),
                    ),
                    ft.Divider(),
                    ft.ResponsiveRow([
                        ft.Container(
                            content=base_button_gradient(
                                button_name="เริ่มส่งออก",
                                icon="DOWNLOAD",
                                on_click=start_export,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=base_button_normal(
                                button_name="ยกเลิก",
                                on_click=lambda e: cancel_export(),
                                background_color=White,
                                text_color=Black,
                            ),
                            expand=True,
                        ),
                    ]),
                ], spacing=15),
                padding=20,
                expand=True,
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

    def build_history_section():
        """ส่วนประวัติการนำเข้า/ส่งออก"""
        export_records = get_export_history()
        import_records = get_import_history()

        def create_export_cards():
            if not export_records:
                return [ft.Container(
                    content=ft.Text("ไม่มีประวัติการส่งออก", color=Grey, size=14),
                    alignment=ft.alignment.center,
                    height=100,
                )]

            cards = []
            for record in export_records[:10]:
                status_color = ft.Colors.GREEN if record["status"] == "success" else ft.Colors.RED
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("ส่งออกข้อมูล", size=13, weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text(record["status"], size=10, color=status_color),
                                    bgcolor=ft.Colors.with_opacity(0.1, status_color),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12,
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"ไฟล์: {record['file_name']}", size=12, color=Grey),
                            ft.Text(f"วันที่: {record.get('export_date', record.get('created_at', 'ไม่ระบุ'))}", size=11, color=Grey),
                            ft.Text(f"หมายเหตุ: {record.get('note', 'ไม่มี')}", size=11, color=Grey, max_lines=2),
                        ]),
                        padding=15,
                    ),
                    margin=ft.margin.only(bottom=10),
                )
                cards.append(card)
            return cards

        def create_import_cards():
            if not import_records:
                return [ft.Container(
                    content=ft.Text("ไม่มีประวัติการนำเข้า", color=Grey, size=14),
                    alignment=ft.alignment.center,
                    height=100,
                )]

            cards = []
            for record in import_records[:10]:
                status_color = ft.Colors.GREEN if record["status"] == "success" else ft.Colors.RED
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("นำเข้าข้อมูล", size=13, weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text(record["status"], size=10, color=status_color),
                                    bgcolor=ft.Colors.with_opacity(0.1, status_color),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=12,
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"ไฟล์: {record['file_name']}", size=12, color=Grey),
                            ft.Text(f"วันที่: {record.get('import_date', record.get('created_at', 'ไม่ระบุ'))}", size=11, color=Grey),
                            ft.Text("สำเร็จ", size=11, color=ft.Colors.GREEN) if not record.get("error_message")
                            else ft.Text(f"ข้อผิดพลาด: {record.get('error_message', '')[:100]}{'...' if len(record.get('error_message', '')) > 100 else ''}", 
                                       size=11, color=Grey, max_lines=2),
                        ]),
                        padding=15,
                    ),
                    margin=ft.margin.only(bottom=10),
                )
                cards.append(card)
            return cards

        return ft.ResponsiveRow([
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("ประวัติการนำเข้า/ส่งออก", size=18, weight=ft.FontWeight.BOLD),
                    ]),
                    ft.Divider(),
                    ft.Text("ประวัติการส่งออก", size=16, weight=ft.FontWeight.BOLD, color=Black),
                    ft.Column(create_export_cards()),
                    base_empty_box(20),
                    ft.Text("ประวัติการนำเข้า", size=16, weight=ft.FontWeight.BOLD, color=Black),
                    ft.Column(create_import_cards()),
                ]),
                padding=20, 
                expand=True,
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

    def build_main_content():
        """เนื้อหาหลัก"""
        def go_to_import(e):
            nonlocal current_view
            current_view = "import"
            refresh_view()

        def go_to_export(e):
            nonlocal current_view
            current_view = "export"
            refresh_view()

        def go_to_history(e):
            nonlocal current_view
            current_view = "history"
            refresh_view()

        try:
            export_records = get_export_history()
            import_records = get_import_history()
        except:
            export_records = []
            import_records = []

        return ft.Column([
            ft.Container(
                content=ft.Text("จัดการนำเข้า/ส่งออกข้อมูล", size=20, weight=ft.FontWeight.BOLD, color=Black),
                margin=ft.margin.only(bottom=20),
            ),
            ft.ResponsiveRow([
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.UPLOAD, size=50, color=Deep_Purple),
                                ft.Text("นำเข้าข้อมูล", size=16, weight=ft.FontWeight.BOLD, color=Black),
                                ft.Text("นำเข้าข้อมูลหนูจากไฟล์ CSV", size=12, color=Grey),
                                base_empty_box(10),
                                ft.ElevatedButton(
                                    "เริ่มนำเข้า",
                                    style=ft.ButtonStyle(bgcolor=Deep_Purple, color=White),
                                    on_click=go_to_import,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=30,
                            alignment=ft.alignment.center,
                        ),
                        elevation=2,
                    ),
                    col={"xs": 12, "sm": 6, "md": 4},
                ),
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.DOWNLOAD, size=50, color=Neo_Mint),
                                ft.Text("ส่งออกข้อมูล", size=16, weight=ft.FontWeight.BOLD, color=Black),
                                ft.Text("ส่งออกข้อมูลหนูเป็นไฟล์ CSV", size=12, color=Grey),
                                base_empty_box(10),
                                ft.ElevatedButton(
                                    "เริ่มส่งออก",
                                    style=ft.ButtonStyle(bgcolor=Neo_Mint, color=White),
                                    on_click=go_to_export,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=30,
                            alignment=ft.alignment.center,
                        ),
                        elevation=2,
                    ),
                    col={"xs": 12, "sm": 6, "md": 4},
                ),
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.HISTORY, size=50, color=ft.Colors.ORANGE),
                                ft.Text("ประวัติ", size=16, weight=ft.FontWeight.BOLD, color=Black),
                                ft.Text("ดูประวัติการนำเข้า/ส่งออก", size=12, color=Grey),
                                base_empty_box(10),
                                ft.ElevatedButton(
                                    "ดูประวัติ",
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.ORANGE, color=White),
                                    on_click=go_to_history,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=30,
                            alignment=ft.alignment.center,
                        ),
                        elevation=2,
                    ),
                    col={"xs": 12, "sm": 6, "md": 4},
                ),
            ], run_spacing=20),
            base_empty_box(30),
            ft.Container(
                content=ft.Column([
                    ft.Text("สถิติโดยรวม", size=16, weight=ft.FontWeight.BOLD, color=Black),
                    ft.ResponsiveRow([
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("การส่งออกล่าสุด", size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"{len(export_records)} รายการ", size=20, weight=ft.FontWeight.BOLD, color=Neo_Mint),
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=20,
                                ),
                                elevation=1,
                            ),
                            col={"xs": 12, "sm": 6, "md": 3},
                        ),
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.Text("การนำเข้าล่าสุด", size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"{len(import_records)} รายการ", size=20, weight=ft.FontWeight.BOLD, color=Deep_Purple),
                                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                    padding=20,
                                ),
                                elevation=1,
                            ),
                            col={"xs": 12, "sm": 6, "md": 3},
                        ),
                    ]),
                ]),
                margin=ft.margin.only(top=20),
            ),
        ])

    def switch_to_main():
        """กลับไปหน้าหลัก"""
        nonlocal current_view
        current_view = "main"
        result_container.visible = False
        # รีเซ็ตการเลือกไฟล์และซ่อน ring notification เมื่อกลับหน้าหลัก
        nonlocal selected_file_path
        selected_file_path = None
        selected_file_text.value = "ยังไม่ได้เลือกไฟล์"
        selected_file_text.color = Grey
        ring_notification_container.visible = False
        refresh_view()

    def refresh_view():
        """รีเฟรชหน้าจอ"""
        if current_view == "main":
            list_view.controls = [build_main_content()]
        elif current_view == "import":
            list_view.controls = [build_import_section()]
        elif current_view == "export":
            list_view.controls = [build_export_section()]
        elif current_view == "history":
            list_view.controls = [build_history_section()]

        list_view.update()

    # สร้าง ListView หลัก
    list_view = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.padding.only(top=20, bottom=20, left=5, right=5),
        controls=[build_main_content()],
    )

    # สร้าง Column ที่รวม FilePicker และ ListView
    main_column = ft.Column(
        [
            file_picker,
            result_container,
            ft.Container(content=list_view, expand=True),
        ],
        expand=True,
    )

    return main_column