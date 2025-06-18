import flet as ft
from settings import settings_page
from settings_utils import load_settings
from parser import fetch_news, fetch_schedule_links, fetch_rating_links, fetch_pdf_links
from home import home_page
from greetings import get_greeting
from navbar import create_nav_bar
from pages import pages_page
from fordiplom import fordiplom

greeting_container: ft.Text = None
nav_bar: ft.NavigationBar = None
page_content_container: ft.Container = None

def main(page: ft.Page) -> None:
    global page_content_container, greeting_container, nav_bar

    page.title = "Портал ВСП ПФК НУК"
    page.fonts = {
        "Noto Color Emoji": "fonts/NotoColorEmoji.ttf",
        "San Francisco Bold": "fonts/San Francisco Bold.ttf",
        "Open Sans": "/fonts/OpenSans.ttf"
    }

    page.extend_body = False
    page.padding = 0

    # Завантаження налаштувань теми
    theme_mode = load_settings().get("theme_mode", "Системна")
    page.theme_mode = {
        "Системна": ft.ThemeMode.SYSTEM,
        "Темна": ft.ThemeMode.DARK,
        "Світла": ft.ThemeMode.LIGHT
    }.get(theme_mode, ft.ThemeMode.SYSTEM)

    # Нижня навігація
    nav_bar = create_nav_bar(page)
    page.navigation_bar = nav_bar

    # Привітання
    greeting_container = ft.Text(get_greeting(), size=32, visible=False)

    # Контейнер з відступами для основного контенту
    page_content_container = ft.Container(
        expand=True,
        padding=ft.padding.only(left=10, right=10, top=10)  # Відступи
    )

    # Основний вміст
    main_content_column = ft.Column(
        controls=[greeting_container, page_content_container],
        expand=True,
        spacing=0,
    )

    # Обгортка в SafeArea
    page.add(
        ft.SafeArea(
            content=main_content_column,
            expand=True,
        )
    )

    async def load_page(route: str) -> None:
        nav_bar.selected_index = {"0": 0, "1": 1, "2": 2, "settings": 3}.get(route.strip("/"), None)
        greeting_container.visible = route == "/0"

        # Показати індикатор завантаження
        page_content_container.content = ft.Column(
            [ft.ProgressRing()],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        page.update()

        # Завантажити вміст сторінки
        if route == "/0":
            page_content = home_page(page, fetch_news)
        elif route == "/1":
            page_content = await pages_page(page, fetch_schedule_links, fetch_rating_links, fetch_pdf_links)
        elif route == "/2":
            page_content = fordiplom(page)
        elif route == "/settings":
            page_content = settings_page(page)
        else:
            page_content = ft.Column(
                [ft.Text("Сторінки не існує", size=20, color="red")],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

        # Оновити контент
        page_content_container.content = page_content
        page.update()

    async def route_change(e):
        await load_page(page.route)

    page.on_route_change = route_change
    page.go("/0")

ft.app(target=main)
