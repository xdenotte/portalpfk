import flet as ft

from fordiplom import fordiplom
from home import home_page
from navbar import create_navigation_drawer
from pages import pages_page
from parser import fetch_news, fetch_pdf_links, fetch_rating_links, fetch_schedule_links
from settings import settings_page
from settings_utils import load_settings
from theme import THEME_MAP

PAGE_TITLES = {
    "/0": "Головна",
    "/1": "Сторінки",
    "/2": "Випускники",
    "/settings": "Налаштування",
}


async def main(page: ft.Page) -> None:
    page.title = "Портал ВСП ПФК НУК"
    page.padding = 0

    theme_name = load_settings().get("theme_mode", "Системна")
    page.theme_mode = THEME_MAP.get(theme_name, ft.ThemeMode.SYSTEM)

    page.drawer = create_navigation_drawer(page)

    page_content_container = ft.Container(
        expand=True,
        padding=ft.Padding(left=10, right=10, top=0, bottom=0),
    )

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[page_content_container],
                expand=True,
                spacing=0,
            ),
            expand=True,
        )
    )

    async def open_drawer_clicked(e):
        await page.show_drawer()

    async def load_page(route: str) -> None:
        try:
            await page.close_drawer()
        except RuntimeError as e:
            print(f"[WARN] Не вдалося закрити меню: {e}")

        page_content_container.content = ft.Column(
            [ft.ProgressRing()],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        page.update()

        page_header = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.MENU,
                    on_click=open_drawer_clicked,
                    icon_size=24,
                    tooltip="Відкрити меню",
                ),
                ft.Text(
                    PAGE_TITLES.get(route, "Невідома сторінка"),
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )

        wrapper = ft.Column(expand=True, spacing=0)
        wrapper.controls.extend([page_header, ft.Divider()])

        if route == "/0":
            wrapper.controls.append(home_page(page, fetch_news))
        elif route == "/1":
            wrapper.controls.append(
                await pages_page(page, fetch_schedule_links, fetch_rating_links, fetch_pdf_links)
            )
        elif route == "/2":
            wrapper.controls.append(fordiplom(page))
        elif route == "/settings":
            wrapper.controls.append(settings_page(page))
        else:
            wrapper.controls.append(ft.Text("Сторінки не існує", size=20, color="red"))

        page_content_container.content = wrapper
        page.update()

    async def route_change(e):
        await load_page(page.route)

    page.on_route_change = route_change

    await page.push_route("/0")


ft.run(main)
