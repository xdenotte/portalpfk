import flet as ft
from settings import settings_page
from settings_utils import load_settings
from parser import fetch_news, fetch_schedule_links, fetch_rating_links, fetch_pdf_links
from home import home_page
from greetings import get_greeting
from navbar import create_navigation_drawer
from pages import pages_page
from fordiplom import fordiplom

greeting_container: ft.Text = None
navigation_drawer: ft.NavigationDrawer = None
page_content_container: ft.Container = None

async def main(page: ft.Page) -> None:
    global page_content_container, greeting_container, navigation_drawer

    page.title = "Портал ВСП ПФК НУК"

    page.extend_body = True
    page.padding = 0

    theme_mode = load_settings().get("theme_mode", "Системна")
    page.theme_mode = {
        "Системна": ft.ThemeMode.SYSTEM,
        "Темна": ft.ThemeMode.DARK,
        "Світла": ft.ThemeMode.LIGHT
    }.get(theme_mode, ft.ThemeMode.SYSTEM)

    navigation_drawer = create_navigation_drawer(page)
    page.drawer = navigation_drawer

    greeting_container = ft.Text(get_greeting(), size=32, visible=False)

    page_content_container = ft.Container(
        expand=True,
        padding=ft.Padding(left=10, right=10, top=0, bottom=0)
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
        except Exception:
            pass

        page_content_container.content = ft.Column(
            [ft.ProgressRing()],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        page.update()

        header_controls = [
            ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=open_drawer_clicked,
                icon_size=24, 
                tooltip="Відкрити меню"
            )
        ]

        titles = {
            "/0": "Головна",
            "/1": "Сторінки",
            "/2": "Випускники",
            "/settings": "Налаштування"
        }
        current_page_title = titles.get(route, "Невідома сторінка")
        header_controls.append(ft.Text(current_page_title, size=24, weight=ft.FontWeight.BOLD))

        page_header = ft.Row(
            controls=header_controls,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )

        page_content_wrapper = ft.Column(expand=True, spacing=0)
        page_content_wrapper.controls.append(page_header)
        page_content_wrapper.controls.append(ft.Divider())

        if route == "/0":
            greeting_container.visible = True
            page_content_wrapper.controls.append(greeting_container)
            page_content_wrapper.controls.append(home_page(page, fetch_news))
        elif route == "/1":
            greeting_container.visible = False
            page_content_wrapper.controls.append(await pages_page(page, fetch_schedule_links, fetch_rating_links, fetch_pdf_links))
        elif route == "/2":
            greeting_container.visible = False
            page_content_wrapper.controls.append(fordiplom(page))
        elif route == "/settings":
            greeting_container.visible = False
            page_content_wrapper.controls.append(settings_page(page))
        else:
            greeting_container.visible = False
            page_content_wrapper.controls.append(ft.Text("Сторінки не існує", size=20, color="red"))
        
        page_content_container.content = page_content_wrapper
        page.update()

    async def route_change(e):
        await load_page(page.route)

    page.on_route_change = route_change
    
    await page.push_route("/0")

ft.run(main)