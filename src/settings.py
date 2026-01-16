import flet as ft
from settings_utils import load_settings, save_settings

async def change_theme(e, page: ft.Page):
    choice = e.control.value
    print(f"Обрана тема: {choice}") 
    
    theme_map = {
        "Системна": ft.ThemeMode.SYSTEM,
        "Темна": ft.ThemeMode.DARK,
        "Світла": ft.ThemeMode.LIGHT
    }
    
    page.theme_mode = theme_map.get(choice, ft.ThemeMode.SYSTEM)
    settings = load_settings()
    settings["theme_mode"] = choice
    save_settings(settings)
    
    page.update()

def settings_page(page: ft.Page):
    settings = load_settings()
    current_theme = settings.get("theme_mode", "Системна")

    theme_selector = ft.Dropdown(
        label="Тема оформлення",
        options=[
            ft.dropdown.Option("Системна"),
            ft.dropdown.Option("Темна"),
            ft.dropdown.Option("Світла"),
        ],
        value=current_theme,
        width=300,
        # Використовуємо вашу подію on_text_change
        on_text_change=lambda e: page.run_task(change_theme, e, page)
    )

    about_tile = ft.ExpansionTile(
         title=ft.Text("Про програму", weight=ft.FontWeight.BOLD),
         subtitle=ft.Text("Версія, автор, посилання"),
         leading=ft.Icon(ft.Icons.INFO_OUTLINE),
         controls=[
             ft.ListTile(
                 title=ft.Text("Версія програми"),
                 subtitle=ft.Text("1.1.0"),
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
                 on_click=lambda e: page.run_task(ft.UrlLauncher().launch_url, "https://github.com/xdenotte"),
             )
         ]
    )

    return ft.Column(
        controls=[
            ft.Container(height=10),
            theme_selector,
            ft.Container(height=10),
            about_tile,
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )