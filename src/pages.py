import asyncio
import datetime
import time

import flet as ft

CACHE_TTL = 3600  # секунд, після цього дані оновлюються при відкритті сторінки
REQUEST_TIMEOUT = 15

_cache: dict[str, dict] = {}
_lock = asyncio.Lock()


def _is_fresh(key: str) -> bool:
    entry = _cache.get(key)
    return bool(entry) and time.monotonic() - entry["ts"] < CACHE_TTL


def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M")


def _loading() -> ft.Control:
    return ft.Container(
        padding=20,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            [ft.ProgressRing(), ft.Text("Завантаження...", size=16)],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


async def pages_page(page: ft.Page, fetch_schedule_links, fetch_rating_links, fetch_pdf_links):
    url_launcher = ft.UrlLauncher()
    status = ft.Text("", size=12, color=ft.Colors.GREEN_700)

    async def open_url(e):
        if e.control.data:
            await url_launcher.launch_url(e.control.data)

    async def ispyt_items():
        # Поки показуємо лише перший PDF, як і раніше
        links = await fetch_pdf_links()
        if not links:
            return []
        return [{"text": "Іспити 3-4 курсів", "link": links[0]}]

    # (ключ кешу, заголовок секції, функція завантаження)
    sections = [
        ("schedule", "Розклад занять", fetch_schedule_links),
        ("rating", "Рейтинги студентів", fetch_rating_links),
        ("ispyt", "Розклад іспитів", ispyt_items),
    ]

    bodies = {
        key: ft.Column([_loading()], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        for key, _, _ in sections
    }

    def render(key: str, items: list | None) -> None:
        body = bodies[key]
        body.controls.clear()
        if items:
            body.controls.extend(
                ft.Button(
                    content=ft.Text(item["text"]),
                    width=400,
                    height=50,
                    data=item["link"],
                    on_click=open_url,
                )
                for item in items
            )
        else:
            body.controls.append(ft.Text("Дані відсутні."))

    async def load_section(key: str, fetch, force: bool) -> bool:
        """Повертає True, якщо отримано свіжі дані."""
        if not force and _is_fresh(key):
            render(key, _cache[key]["data"])
            return True

        try:
            data = await asyncio.wait_for(fetch(), timeout=REQUEST_TIMEOUT)
        except RuntimeError as e:
            print(f"Помилка ({key}): {e}")
            data = None

        if data:
            _cache[key] = {"data": data, "ts": time.monotonic()}
            render(key, data)
            return True

        # Оновити не вдалося: лишаємо старі дані, якщо вони є
        render(key, _cache.get(key, {}).get("data"))
        return False

    def set_status(message: str, color) -> None:
        status.value = message
        status.color = color

    async def load_all(force: bool = False) -> None:
        async with _lock:
            was_cached = all(_is_fresh(key) for key, _, _ in sections)

            # Показуємо спінери тільки там, де даних немає або потрібне оновлення
            for key, _, _ in sections:
                if force or not _is_fresh(key):
                    bodies[key].controls = [_loading()]

            if force or not was_cached:
                set_status("Завантаження даних...", ft.Colors.BLUE_ACCENT_700)
            page.update()

            results = await asyncio.gather(
                *(load_section(key, fetch, force) for key, _, fetch in sections)
            )

            current_time = _now()
            if all(results):
                if was_cached and not force:
                    set_status(f"Дані актуальні ({current_time})", ft.Colors.GREEN_700)
                else:
                    set_status(f"Всі дані оновлено о {current_time}", ft.Colors.GREEN_700)
            elif any(results):
                set_status(f"Частково завантажено о {current_time}", ft.Colors.ORANGE_ACCENT_700)
            else:
                set_status("Не вдалося отримати дані", ft.Colors.RED_ACCENT_700)

            page.update()

    async def refresh(e):
        if not _lock.locked():
            await load_all(force=True)

    page.run_task(load_all)

    return ft.Column(
        controls=[
            ft.Container(
                padding=ft.Padding.only(top=5, bottom=10),
                content=ft.Row(
                    controls=[
                        status,
                        ft.IconButton(icon=ft.Icons.REFRESH, on_click=refresh, tooltip="Оновити"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
            *(
                ft.ExpansionTile(
                    title=ft.Text(title, weight=ft.FontWeight.BOLD),
                    controls=[bodies[key]],
                )
                for key, title, _ in sections
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
