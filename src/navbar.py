import flet as ft

def update_nav(page, index):
    if index == 0:
        page.go("/0")
    elif index == 1:
        page.go("/1")
    elif index == 2:
        page.go("/2")
    elif index == 3:
        page.go("/settings")

def create_nav_bar(page: ft.Page) -> ft.NavigationBar:
    nav_bottom_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Головна"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOKMARK_BORDER, label="Сторінки", selected_icon=ft.Icons.BOOKMARK),
            ft.NavigationBarDestination(icon=ft.Icons.SCHOOL, label="Випускники"), 
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Налаштування"),
        ],
        selected_index=0,
        on_change=lambda e: update_nav(page, e.control.selected_index),
    )
    return nav_bottom_bar
