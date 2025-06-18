import httpx
from bs4 import BeautifulSoup
import asyncio

url_rating = "https://pk-nuk.com.ua/rejtingovi-spiski-zdobuvachiv-osviti/"

async def fetch_rating_links():
    timeout = 5
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url_rating, timeout=timeout)
            response.raise_for_status()
    except httpx.RequestError as e:
        print(f"Сервер не відповідає або недоступний: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    rating_block = soup.find("div", class_="elementor-widget-container")

    if not rating_block:
        print("Блок .elementor-widget-container не найден.")
        return []

    rating_links = []
    p_tags = rating_block.find_all("p")

    if not p_tags:
        print("Внутри блока нет <p> тегов.")
    else:
        print(f"Найдено {len(p_tags)} <p> тегов.")

    for p in p_tags:
        a_tag = p.find("a")
        if a_tag and a_tag.get("href"):
            link = a_tag["href"]
            print(f"Найдена ссылка: {link}")
            rating_links.append(link)

    return rating_links

# Тестовый запуск
if __name__ == "__main__":
    links = asyncio.run(fetch_rating_links())
    print("Все найденные ссылки:")
    print(links)
