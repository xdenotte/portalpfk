import httpx
from bs4 import BeautifulSoup
import re # Імпортуємо модуль для паттернів

url_ispyt = "https://pk-nuk.com.ua/rozklad-ispytiv/"
url_news = "https://pk-nuk.com.ua/category/news/"
url_zanyat = "https://pk-nuk.com.ua/rozklad-zanyat/"
url_rating = "https://pk-nuk.com.ua/rejtingovi-spiski-zdobuvachiv-osviti/"

# Функція для отримання новин
async def fetch_news():
    timeout = 5
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url_news, timeout=timeout)
            response.raise_for_status()
    except httpx.RequestError as e:
        print(f"Сервер новин не відповідає: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    all_news_items = soup.find_all("article", class_="post-each-blog")
    # Беремо тільки останні 5 новин, впливає на кількість відображення в головній сторінці (максимально 10)
    # Впливає на швидкість завантажування
    latest_news_items = all_news_items[:5]
    news = []

    # Патерн для пошуку дати у форматі ДД.ММ.РРРР
    date_pattern = re.compile(r'\d{2}\.\d{2}\.\d{4}')

    for item in latest_news_items:
        title_tag = item.find("h2", class_="entry-title")
        title = title_tag.text.strip() if title_tag else "Без заголовка"
        link = title_tag.find("a").get("href") if title_tag and title_tag.find("a") else None

        # --- Пошук дати ---
        date = "Без дати" # Значення за замовчуванням

        # Спроба знайти дату у стандартному місці (ul.post-date)
        date_ul = item.find("ul", class_="post-date")
        if date_ul:
            # Якщо знайдено ul.post-date, беремо текст з усіх li в ньому
            date = " ".join(li.text.strip() for li in date_ul.find_all("li"))
        else:
            # Якщо ul.post-date не знайдено, шукаємо альтернативне місце
            # Шукаємо div з класом entry-meta
            entry_meta_div = item.find("div", class_="entry-meta")
            if entry_meta_div:
                # У цьому div шукаємо ul, а в ньому - li, яке містить дату, якщо не було знайдено в фотографії
                calendar_li = entry_meta_div.select_one("ul li i.fas.fa-calendar")
                if calendar_li:
                    # Батьківський елемент - це li
                    date_li = calendar_li.find_parent("li")
                    if date_li:
                        # Отримуємо весь текст з li
                        li_text = date_li.get_text() # Використовуємо get_text()
                        # Використовуємо паттерн щоб зпарсити тіки дату
                        match = date_pattern.search(li_text)
                        if match:
                            date = match.group(0) # Беремо знайдений фрагмент (дату)

        content_div = item.find("div", class_="entry-content")
        content = content_div.find("p").text.strip() if content_div and content_div.find("p") else "Без тексту"

        image_div = item.find("div", class_="entry-thumbnail-area")
        image_tag = image_div.find("img") if image_div else None
        image_url = image_tag.get("src") if image_tag else None

        news.append({"title": title, "link": link, "date": date, "content": content, "image_url": image_url})

    return news

# Функція для отримання розкладів занять
async def fetch_schedule_links():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url_zanyat, timeout=5)
            response.raise_for_status()
    except httpx.RequestError as e:
        print(f"Сервер розкладу занять не відповідає: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.find("div", class_="elementor-widget-container")
    ul_tag = container.find("ul") if container else None
    return [a.get("href") for li in ul_tag.find_all("li") if (a := li.find("a")) and a.get("href")] if ul_tag else []

# Функція для отримання рейтингів
async def fetch_rating_links():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url_rating, timeout=5)
            response.raise_for_status()
    except httpx.RequestError as e:
        print(f"Сервер рейтингових списків не відповідає: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    container = soup.find("div", class_="elementor-widget-container")
    p_tags = container.find_all("p") if container else []

    result = []
    for p in p_tags:
        a_tag = p.find("a")
        text = p.get_text(strip=True)
        link = a_tag.get("href") if a_tag else None
        result.append({"link": link, "text": text})

    return result

# Функція для отримання посилань на PDF екзаменів
async def fetch_pdf_links():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url_ispyt)
            response.raise_for_status()
    except httpx.RequestError as e:
        print(f"Помилка при запиті: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    pdf_links = [a['href'] for a in soup.find_all("a", href=True) if a["href"].endswith(".pdf")]
    return pdf_links