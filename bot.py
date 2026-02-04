import os
import requests
import feedparser
from bs4 import BeautifulSoup
from textwrap import wrap

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_URL = "https://www.sports.ru/football/club/chelsea/materials/rss/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

MAX_MESSAGE = 3500

print("=== SPORTS.RU RSS + FULL TEXT BOT ===")


def get_latest_link():
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("RSS EMPTY")
        return None

    link = feed.entries[0].link
    print("RSS LINK:", link)
    return link


def parse_full_article(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    article = soup.select_one("article")
    if not article:
        print("ARTICLE NOT FOUND")
        return None, None

    title_tag = article.select_one("h1")
    if not title_tag:
        return None, None

    title = title_tag.get_text(strip=True)

    blocks = []
    for tag in article.select("p, h2, h3"):
        text = tag.get_text(" ", strip=True)
        if not text:
            continue

        if tag.name in ["h2", "h3"]:
            blocks.append(f"\n<b>{text}</b>\n")
        else:
            blocks.append(text)

    full_text = "\n\n".join(blocks)
    return title, full_text


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    r = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        },
        timeout=20
    )
    print("TG STATUS:", r.status_code)


def main():
    link = get_latest_link()
    if not link:
        return

    title, text = parse_full_article(link)
    if not title or not text:
        return

    header = f"⚽ <b>CHELSEA | Sports.ru</b>\n\n<b>{title}</b>"
    send_message(header)

    parts = wrap(text, MAX_MESSAGE)
    for i, part in enumerate(parts):
        prefix = "\n📄 <b>Davomi:</b>\n\n" if i > 0 else "\n\n"
        send_message(prefix + part)


if __name__ == "__main__":
    main()





