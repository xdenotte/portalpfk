import flet as ft
import datetime
import asyncio

# Кеш-пам'ять (глобальна)
schedule_cache = None
rating_cache = None
ispyt_cache = None

async def pages_page(page: ft.Page, fetch_schedule_links, fetch_rating_links, fetch_pdf_links):
    global schedule_cache, rating_cache, ispyt_cache

    update_status_text = ft.Text("", size=12, color=ft.Colors.GREEN_700)

    async def open_url(e):
        url = e.control.data
        if url:
            await page.launch_url(url)

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
        try:
            if schedule_cache is None: 
                # Якщо кешу немає — завантажуємо
                result = await fetch_schedule_links()
                if result:
                    schedule_cache = result
            
            # Якщо кеш є (або щойно завантажився)
            if schedule_cache:
                schedule_container.content.controls.clear() 
                for item in schedule_cache:
                    schedule_container.content.controls.append(
                        ft.Button(
                            content=ft.Text(item["text"]),
                            width=400,
                            height=50,
                            data=item["link"],
                            on_click=open_url
                        )
                    )
                page.update()
                return True # Дані успішно відображені (з мережі або кешу)
            
            schedule_container.content.controls.append(ft.Text("Дані відсутні."))
            return False
        except Exception as e:
            print(f"Помилка розкладу: {e}")
            return False

    async def load_rating():
        nonlocal rating_container
        global rating_cache
        try:
            if rating_cache is None:
                result = await fetch_rating_links()
                if result:
                    rating_cache = result

            if rating_cache:
                rating_container.content.controls.clear()
                for i, item in enumerate(rating_cache):
                    text = item.get("text", f"Елемент {i+1}") if isinstance(item, dict) else f"Елемент {i+1}"
                    link = item.get("link") if isinstance(item, dict) else item
                    rating_container.content.controls.append(
                        ft.Button(content=ft.Text(text), height=50, width=400, data=link, on_click=open_url)
                    )
                page.update()
                return True
            return False
        except Exception as e:
            print(f"Помилка рейтингу: {e}")
            return False

    async def load_ispyt():
        nonlocal ispyt_container
        global ispyt_cache
        try:
            if ispyt_cache is None:
                result = await fetch_pdf_links()
                if result:
                    ispyt_cache = result

            if ispyt_cache:
                ispyt_container.content.controls.clear()
                ispyt_container.content.controls.append(
                    ft.Button(content=ft.Text("Іспити 3-4 курсів"), width=400, height=50, data=ispyt_cache[0], on_click=open_url)
                )
                page.update()
                return True
            return False
        except Exception as e:
            print(f"Помилка іспитів: {e}")
            return False

    async def load_all_data():
        # Перевіряємо, чи ми вперше завантажуємо, чи дані вже в кеші
        is_cached = all([schedule_cache, rating_cache, ispyt_cache])
        
        if not is_cached:
            update_status_message("Завантаження даних...", color=ft.Colors.BLUE_ACCENT_700)
        
        results = await asyncio.gather(
            load_schedule(),
            load_rating(),
            load_ispyt()
        )

        current_time = datetime.datetime.now().strftime("%H:%M")
        
        if all(results):
            msg = f"Дані актуальні ({current_time})" if is_cached else f"Всі дані оновлено о {current_time}"
            update_status_message(msg, color=ft.Colors.GREEN_700)
        elif any(results):
            update_status_message(f"Частково завантажено о {current_time}", color=ft.Colors.ORANGE_ACCENT_700)
        else:
            update_status_message("Не вдалося отримати дані", color=ft.Colors.RED_ACCENT_700)

    async def refresh_data(e):
        global schedule_cache, rating_cache, ispyt_cache
        schedule_cache = rating_cache = ispyt_cache = None
        # Повертаємо індикатори завантаження
        schedule_container.content = loading_indicator()
        rating_container.content = loading_indicator()
        ispyt_container.content = loading_indicator()
        page.update()
        await load_all_data()

    # Запускаємо через run_task
    page.run_task(load_all_data)

    return ft.Column(
        controls=[
            ft.Container( 
                content=ft.Row(
                    controls=[
                        update_status_text,
                        ft.IconButton(icon=ft.Icons.REFRESH, on_click=refresh_data, tooltip="Оновити")
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=ft.Padding(0, 5, 0, 10)
            ),
            ft.ExpansionTile(
                title=ft.Text("Розклад занять", weight="bold"),
                controls=[schedule_container]
            ),
            ft.ExpansionTile(
                title=ft.Text("Рейтинги студентів", weight="bold"),
                controls=[rating_container]
            ),
            ft.ExpansionTile(
                title=ft.Text("Розклад іспитів", weight="bold"),
                controls=[ispyt_container]
            )
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )