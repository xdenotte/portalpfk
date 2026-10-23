import asyncio
import time

import flet as ft

CACHE_TTL = 300  # секунд, після цього дані вважаються застарілими
PULL_THRESHOLD = 80  # пікселів, на скільки потрібно потягнути вниз (висота кружка)

# Кеш новин на рівні модуля
_cache: dict = {"data": None, "ts": 0.0}
_lock = asyncio.Lock()


def _text(value: str, **kwargs) -> ft.Text:
    return ft.Text(value, **kwargs)


def _vertical_delta(e) -> float:
    """Зміна по вертикалі в одній події перетягування."""
    value = getattr(e, "primary_delta", None)
    if value is not None:
        return float(value)
    local = getattr(e, "local_delta", None)
    return float(getattr(local, "y", 0) or 0)


# --- Компоненти ---

def loading_indicator() -> ft.Control:
    return ft.Container(
        height=300,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            [
                ft.ProgressRing(width=50, height=50),
                _text("Завантаження новин...", size=16),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def error_message(message: str) -> ft.Control:
    return ft.Container(
        height=300,
        alignment=ft.Alignment.CENTER,
        content=_text(
            message,
            size=18,
            color=ft.Colors.RED_ACCENT_700,
            text_align=ft.TextAlign.CENTER,
        ),
    )


def create_news_card(item: dict) -> ft.Control:
    controls: list[ft.Control] = []

    if item.get("image_url"):
        controls.append(
            ft.Container(
                content=ft.Image(
                    src=item["image_url"],
                    fit=ft.BoxFit.COVER,
                    border_radius=ft.BorderRadius.all(5),
                    error_content=ft.Text("Немає фото", color=ft.Colors.RED_ACCENT_700),
                ),
                expand=True,
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding.only(bottom=5),
            )
        )

    controls.append(
        _text(
            item.get("title", "Немає заголовка"),
            size=18,
            weight=ft.FontWeight.BOLD,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
    )
    controls.append(
        _text(item.get("date", "Немає дати"), size=14, color=ft.Colors.BLUE_ACCENT_700)
    )
    controls.append(
        _text(
            item.get("content", "Немає тексту новини."),
            size=14,
            max_lines=3,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
    )

    if item.get("link"):
        controls.append(
            ft.Container(
                alignment=ft.Alignment.CENTER_RIGHT,
                content=ft.TextButton(
                    content=ft.Text("Читати далі"),
                    icon=ft.Icons.ARROW_FORWARD,
                    url=item["link"],
                ),
            )
        )

    return ft.Card(
        elevation=4,
        margin=ft.Margin.symmetric(vertical=8),
        content=ft.Container(
            padding=15,
            content=ft.Column(controls, spacing=10),
        ),
    )


# --- Головна сторінка ---

def home_page(page: ft.Page, fetch_news) -> ft.Control:
    # Заголовок зафіксований, не рухається при прокручуванні
    header = ft.Container(
        padding=ft.Padding.only(left=12, top=8, bottom=4),
        content=_text(
            "Останні новини:",
            size=24,
            weight=ft.FontWeight.BOLD,
        ),
    )

    # --- Кружок, який з'являється над першою новиною ---
    pull_ring = ft.ProgressRing(
        width=32,
        height=32,
        stroke_width=3,
        value=0,
    )

    pull_check = ft.Icon(
        icon=ft.Icons.CHECK,
        size=32,
        color=ft.Colors.GREEN,
    )

    pull_box = ft.Container(
        height=0,
        alignment=ft.Alignment.CENTER,
        content=pull_ring,
    )

    pull: dict = {
        "distance": 0.0,
        "loading": False,
        "armed": False,
    }

    def set_pull_visual(distance: float) -> None:
        """Показує прогрес або галочку, коли поріг досягнуто."""
        progress = min(distance / PULL_THRESHOLD, 1.0)
        pull_box.height = PULL_THRESHOLD * progress

        if distance >= PULL_THRESHOLD:
            pull_box.content = pull_check
        else:
            pull_box.content = pull_ring
            pull_ring.value = progress

        page.update()

    def set_loading_visual(active: bool) -> None:
        """Показує індикатор під час завантаження."""
        if active:
            pull_box.height = PULL_THRESHOLD
            pull_box.content = pull_ring
            pull_ring.value = None
        else:
            pull_box.height = 0
            pull_ring.value = 0
            pull_box.content = pull_ring

        page.update()

    # --- Список новин ---
    news_list = ft.ListView(
        expand=True,
        spacing=0,
        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
    )

    def render(items: list | None) -> None:
        news_list.controls.clear()
        news_list.controls.append(pull_box)

        if items:
            first, *rest = items

            news_list.controls.append(create_news_card(first))
            news_list.controls.extend(create_news_card(i) for i in rest)
        else:
            news_list.controls.append(
                error_message(
                    "Не вдалося завантажити новини. "
                    "Перевірте підключення або спробуйте пізніше."
                )
            )

        page.update()

    def show_full_loading() -> None:
        """Перше завантаження, коли кешу ще немає: спінер по центру списку."""
        news_list.controls.clear()
        news_list.controls.append(loading_indicator())
        page.update()

    def is_fresh() -> bool:
        return (
            _cache["data"] is not None
            and time.monotonic() - _cache["ts"] < CACHE_TTL
        )

    async def load(force: bool = False) -> None:
        if not force and is_fresh():
            render(_cache["data"])
            return

        async with _lock:
            had_cache = _cache["data"] is not None
            pull["loading"] = True

            if had_cache:
                # Новини зникають, над порожнім списком крутиться кружок
                news_list.controls.clear()
                news_list.controls.append(pull_box)
                set_loading_visual(True)
            else:
                show_full_loading()

            try:
                data = await asyncio.wait_for(fetch_news(), timeout=15)
            except Exception as e: # noqa: BLE001
                print(f"[ERROR] Не вдалося отримати новини: {e}")
                data = None

            if data is not None:
                _cache["data"] = data
                _cache["ts"] = time.monotonic()

            pull["loading"] = False

            # Ховаємо кружок до того, як render знову додасть його в список
            set_pull_visual(0)

        render(_cache["data"])

    async def on_news_scroll(e: ft.OnScrollEvent) -> None:
        if pull["loading"]:
            return

        if e.event_type == ft.ScrollType.START:
            pull["distance"] = 0.0
            pull["armed"] = e.extent_before <= 1.0
            set_pull_visual(0)
            return

        if e.event_type == ft.ScrollType.OVERSCROLL:
            overscroll = float(e.overscroll or 0)

            if pull["armed"] and overscroll < 0:
                pull["distance"] = min(
                    PULL_THRESHOLD,
                    pull["distance"] + abs(overscroll),
                )
                set_pull_visual(pull["distance"])

            elif overscroll > 0:
                pull["distance"] = 0.0
                pull["armed"] = False
                set_pull_visual(0)

            return

        if e.event_type == ft.ScrollType.END:
            should_refresh = (
                pull["armed"]
                and pull["distance"] >= PULL_THRESHOLD
                and not _lock.locked()
            )

            pull["distance"] = 0.0
            pull["armed"] = False

            if should_refresh:
                await load(force=True)
            else:
                set_pull_visual(0)

    news_list.on_scroll = on_news_scroll

    # Миттєвий показ кешу
    if _cache["data"] is not None:
        render(_cache["data"])

    page.run_task(load)

    # Заголовок фіксований зверху, список прокручується під ним
    return ft.Column(
        [
            header,
            news_list,
        ],
        expand=True,
    )
