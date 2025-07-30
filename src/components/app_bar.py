import flet as ft

from storages.general_information import get_managername
from styles.colors import Deep_Purple, Neo_Mint

def base_appbar(title_name="หนูพุกใหญ่พรหมพิราม"):
    gradient_container = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=[Neo_Mint, Deep_Purple],
        ),
        width=None,
        height=100,
        border_radius=0,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text(
                    title_name,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    f"ยินดีต้อนรับ คุณ{get_managername().split()[0]}",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
            ],
            # alignment=ft.MainAxisAlignment.START,
            # vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    return gradient_container