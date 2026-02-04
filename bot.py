import os
import requests
from bs4 import BeautifulSoup
from textwrap import wrap

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = "https://www.sports.ru"
NEWS_URL = "https://www.sports.ru/football/club/chelsea/materials/"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

MAX_MESSAGE = 3500
LAST_POST_FILE = "last_post.txt"


def get_all_post_links():
    r = requests.get(NEWS_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.select("a.material-preview__link"):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("http"):
            links.append(href)
        else:
            links.append(BASE_URL + href)

    return links


def get_last_sent():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            return f.read().strip()
    return None


def save_last_sent(link):
    with open(LAST_POST_FILE, "w") as f:
        f.write(link)


def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    article = soup.select_one("article")
    if not article:
        return None, None

    title_tag = article.select_one("h1")
    title = title_tag.get_text(strip=True)

    content_blocks = []
    for tag in article.select("p, h2, h3"):
        text = tag.get_text(" ", strip=True)
        if not text:
            continue

        if tag.name in ["h2", "h3"]:
            content_blocks.append(f"\n<b>{text}</b>\n")
        else:
            content_blocks.append(text)

    full_text = "\n\n".join(content_blocks)
    return title, full_text


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })


def main():
    links = get_all_post_links()
    last_sent = get_last_sent()

    new_link = None
    for link in links:
        if link != last_sent:
            new_link = link
            break

    if not new_link:
        return

    title, text = get_post_data(new_link)
    if not title or not text:
        return

    header = f"⚽ <b>CHELSEA | Sports.ru</b>\n\n<b>{title}</b>\n"
    send_message(header)

    parts = wrap(text, MAX_MESSAGE)
    for i, part in enumerate(parts):
        prefix = "\n📄 <b>Davomi:</b>\n\n" if i > 0 else "\n\n"
        send_message(prefix + part)

    save_last_sent(new_link)


if __name__ == "__main__":
    main()



