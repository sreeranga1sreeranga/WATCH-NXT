import flet as ft
from config import NETFLIX_RED, TEXT_COLOR

def NetflixRedButton(text, on_click=None, width=None):
    return ft.Container(
        content=ft.Row([ft.Text(text, color=TEXT_COLOR, weight=ft.FontWeight.W_900, size=14)], alignment=ft.MainAxisAlignment.CENTER),
        width=width, height=50, bgcolor=NETFLIX_RED, border_radius=5, on_click=on_click
    )

def NetflixStandardButton(text, icon=None, on_click=None, width=None, primary=True):
    bg = ft.Colors.WHITE if primary else "#303030"
    tc = ft.Colors.BLACK if primary else ft.Colors.WHITE
    content_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=8)
    if icon:
        content_row.controls.append(ft.Icon(icon, color=tc, size=18))
    content_row.controls.append(ft.Text(text, color=tc, weight=ft.FontWeight.BOLD, size=13))
    
    return ft.Container(
        content=content_row, width=width, height=45, bgcolor=bg, border_radius=4, on_click=on_click
    )