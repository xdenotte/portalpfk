import flet as ft

from settings_utils import load_settings, save_settings
from theme import THEME_MAP
from version import APP_VERSION

GITHUB_URL = "https://github.com/xdenotte"


async def change_theme(e, page: ft.Page) -> None:
    choice = e.control.value
    page.theme_mode = THEME_MAP.get(choice, ft.ThemeMode.SYSTEM)

    settings = load_settings()
    settings["theme_mode"] = choice
    save_settings(settings)

    page.update()


def settings_page(page: ft.Page) -> ft.Control:
    current_theme = load_settings().get("theme_mode", "Системна")
    url_launcher = ft.UrlLauncher()

    async def on_theme_change(e) -> None:
        await change_theme(e, page)

    async def open_github(e) -> None:
        await url_launcher.launch_url(GITHUB_URL)

    theme_selector = ft.Dropdown(
        label="Тема оформлення",
        options=[ft.dropdown.Option(name) for name in THEME_MAP],
        value=current_theme,
        width=300,
        on_select=on_theme_change,
    )

    about_items: list = [
        ft.ListTile(
            title=ft.Text("Версія програми"),
            subtitle=ft.Text(APP_VERSION),
            leading=ft.Icon(ft.Icons.BUG_REPORT),
        ),
        ft.ListTile(
            title=ft.Text("Розробник"),
            subtitle=ft.Text("xdenotte"),
            leading=ft.Icon(ft.Icons.PERSON),
        ),
        ft.ListTile(
            title=ft.Text("GitHub"),
            subtitle=ft.Text("github.com/xdenotte"),
            leading=ft.Icon(ft.Icons.CODE),
            on_click=open_github,
        ),
    ]

    about_tile = ft.ExpansionTile(
        title=ft.Text("Про програму", weight=ft.FontWeight.BOLD),
        subtitle=ft.Text("Версія, автор, посилання"),
        leading=ft.Icon(ft.Icons.INFO_OUTLINE),
        controls=about_items,
    )

    return ft.Column(
        controls=[
            ft.Container(height=10),
            theme_selector,
            ft.Container(height=10),
            about_tile,
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )
