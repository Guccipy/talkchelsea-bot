import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = "https://chelseablues.ru"
NEWS_URL = "https://chelseablues.ru/news"
LAST_FILE = "last_link.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

PHOTO_LIMIT = 900
TEXT_LIMIT = 3800


# ===== last_link =====
def get_last_link():
    if os.path.exists(LAST_FILE):
        return open(LAST_FILE).read().strip()
    return ""


def save_last_link(link):
    with open(LAST_FILE, "w") as f:
        f.write(link)


# ===== eng oxirgi yangilik linki =====
def get_latest_post_link():
    r = requests.get(NEWS_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    item = soup.select_one(".newsline-tab-item-title a")
    if not item:
        return None

    link = item["href"]
    if link.startswith("/"):
        link = BASE_URL + link

    return link


# ===== post ichidan data =====
def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1", class_="entry-title").get_text(strip=True)

    img_tag = soup.select_one("figure.entry-poster img")
    image = BASE_URL + img_tag["src"]

    content = soup.find("div", class_="entry-message")
    blocks = content.find_all(["p", "h3"])

    text_parts = []
    for block in blocks:
        if block.name == "h3":
            section = block.get_text(strip=True)
            text_parts.append(f"\n<b>• {section}</b>\n")
        else:
            txt = block.get_text(" ", strip=True)
            if txt:
                text_parts.append(txt)

    full_text = "\n\n".join(text_parts)
    return title, full_text, image


# ===== text bo‘lish =====
def split_text(text, limit):
    parts = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut == -1:
            cut = limit
        parts.append(text[:cut])
        text = text[cut:].strip()
    parts.append(text)
    return parts


# ===== telegram =====
def send_photo(caption, image):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": image,
        "caption": caption,
        "parse_mode": "HTML"
    })


def send_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    })


# ===== MAIN =====
def main():
    latest_link = get_latest_post_link()
    if not latest_link:
        print("❌ Yangilik topilmadi")
        return

    last_link = get_last_link()
    if latest_link == last_link:
        print("⏭ Yangi post yo‘q")
        return

    title, text, image = get_post_data(latest_link)

    first_parts = split_text(f"📰 <b>{title}</b>\n\n{text}", PHOTO_LIMIT)
    send_photo(first_parts[0], image)

    if len(first_parts) > 1:
        rest_text = "\n\n".join(first_parts[1:])
        rest_parts = split_text(rest_text, TEXT_LIMIT)

        for part in rest_parts:
            send_text(f"⏩ <i>Davomi:</i>\n\n{part}")

    save_last_link(latest_link)
    print("✅ Yangi post yuborildi")


if __name__ == "__main__":
    main()

