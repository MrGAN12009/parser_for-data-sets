import requests
from bs4 import BeautifulSoup
import sqlite3

# Указываем URL
url = "https://belabraziv.ru"
count = 0

# Подключение к SQLite
with sqlite3.connect("database.db") as db:
    sql = db.cursor()
    sql.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            source TEXT NOT NULL,
            link TEXT NOT NULL UNIQUE,
            title TEXT,
            content TEXT
        );
        """
    )
    db.commit()
    print("SQLite подключен")

visited_links = set()


def get_page_data(url):
    """Загружает страницу и извлекает данные"""
    try:
        response = requests.get(url, timeout=10)
        response.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"Ошибка запроса {url}: {e}")
        return None

    if response.status_code != 200:
        print(f"Ошибка {response.status_code} при получении {url}")
        return None

    return BeautifulSoup(response.text, "html.parser")


def get_all_links(url):
    """Рекурсивный обход ссылок"""
    global count
    if url in visited_links:
        return
    visited_links.add(url)
    count += 1
    print(f"Обрабатываем страницу {count}: {url}")

    soup = get_page_data(url)
    if not soup:
        return

    title_tag = soup.find("h1", id="pagetitle")
    title = title_tag.text.strip() if title_tag else ""
    if title == "Поиск":
        print(f"Пропущена страница {url} из-за заголовка 'Поиск'")
        return

    content_tag = soup.find("div", class_="container_inner")
    content = content_tag.get_text(strip=True, separator=" ") if content_tag else ""

    try:
        sql.execute(
            "INSERT INTO pages (source, link, title, content) VALUES (?, ?, ?, ?);",
            (url, url, title, content)
        )
        db.commit()
    except sqlite3.IntegrityError:
        pass

    # Обход ссылок
    for link in soup.find_all("a"):
        href = link.get("href")
        if not href or href.startswith("#"):
            continue
        full_url = href if href.startswith("http") else f"https://belabraziv.ru{href}"
        if full_url.startswith("https://belabraziv.ru"):
            get_all_links(full_url)


if __name__ == "__main__":
    get_all_links(url)
    print("Обход завершен!")
