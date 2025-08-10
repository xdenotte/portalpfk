import flet as ft
from datetime import datetime

def fordiplom(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.START

    current_year = datetime.now().year
    enrollment_year = current_year - 4

    example_filename = f"Шевченко_Т_Г_412-КІ-{str(enrollment_year)[-2:]}_{current_year}_плагiат."

    def section_title(text):
        return ft.Text(text, size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)

    def section_text(text, italic=False):
        return ft.Text(text, size=16, italic=italic)

    def list_item(text):
        return ft.ListTile(
            leading=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREEN),
            title=ft.Text(text, size=16),
        )

    def email_block(special, email, url):
        return ft.Card(
            content=ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.EMAIL, color=ft.Colors.BLUE_700),
                    title=ft.Text(f"Для спеціальності {special}: надсилайте роботу на електронну пошту:", size=16),
                    subtitle=ft.Row(
                        [
                            ft.Text(
                                email,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700,
                                selectable=True,
                                expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS, 
                            ),
                            ft.IconButton(
                                icon=ft.Icons.LAUNCH,
                                icon_color=ft.Colors.BLUE_700,
                                tooltip="Відкрити у поштовому клієнті",
                                on_click=lambda e: page.launch_url(f"mailto:{url}"),
                                icon_size=20,
                                style=ft.ButtonStyle(
                                    shape=ft.CircleBorder(),
                                    padding=5,
                                )
                            )
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    )
                ),
                padding=10,
            )
        )

    content_column = ft.Column(
        [
            ft.Text("Перевірка дипломних робіт на плагіат",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color=ft.Colors.PRIMARY),

            ft.Divider(height=30, color="transparent"),

            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Шановні випускники!",
                                size=18,
                                weight=ft.FontWeight.BOLD),
                        section_text("Для успішної перевірки вашої дипломної роботи на плагіат, будь ласка, уважно ознайомтесь з наступними правилами. Недотримання цих вимог призведе до відхилення роботи та її неперевірки.")
                    ]),
                    padding=15,
                )
            ),

            ft.Divider(height=20, color="transparent"),
            section_title("Правила подання роботи на перевірку:"),
            list_item("Ви, як автор, несете повну відповідальність за підготовку файлу роботи, що підлягає перевірці."),
            list_item("Файл повинен бути у форматі .doc, .docx, .pdf, або .odt. Файли, що містять елементи захисту (наприклад, паролі), не підтримуються."),
            list_item(f"Назва файлу повинна складатися з прізвища та ініціалів, номера групи здобувача освіти, рік вступу здобувача освіти та року подання роботи. Приклад: {example_filename}"),
            list_item("Для виявлення рівня плагіату робота відправляється на електронну пошту без економічного розділу, розділу «Охорона праці», додатків та списку літератури."),

            ft.Divider(height=30, color="transparent"),
            section_title("Куди надсилати роботу:"),
            email_block("123 «Комп’ютерна інженерія»", "it.plagiat@pk-nuk.com.ua", "it.plagiat@pk-nuk.com.ua"),
            email_block("133 «Галузеве машинобудування»", "gm.plagiat@pk-nuk.com.ua", "gm.plagiat@pk-nuk.com.ua"),

            ft.Divider(height=30, color="transparent"),
            ft.Card(
                content=ft.Container(
                    content=section_text("Будь ласка, переконайтеся, що ви дотримуєтеся всіх вищезгаданих правил, щоб уникнути затримок у процесі перевірки вашої дипломної роботи.", italic=True),
                    padding=15,
                    border_radius=10
                )
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.START,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    return content_column