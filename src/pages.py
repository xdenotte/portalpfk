import flet as ft
import datetime
import asyncio

# Кеш-пам'ять для зберігання результатів
schedule_cache = None
rating_cache = None
ispyt_cache = None

async def pages_page(page: ft.Page, fetch_schedule_links, fetch_rating_links, fetch_pdf_links):
    global schedule_cache, rating_cache, ispyt_cache

    update_status_text = ft.Text("", size=12, color=ft.Colors.GREEN_700)

    def loading_indicator():
        return ft.Column(
            controls=[
                ft.ProgressRing(visible=True),
                ft.Text("Завантаження...", size=16)
            ],
            horizontal_alignment="center"
        )

    schedule_container = ft.Container(content=ft.Column(controls=[loading_indicator()], expand=True), expand=True)
    rating_container = ft.Container(content=ft.Column(controls=[loading_indicator()], expand=True), expand=True)
    ispyt_container = ft.Container(content=ft.Column(controls=[loading_indicator()], expand=True), expand=True)


    def update_status_message(message, color=ft.Colors.GREEN_700):
        update_status_text.value = message
        update_status_text.color = color
        page.update() 

    async def load_schedule():
        nonlocal schedule_container
        global schedule_cache
        fetched = False
        try:
            if schedule_cache is None: 
                schedule_container.content.controls.clear()
                schedule_container.content.controls.append(loading_indicator())
                page.update() 
                
                result = await fetch_schedule_links()
                if result:
                    schedule_cache = result
                    fetched = True

            schedule_container.content.controls.clear() 

            if not schedule_cache or not isinstance(schedule_cache, list):
                schedule_container.content.controls.append(
                    ft.Text("Не вдалося завантажити розклад або дані відсутні.", size=16, color=ft.Colors.RED_ACCENT_700)
                )
            else:
                for i, link in enumerate(schedule_cache):
                    schedule_container.content.controls.append(
                        ft.ElevatedButton(
                            text=f"{i + 1} курс",
                            width=400,
                            height=50,
                            on_click=lambda e, url=link: page.launch_url(url) if url else None
                        )
                    )
        except Exception as e:
            print(f"Помилка завантаження розкладу: {e}")
            schedule_container.content.controls.clear()
            schedule_container.content.controls.append(
                ft.Text(f"Помилка завантаження розкладу: {e}", size=16, color=ft.Colors.RED_ACCENT_700)
            )
        finally:
            page.update() 
        return fetched

    async def load_rating():
        nonlocal rating_container
        global rating_cache
        fetched = False
        try:
            if rating_cache is None: 
                rating_container.content.controls.clear()
                rating_container.content.controls.append(loading_indicator())
                page.update() 

                result = await fetch_rating_links()
                if result:
                    rating_cache = result
                    fetched = True

            rating_container.content.controls.clear() 

            if not rating_cache or not isinstance(rating_cache, list):
                rating_container.content.controls.append(
                    ft.Text("Не вдалося завантажити рейтинги або дані відсутні.", size=16, color=ft.Colors.RED_ACCENT_700)
                )
            else:
                for i, item in enumerate(rating_cache):
                    if isinstance(item, dict):
                        link = item.get("link")
                        text = item.get("text", f"Елемент {i + 1}")
                    else:
                        link = item
                        text = f"Елемент {i + 1}"

                    rating_container.content.controls.append(
                        ft.ElevatedButton(
                            text=text,
                            height=50,
                            width=400,
                            on_click=lambda e, url=link: page.launch_url(url) if url else None
                        )
                    )
        except Exception as e:
            print(f"Помилка завантаження рейтингів: {e}")
            rating_container.content.controls.clear()
            rating_container.content.controls.append(
                ft.Text(f"Помилка завантаження рейтингів: {e}", size=16, color=ft.Colors.RED_ACCENT_700)
            )
        finally:
            page.update() 
        return fetched

    async def load_ispyt():
        nonlocal ispyt_container
        global ispyt_cache
        fetched = False
        try:
            if ispyt_cache is None:
                ispyt_container.content.controls.clear()
                ispyt_container.content.controls.append(loading_indicator())
                page.update()

                result = await fetch_pdf_links()
                if result:
                    ispyt_cache = result
                    fetched = True

            ispyt_container.content.controls.clear() 

            if not ispyt_cache or not isinstance(ispyt_cache, list):
                ispyt_container.content.controls.append(
                    ft.Text("Не знайдено PDF або сервер недоступний.", size=16, color=ft.Colors.RED_ACCENT_700)
                )
            else:
                if ispyt_cache:
                    ispyt_container.content.controls.append(
                        ft.ElevatedButton(
                            text="Іспити 3-4 курсів (1-2 семестри)",
                            width=400,
                            height=50,
                            on_click=lambda e, url=ispyt_cache[0]: page.launch_url(url) if url else None
                        )
                    )
                else:
                    ispyt_container.content.controls.append(
                        ft.Text("Не знайдено PDF іспитів.", size=16, color=ft.Colors.RED_ACCENT_700)
                    )
        except Exception as e:
            print(f"Помилка завантаження іспитів: {e}")
            ispyt_container.content.controls.clear()
            ispyt_container.content.controls.append(
                ft.Text(f"Помилка завантаження іспитів: {e}", size=16, color=ft.Colors.RED_ACCENT_700)
            )
        finally:
            page.update() 
        return fetched

    async def load_all_data():
        update_status_message("Завантаження даних...", color=ft.Colors.BLUE_ACCENT_700)
        fetched_schedule, fetched_rating, fetched_ispyt = await asyncio.gather(
            load_schedule(),
            load_rating(),
            load_ispyt()
        )

        # Логіка оновлення статусу
        if fetched_schedule or fetched_rating or fetched_ispyt:
            current_time = datetime.datetime.now()
            page.session.set("last_data_update_time", current_time.isoformat())
            formatted_time = current_time.strftime("%d.%m.%Y %H:%M")
            update_status_message(f"Дані оновлено {formatted_time}", color=ft.Colors.GREEN_700)
        else:
            last_updated_time_str = page.session.get("last_data_update_time")
            if last_updated_time_str:
                try:
                    last_updated_time = datetime.datetime.fromisoformat(last_updated_time_str)
                    formatted_time = last_updated_time.strftime("%d.%m.%Y %H:%M")
                    if schedule_cache is not None and rating_cache is not None and ispyt_cache is not None:
                        update_status_message(f"Дані з кешу. Оновлено: {formatted_time}", color=ft.Colors.BLUE_GREY_400)
                    else:
                        update_status_message(f"Деякі дані не завантажено. Останнє оновлення: {formatted_time}", color=ft.Colors.ORANGE_ACCENT_700)
                except ValueError:
                    update_status_message("Помилка: не вдалося завантажити всі дані або час невідомий.", color=ft.Colors.RED_ACCENT_700)
            else:
                update_status_message("Не вдалося завантажити дані.", color=ft.Colors.RED_ACCENT_700)
        page.update()


    async def refresh_data(e):
        global schedule_cache, rating_cache, ispyt_cache
        schedule_cache = None
        rating_cache = None
        ispyt_cache = None

        schedule_container.content.controls.clear()
        schedule_container.content.controls.append(loading_indicator())
        rating_container.content.controls.clear()
        rating_container.content.controls.append(loading_indicator())
        ispyt_container.content.controls.clear()
        ispyt_container.content.controls.append(loading_indicator())

        page.update() 
        await load_all_data() 

    page.run_task(load_all_data)

    return ft.Column(
        controls=[
            ft.Container( 
                content=ft.Row(
                    controls=[
                        update_status_text,
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Оновити дані",
                            on_click=refresh_data,
                            icon_size=20
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=ft.padding.only(top=5, bottom=10),
                alignment=ft.alignment.center_left
            ),
            ft.ExpansionTile(
                title=ft.Text("Розклад занять", size=18, weight=ft.FontWeight.BOLD),
                controls=[schedule_container]
            ),
            ft.ExpansionTile(
                title=ft.Text("Рейтинги студентів", size=18, weight=ft.FontWeight.BOLD),
                controls=[rating_container]
            ),
            ft.ExpansionTile(
                title=ft.Text("Розклад іспитів", size=18, weight=ft.FontWeight.BOLD),
                controls=[ispyt_container]
            )
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )