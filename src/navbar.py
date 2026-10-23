import flet as ft

# (маршрут, підпис, іконка, іконка у вибраному стані)
DESTINATIONS = (
    ("/0", "Головна", ft.Icons.HOME, ft.Icons.HOME_FILLED),
    ("/1", "Сторінки", ft.Icons.BOOKMARK_BORDER, ft.Icons.BOOKMARK),
    ("/2", "Випускники", ft.Icons.SCHOOL, ft.Icons.SCHOOL),
    ("/settings", "Налаштування", ft.Icons.SETTINGS, ft.Icons.SETTINGS),
)

ROUTES = tuple(route for route, *_ in DESTINATIONS)


def create_navigation_drawer(page: ft.Page) -> ft.NavigationDrawer:
    async def on_change(e) -> None:
        index = e.control.selected_index
        if index is not None and 0 <= index < len(ROUTES):
            await page.push_route(ROUTES[index])

        await page.close_drawer()

    return ft.NavigationDrawer(
        on_change=on_change,
        controls=[
            ft.Container(height=12),
            *(
                ft.NavigationDrawerDestination(
                    icon=icon,
                    selected_icon=selected_icon,
                    label=label,
                )
                for _, label, icon, selected_icon in DESTINATIONS
            ),
        ],
    )
