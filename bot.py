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
print("=== SPORTS.RU BOT VERSION 2026-02-04 ===")

def get_all_post_links():
    r = requests.get(NEWS_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("/football/") and href.endswith(".html"):
            links.append(BASE_URL + href)

    # dublikatlarni olib tashlaymiz
    links = list(dict.fromkeys(links))

    print("LINKS FOUND:", len(links))
    return links


def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    # sarlavha
    title_tag = soup.select_one("h1")
    if not title_tag:
        print("NO TITLE")
        return None, None

    title = title_tag.get_text(strip=True)

    # kontent (bir nechta ehtimoliy joy)
    content = (
        soup.select_one('div[itemprop="articleBody"]')
        or soup.select_one(".news-item__content")
        or soup.select_one(".content")



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

    print("TELEGRAM STATUS:", r.status_code)
    print("TELEGRAM RESPONSE:", r.text)



def main():
    links = get_all_post_links()
    if not links:
        return

    # HAR DOIM ENG SO‘NGGI MAQOLA
    new_link = links[0]

    title, text = get_post_data(new_link)
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




