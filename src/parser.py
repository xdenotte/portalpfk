import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

# ============================================================
# URL сторінок сайту
# ============================================================

url_ispyt = "https://pk-nuk.com.ua/rozklad-ispytiv/"
url_news = "https://pk-nuk.com.ua/category/news/"
url_zanyat = "https://pk-nuk.com.ua/rozklad-zanyat/"
url_rating = "https://pk-nuk.com.ua/rejtingovi-spiski-zdobuvachiv-osviti/"


# ============================================================
# Налаштування HTTP-запитів
# ============================================================

TIMEOUT = httpx.Timeout(
    8.0,
    connect=3.0,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; PFK-NUK-Portal/1.0)"
    )
}


# Шаблони дат
DATE_PATTERN = re.compile(r"\d{2}\.\d{2}\.\d{4}")
ISO_DATE_PATTERN = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

# Допоміжні функції

async def get_soup(url: str) -> BeautifulSoup | None:
    try:
        async with httpx.AsyncClient(
            timeout=TIMEOUT,
            follow_redirects=True,
            headers=HEADERS,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        return BeautifulSoup(response.text, "html.parser")

    except httpx.HTTPError as e:
        print(f"[HTTP ERROR] Не вдалося завантажити {url}: {e}")
        return None


def absolute_url(
    base_url: str,
    raw_url: str | None,
) -> str | None:

    if not raw_url:
        return None

    raw_url = raw_url.strip()

    if not raw_url:
        return None

    result = urljoin(base_url, raw_url)
    parsed = urlparse(result)

    if parsed.scheme.lower() not in ("http", "https"):
        return None

    if not parsed.netloc:
        return None

    return result


def is_pdf(url: str | None) -> bool:
    if not url:
        return False

    return urlparse(url).path.lower().endswith(".pdf")


def unique_urls(urls: list[str]) -> list[str]:
    return list(dict.fromkeys(urls))

def get_attr(tag, name: str) -> str | None:
    """Повертає атрибут тега як рядок або None."""
    if tag is None:
        return None
    value = tag.get(name)
    if isinstance(value, list):
        value = " ".join(value)
    return value if isinstance(value, str) else None

# Допоміжні функції для новин

def extract_news_date(item) -> str:
    date_ul = item.find("ul", class_="post-date")

    if date_ul:
        date_text = " ".join(
            li.get_text(" ", strip=True)
            for li in date_ul.find_all("li")
        ).strip()

        match = DATE_PATTERN.search(date_text)

        if match:
            return match.group(0)

        if date_text:
            return date_text

    # 2. HTML-елемент time
    time_tag = item.find("time")

    if time_tag:
        time_text = time_tag.get_text(" ", strip=True)

        match = DATE_PATTERN.search(time_text)

        if match:
            return match.group(0)

        datetime_value = time_tag.get("datetime", "")

        match = DATE_PATTERN.search(datetime_value)

        if match:
            return match.group(0)

        match = ISO_DATE_PATTERN.search(datetime_value)

        if match:
            year, month, day = match.groups()
            return f"{day}.{month}.{year}"

    # 3. Альтернативний блок метаданих
    entry_meta = item.find("div", class_="entry-meta")

    if entry_meta:
        meta_text = entry_meta.get_text(" ", strip=True)

        match = DATE_PATTERN.search(meta_text)

        if match:
            return match.group(0)

    # 4. Дата не знайдена
    return "Без дати"


def extract_news_image(item) -> str | None:

    image_div = item.find(
        "div",
        class_="entry-thumbnail-area",
    )

    image_tag = (
        image_div.find("img")
        if image_div
        else item.find("img")
    )

    if not image_tag:
        return None

    # Атрибути lazy-loading мають пріоритет,
    # оскільки src може містити тимчасове зображення.
    for attribute in (
        "data-src",
        "data-lazy-src",
        "data-original",
        "src",
    ):
        image_url = image_tag.get(attribute)

        if image_url and not image_url.strip().lower().startswith(
            "data:image/"
        ):
            return absolute_url(url_news, image_url)

    # Якщо звичайного URL немає, перевіряємо srcset.
    srcset = image_tag.get("data-srcset") or image_tag.get("srcset")

    if srcset:
        candidates = [
            candidate.strip()
            for candidate in srcset.split(",")
            if candidate.strip()
        ]

        if candidates:
            # Зазвичай останній варіант має найбільшу роздільність.
            image_url = candidates[-1].split()[0]
            return absolute_url(url_news, image_url)

    return None

# Отримання новин

async def fetch_news() -> list[dict[str, str | None]] | None:

    soup = await get_soup(url_news)

    if soup is None:
        return None

    all_news_items = soup.find_all(
        "article",
        class_="post-each-blog",
    )

    # Максимальна кількість новин на головній сторінці
    latest_news_items = all_news_items[:10]

    news: list[dict[str, str | None]] = []

    for item in latest_news_items:

        title_tag = item.find(
            "h2",
            class_="entry-title",
        )

        title = (
            title_tag.get_text(" ", strip=True)
            if title_tag
            else "Без заголовка"
        )

        link_tag = (
            title_tag.find("a", href=True)
            if title_tag
            else None
        )

        link = absolute_url(
            url_news,
            str(link_tag.get("href")) if link_tag and link_tag.get("href") else None,
        )

        date = extract_news_date(item)

        content_div = item.find(
            "div",
            class_="entry-content",
        )

        paragraph = (
            content_div.find("p")
            if content_div
            else None
        )

        content = (
            paragraph.get_text(" ", strip=True)
            if paragraph
            else "Без тексту"
        )

        image_url = extract_news_image(item)

        news.append({
            "title": title,
            "link": link,
            "date": date,
            "content": content,
            "image_url": image_url,
        })

    return news

# Отримання посилань на розклади занять

async def fetch_schedule_links() -> list[dict[str, str]]:

    soup = await get_soup(url_zanyat)

    if soup is None:
        return []

    containers = soup.find_all(
        "div",
        class_="elementor-widget-container",
    )

    result: list[dict[str, str]] = []
    seen_urls = set()

    for container in containers:
        for a in container.find_all("a", href=True):

            href = absolute_url(
                url_zanyat,
                get_attr(a, "href"),
            )

            if not href or not is_pdf(href):
                continue

            if href in seen_urls:
                continue

            seen_urls.add(href)

            text = a.get_text(" ", strip=True)

            if not text:
                text = "Розклад (PDF)"

            result.append({
                "link": href,
                "text": text,
            })

    return result

# Отримання рейтингових списків

async def fetch_rating_links() -> list[dict[str, str]]:

    soup = await get_soup(url_rating)

    if soup is None:
        return []

    containers = soup.find_all(
        "div",
        class_="elementor-widget-container",
    )

    result: list[dict[str, str]] = []
    seen_urls = set()

    for container in containers:
        for a in container.find_all("a", href=True):

            href = absolute_url(
                url_rating,
                get_attr(a, "href"),
            )

            if not href:
                continue

            if href in seen_urls:
                continue

            seen_urls.add(href)

            text = a.get_text(" ", strip=True)

            if not text:
                text = "Відкрити посилання"

            result.append({
                "link": href,
                "text": text,
            })

    return result

# Отримання PDF-файлів екзаменів

async def fetch_pdf_links() -> list[str]:

    soup = await get_soup(url_ispyt)

    if soup is None:
        return []

    pdf_links: list[str] = []

    for a in soup.find_all("a", href=True):

        raw_url = get_attr(a, "href")

        if not is_pdf(raw_url):
            continue

        href = absolute_url(
            url_ispyt,
            raw_url,
        )

        if href:
            pdf_links.append(href)

    return unique_urls(pdf_links)
