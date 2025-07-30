import flet as ft

from styles.colors import Black, Deep_Purple, Neo_Mint, White


def base_button_gradient(
    button_name: str = "gradient_button",
    icon: str = None,
    on_click=None,
):

    base_button = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=[Neo_Mint, Deep_Purple],
        ),
        border_radius=10,
        padding=10,
        margin=ft.margin.only(left=5, right=5),
        width=None,
        ink=True,
        on_click=on_click,
        content=ft.Row(
            [
                ft.Icon(icon, color=ft.Colors.WHITE) if icon else ft.Container(width=0),
                ft.Text(
                    button_name,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        ),
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=4,
            color=ft.Colors.GREY,
            offset=ft.Offset(0, 1),
        ),
    )

    return base_button


def base_button_gradient_v2(
    button_name: str = "gradient_button",
    icon: str = None,
    on_click=None,
):

    base_button = ft.Container(
        gradient=ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=[Neo_Mint, Deep_Purple],
        ),
        border_radius=ft.border_radius.only(
            top_left=0, top_right=0, bottom_left=10, bottom_right=10
        ),
        padding=10,
        margin=ft.margin.only(left=0, right=0),
        width=None,
        ink=True,
        on_click=on_click,
        content=ft.Row(
            [
                ft.Icon(icon, color=ft.Colors.WHITE) if icon else ft.Container(width=0),
                ft.Text(
                    button_name,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        ),
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=4,
            color=ft.Colors.GREY,
            offset=ft.Offset(0, 1),
        ),
    )

    return base_button


def base_button_normal(
    button_name: str = "normal_button",
    icon: str = None,
    on_click=None,
    background_color=None,
    text_color=None,
    icon_color=None,
):

    if background_color is None:
        background_color = White

    if text_color is None:
        if background_color.lower() in ["#ffffff", "white", ft.Colors.WHITE]:
            text_color = Black
        else:
            text_color = White

    if icon_color is None:
        icon_color = text_color

    base_button = ft.Container(
        bgcolor=background_color,
        border_radius=10,
        padding=10,
        margin=ft.margin.only(left=5, right=5),
        width=None,
        ink=True,
        on_click=on_click,
        content=ft.Row(
            [
                ft.Icon(icon, color=icon_color) if icon else ft.Container(width=0),
                ft.Text(
                    button_name,
                    color=text_color,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        ),
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=4,
            color=ft.Colors.GREY,
            offset=ft.Offset(0, 1),
        ),
    )

    return base_button


def base_button_with_icon(
    button_name: str = "normal_button",
    icon: str = None,
    on_click=None,
    background_color=None,
    text_color=None,
    icon_color=None,
    min_height: int = 80,
):
    if background_color is None:
        background_color = White

    if text_color is None:
        if background_color.lower() in ["#ffffff", "white", ft.Colors.WHITE]:
            text_color = Black
        else:
            text_color = White

    if icon_color is None:
        icon_color = text_color

    base_button = ft.Container(
        expand=True,
        bgcolor=background_color,
        border_radius=10,
        padding=10,
        ink=True,
        on_click=on_click,
        height=min_height,
        content=ft.Column(
            [
                ft.Row(
                    [ft.Icon(icon, color=icon_color)] if icon else [],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text(
                    button_name,
                    color=text_color,
                    size=11,
                    text_align=ft.TextAlign.CENTER,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        ),
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=4,
            color=ft.Colors.GREY,
            offset=ft.Offset(0, 1),
        ),
    )

    return base_button


def base_button_normal_v2(
    button_name: str = "normal_button",
    icon: str = None,
    on_click=None,
):

    base_button = ft.Container(
        border_radius=ft.border_radius.only(
            top_left=0, top_right=0, bottom_left=6, bottom_right=6
        ),
        padding=6,
        margin=ft.margin.only(left=0, right=0),
        width=None,
        ink=True,
        on_click=on_click,
        content=ft.Row(
            [
                (
                    ft.Icon(icon, color=ft.Colors.GREY_500, size=13)
                    if icon
                    else ft.Container(
                        width=0,
                    )
                ),
                ft.Text(
                    button_name,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER,
                    size=12,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=White,
        alignment=ft.alignment.center,
        shadow=ft.BoxShadow(
            spread_radius=0.1,
            blur_radius=0.1,
            color=ft.Colors.GREY,
            offset=ft.Offset(0, 0.1),
        ),
    )

    return base_button
