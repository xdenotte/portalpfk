import flet as ft
import asyncio

# Кеш новин
cached_news = None

# --- Компонент: індикатор завантаження ---
def loading_indicator():
    return ft.Container(
        alignment=ft.alignment.center,
        expand=True,
        content=ft.Column(
            [
                ft.ProgressRing(width=50, height=50),
                ft.Text("Завантаження новин...", size=16, font_family="Open Sans"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


# --- Компонент: повідомлення про помилку ---
def show_error_message(message: str) -> ft.Control:
    return ft.Column(
        [
            ft.Text(
                message,
                size=18,
                color=ft.Colors.RED_ACCENT_700,
                text_align=ft.TextAlign.CENTER,
                font_family="Open Sans",
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True,
    )


# --- Компонент: одна картка новини ---
def create_news_card(item: dict) -> ft.Control:
    content = ft.Column(spacing=10, expand=True)

    # Зображення
    if item.get("image_url"):
        content.controls.append(
            ft.Container(
                content=ft.Image(
                    src=item["image_url"],
                    fit=ft.ImageFit.COVER,
                    error_content=ft.Text("Немає фото", color=ft.Colors.RED_ACCENT_700),
                    border_radius=ft.border_radius.all(5),
                ),
                expand=True,
                alignment=ft.alignment.center,
                padding=ft.padding.only(bottom=5),
            )
        )

    # Заголовок
    content.controls.append(
        ft.Text(
            item.get("title", "Немає заголовка"),
            font_family="Open Sans",
            size=18,
            weight=ft.FontWeight.BOLD,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
    )

    # Дата
    content.controls.append(
        ft.Text(
            item.get("date", "Немає дати"),
            font_family="Open Sans",
            size=14,
            color=ft.Colors.BLUE_ACCENT_700,
        )
    )

    # Уривок тексту
    content.controls.append(
        ft.Text(
            item.get("content", "Немає тексту новини."),
            font_family="Open Sans",
            size=14,
            max_lines=3,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
    )

    # Кнопка "Читати далі"
    if item.get("link"):
        content.controls.append(
            ft.Container(
                content=ft.ElevatedButton(
                    text="Читати далі",
                    url=item["link"],
                    icon=ft.Icons.ARROW_FORWARD,
                ),
                alignment=ft.alignment.bottom_right,
                expand=True,
            )
        )

    return ft.Card(
        content=ft.Container(
            content=content,
            padding=15,
            expand=True,
        ),
        elevation=4,
        margin=ft.margin.symmetric(vertical=8),
    )


# --- Основна функція домашньої сторінки ---
def home_page(page: ft.Page, fetch_news) -> ft.Control:
    global cached_news

    # Колонка, яка буде повертатись
    home_content_column = ft.Column(expand=True, scroll="auto")

    # --- Функція для оновлення UI ---
    def update_home_ui(news_data):
        home_content_column.controls.clear()

        home_content_column.controls.append(
            ft.Text(
                "Останні новини:",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                font_family="Open Sans",
                expand=True,
            )
        )

        if news_data and isinstance(news_data, list):
            for item in news_data:
                home_content_column.controls.append(create_news_card(item))
        else:
            error_message = "Не вдалося завантажити новини. Перевірте підключення або спробуйте пізніше."
            home_content_column.controls.append(show_error_message(error_message))

        page.update()

    # --- Асинхронне завантаження новин ---
    async def load_news_task():
        global cached_news

        # Показуємо індикатор
        home_content_column.controls.clear()
        home_content_column.controls.append(loading_indicator())
        page.update()

        await asyncio.sleep(0.5)

        try:
            fetched_data = await fetch_news()
            cached_news = fetched_data
        except Exception as e:
            print(f"[ERROR] Не вдалося отримати новини: {e}")
            cached_news = []

        update_home_ui(cached_news)

    # --- Основна логіка завантаження/виводу ---
    if cached_news:
        update_home_ui(cached_news)
    else:
        page.run_task(load_news_task)

    return home_content_column
