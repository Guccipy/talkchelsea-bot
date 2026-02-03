import os
import requests
from bs4 import BeautifulSoup
import telebot

# ====== CONFIG ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = "https://chelseablues.ru"
NEWS_URL = "https://chelseablues.ru/news"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ChelseaBot/1.0)"
}

bot = telebot.TeleBot(BOT_TOKEN)


# ====== TEXT SPLITTER ======
def split_text(text, limit=900):
    parts = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip()
    parts.append(text)
    return parts


# ====== GET LATEST POST LINK ======
def get_latest_post_link():
    r = requests.get(NEWS_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    first_post = soup.select_one(".newsline-tab-item-title a")
    if not first_post:
        raise Exception("Yangilik topilmadi")

    return first_post["href"]


# ====== PARSE POST DATA ======
def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    # Sarlavha
    title = soup.select_one("h1.entry-title").get_text(strip=True)

    # Rasm
    img_tag = soup.select_one(".entry-poster img")
    image_url = BASE_URL + img_tag["src"]

    # Matn
    content = soup.select_one(".entry-message")
    paragraphs = content.find_all("p")

    text_parts = []
    for p in paragraphs:
        txt = p.get_text(strip=True)
        if txt:
            text_parts.append(txt)

    full_text = "\n\n".join(text_parts)

    return title, full_text, image_url


# ====== MAIN ======
def main():
    post_link = get_latest_post_link()
    title, text, image = get_post_data(post_link)

    parts = split_text(text)

    # 1-xabar
    caption_1 = f"📰 {title}\n\n{parts[0]}"
    bot.send_photo(
        chat_id=CHAT_ID,
        photo=image,
        caption=caption_1
    )

    # Davomi bo‘lsa
    if len(parts) > 1:
        caption_2 = "🧵 Davomi:\n\n" + "\n\n".join(parts[1:])
        bot.send_photo(
            chat_id=CHAT_ID,
            photo=image,
            caption=caption_2
        )


if __name__ == "__main__":
    main()
