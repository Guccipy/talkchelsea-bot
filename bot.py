import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_URL = "https://chelseablues.ru"

PHOTO_LIMIT = 900      # caption limiti
TEXT_LIMIT = 3800      # sendMessage limiti


# ===== TEXTNI BO‘LISH =====
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


# ===== POST MA'LUMOTLARI =====
def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1", class_="entry-title").get_text(strip=True)

    img = soup.find("figure", class_="entry-poster").find("img")
    image_url = BASE_URL + img["src"]

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
    return title, full_text, image_url


# ===== TELEGRAM FUNKSIYALAR =====
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
    # hozircha test URL (keyin avtomatlashtiramiz)
    post_url = (
        "https://chelseablues.ru/news/"
        "ronaldu_buntuet_messi_vozvrashhaetsja_domoj_"
        "a_manchester_siti_ishhet_zamenu_gvardiole/"
        "2026-02-03-146405"
    )

    title, text, image = get_post_data(post_url)

    # 1-xabar (rasm bilan)
    first_block = split_text(f"📰 <b>{title}</b>\n\n{text}", PHOTO_LIMIT)
    send_photo(first_block[0], image)

    # qolganlari (faqat matn)
    if len(first_block) > 1:
        rest_text = "\n\n".join(first_block[1:])
        rest_parts = split_text(rest_text, TEXT_LIMIT)

        for i, part in enumerate(rest_parts):
            send_text(f"⏩ <i>Davomi:</i>\n\n{part}")


if __name__ == "__main__":
    main()
