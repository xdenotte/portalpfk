import flet as ft
from settings_utils import load_settings, save_settings

# Функція для зміни теми
def change_theme(e, page):
     choice = e.control.value
     if choice == "Системна":
         page.theme_mode = ft.ThemeMode.SYSTEM
     elif choice == "Темна":
         page.theme_mode = ft.ThemeMode.DARK
     elif choice == "Світла":
         page.theme_mode = ft.ThemeMode.LIGHT

     settings = load_settings()
     settings["theme_mode"] = choice
     save_settings(settings)

     page.update()

# Cторінка налаштувань
def settings_page(page: ft.Page):
     settings = load_settings()

     theme_selector = ft.Dropdown(
         label="Тема оформлення",
         options=[
             ft.dropdown.Option("Системна"),
             ft.dropdown.Option("Темна"),
             ft.dropdown.Option("Світла"),
         ],
         value=settings["theme_mode"],
         on_change=lambda e: change_theme(e, page),
         width=300,
     )

     about_tile = ft.ExpansionTile(
         title=ft.Text("Про програму", weight=ft.FontWeight.BOLD),
         subtitle=ft.Text("Версія, автор, посилання"),
         leading=ft.Icon(ft.Icons.INFO_OUTLINE),
         controls=[
             ft.ListTile(
                 title=ft.Text("Версія програми"),
                 subtitle=ft.Text("1.0.0"),
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
                 on_click=lambda e: page.launch_url("https://github.com/xdenotte"),
             )
         ]
     )

     return ft.Column(
         controls=[
             ft.Container(height=5), 
             theme_selector,
             ft.Container(height=5), 
             about_tile,
         ],
         horizontal_alignment=ft.CrossAxisAlignment.START,
         expand=True,
         scroll=ft.ScrollMode.AUTO
     )