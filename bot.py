import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SITE_URL = "https://chelseablues.ru"
NEWS_LIST = "https://chelseablues.ru/news"
LAST_FILE = "last.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TG_CAPTION_LIMIT = 900   # xavfsiz limit

def get_last():
    if os.path.exists(LAST_FILE):
        return open(LAST_FILE).read().strip()
    return ""

def save_last(link):
    open(LAST_FILE, "w").write(link)

def get_latest_post():
    r = requests.get(NEWS_LIST, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    a = soup.select_one(".newsline-tab-item-title a")

    title = a.text.strip()
    link = a["href"]

    # agar link to‘liq bo‘lsa — o‘zgartirmaymiz
    if link.startswith("http"):
        return title, link

    # aks holda saytni qo‘shamiz
    return title, SITE_URL + link


def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("h1.entry-title").text.strip()
    image = SITE_URL + soup.select_one(".entry-poster img")["src"]

    content = soup.select_one(".entry-message")
    paragraphs = [p.get_text(" ", strip=True) for p in content.find_all("p")]
    text = "\n\n".join(paragraphs)

    return title, text, image

def send_photo(caption, image):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": image,
        "caption": caption
    })

def send_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

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

def main():
    title, link = get_latest_post()

    if link == get_last():
        print("⏭ Old post")
        return

    title, text, image = get_post_data(link)
    parts = split_text(text, TG_CAPTION_LIMIT)

    # 1-xabar
    send_photo(
        f"📰 {title}\n\n{parts[0]}\n\n➡️ Davomi ⬇️",
        image
    )

    # qolganlari
    for part in parts[1:]:
        send_photo(part, image)

    save_last(link)
    print("✅ Sent")

if __name__ == "__main__":
    main()

