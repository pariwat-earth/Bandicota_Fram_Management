import flet as ft

from pages.sturcture_screen import structure_screen


def main(page: ft.Page):
    page.fonts = {
        "Sarabun": "https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;700&display=swap"
    }

    page.theme = ft.Theme(font_family="Sarabun")

    page.padding = 0
    page.margin = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    page.add(
        ft.SafeArea(
            ft.Container(
                structure_screen(),
                alignment=ft.alignment.center,
            ),
            expand=True,
        )
    )


ft.app(main)
