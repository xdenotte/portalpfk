import flet as ft

def create_navigation_drawer(page: ft.Page) -> ft.NavigationDrawer:

    # 1. Робимо функцію асинхронною
    async def update_nav(e):
        selected_index = e.control.selected_index
        
        # Визначаємо маршрут на основі індексу
        routes = {
            0: "/0",
            1: "/1",
            2: "/2",
            3: "/settings"
        }
        
        target_route = routes.get(selected_index)
        
        if target_route:
            # 2. Використовуємо push_route замість go
            await page.push_route(target_route)
            
        # 3. Закриваємо Drawer асинхронно через метод сторінки
        try:
            await page.close_drawer()
        except Exception:
            # Якщо метод не підтримується, використовуємо властивість
            e.control.open = False
            page.update()

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