import flet as ft

def create_navigation_drawer(page: ft.Page) -> ft.NavigationDrawer:

    def update_nav(e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            page.go("/0")
        elif selected_index == 1:
            page.go("/1")
        elif selected_index == 2:
            page.go("/2")
        elif selected_index == 3:
            page.go("/settings")
        page.close(e.control)

    navigation_drawer = ft.NavigationDrawer(
        on_change=update_nav,
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.HOME,
                selected_icon=ft.Icons.HOME_FILLED,
                label="Головна",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.BOOKMARK_BORDER,
                selected_icon=ft.Icons.BOOKMARK,
                label="Сторінки",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SCHOOL,
                selected_icon=ft.Icons.SCHOOL,
                label="Випускники",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.SETTINGS,
                selected_icon=ft.Icons.SETTINGS,
                label="Налаштування",
            ),
        ],
    )
    return navigation_drawer