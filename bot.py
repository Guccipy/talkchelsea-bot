import os
import requests
from bs4 import BeautifulSoup
from textwrap import wrap

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = "https://chelseablues.ru"
NEWS_URL = "https://chelseablues.ru/news"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

MAX_CAPTION = 900      # rasm osti limiti (xavfsiz)
MAX_MESSAGE = 3500     # oddiy xabar limiti


def get_latest_post_link():
    r = requests.get(NEWS_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    a = soup.select_one(".newsline-tab-item-title a")
    if not a:
        return None

    link = a["href"]

    # 🔥 MUHIM FIX
    if link.startswith("http"):
        return link
    else:
        return BASE_URL + link


def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("h1.entry-title").get_text(strip=True)

    img = soup.select_one(".entry-poster img")
    image_url = BASE_URL + img["src"] if img and img.get("src", "").startswith("/") else img["src"]

    content = soup.select_one(".entry-message")
    parts = []

    for tag in content.find_all(["p", "h3"]):
        text = tag.get_text(" ", strip=True)
        if not text:
            continue

        # 🔥 h3 — JIRNIY + smayl
        if tag.name == "h3":
            text = f"🙂 <b>{text}</b>"

        parts.append(text)

    full_text = "\n\n".join(parts)
    return title, full_text, image_url


def send_photo_with_text(image, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": CHAT_ID,
        "photo": image,
        "caption": caption,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


def send_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


def main():
    link = get_latest_post_link()
    if not link:
        return

    title, text, image = get_post_data(link)

    # 1️⃣ birinchi bo‘lak — rasm bilan
    first_part = text[:MAX_CAPTION]
    rest = text[MAX_CAPTION:]

    caption = f"<b>{title}</b>\n\n{first_part}"
    send_photo_with_text(image, caption)

    # 2️⃣ qolganlari — oddiy text
    if rest:
        chunks = wrap(rest, MAX_MESSAGE)
        for i, chunk in enumerate(chunks):
            prefix = "📄 <b>Davomi:</b>\n\n" if i == 0 else ""
            send_text(prefix + chunk)


if __name__ == "__main__":
    main()
