import os
import requests
from bs4 import BeautifulSoup
from textwrap import wrap

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = "https://www.sports.ru"
NEWS_URL = "https://www.sports.ru/football/club/chelsea/news/"

HEADERS = {"User-Agent": "Mozilla/5.0"}

MAX_MESSAGE = 3500
LAST_POST_FILE = "last_post.txt"


# ================== GET NEWS LINKS ==================

def get_all_post_links():
    r = requests.get(NEWS_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for p in soup.select(".news p.one_news a.short-text"):
        href = p.get("href")
        if not href:
            continue
        if href.startswith("http"):
            links.append(href)
        else:
            links.append(BASE_URL + href)

    return links


# ================== LAST SENT ==================

def get_last_sent():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            return f.read().strip()
    return None


def save_last_sent(link):
    with open(LAST_POST_FILE, "w") as f:
        f.write(link)


# ================== PARSE ARTICLE ==================

def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    title_tag = soup.select_one("h1")
    title = title_tag.get_text(" ", strip=True) if title_tag else "Chelsea News"

    article = soup.select_one(".news-item__content, article, .content")
    if not article:
        return title, None

    blocks = []
    for p in article.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) > 25:
            blocks.append(text)

    full_text = "\n\n".join(blocks)
    return title, full_text


# ================== TELEGRAM ==================

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    })


# ================== MAIN ==================

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

    # 1️⃣ Header
    header = f"<b>{title}</b>\n\n{new_link}"
    send_message(header)

    if not text:
        save_last_sent(new_link)
        return

    # 2️⃣ Full text (split)
    parts = wrap(text, MAX_MESSAGE)
    for i, part in enumerate(parts):
        prefix = "\n📄 <b>Davomi:</b>\n\n" if i == 0 else ""
        send_message(prefix + part)

    save_last_sent(new_link)


if __name__ == "__main__":
    main()

