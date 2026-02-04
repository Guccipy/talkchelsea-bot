import os
import requests
from bs4 import BeautifulSoup
from textwrap import wrap

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = "https://chelseablues.ruru"
NEWS_URL = "https://chelseablues.ru/news"

HEADERS = {"User-Agent": "Mozilla/5.0"}

MAX_CAPTION = 900
MAX_MESSAGE = 3500
LAST_POST_FILE = "last_post.txt"


def get_all_post_links():
    r = requests.get(NEWS_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.select(".newsline-tab-item-title a"):
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

    title = soup.select_one("h1.entry-title").get_text(strip=True)

    img = soup.select_one(".entry-poster img")
    image_url = BASE_URL + img["src"] if img["src"].startswith("/") else img["src"]

    content = soup.select_one(".entry-message")
    blocks = []

    for tag in content.find_all(["p", "h3"]):
        text = tag.get_text(" ", strip=True)
        if not text:
            continue

        if tag.name == "h3":
            blocks.append(f"\n🙂 <b>{text}</b>\n")
        else:
            blocks.append(text)

    full_text = "\n\n".join(blocks)
    return title, full_text, image_url


def send_photo(image, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": image,
        "caption": caption,
        "parse_mode": "HTML"
    })


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
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

    title, text, image = get_post_data(new_link)

    first = text[:MAX_CAPTION]
    rest = text[MAX_CAPTION:]

    caption = f"<b>{title}</b>\n\n{first}"
    send_photo(image, caption)

    if rest:
        parts = wrap(rest, MAX_MESSAGE)
        for i, part in enumerate(parts):
            prefix = "\n📄 <b>Davomi:</b>\n\n" if i == 0 else ""
            send_message(prefix + part)

    save_last_sent(new_link)


if __name__ == "__main__":
    main()
