import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

BASE_URL = "https://chelseablues.ru"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_latest_post():
    r = requests.get(BASE_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    container = soup.find("div", id="allEntries")
    first_news = container.find("div", class_="news-item")

    link = first_news.find("a")["href"]
    return BASE_URL + link

def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    # TITLE
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else "No title"

    # IMAGE
    img = soup.find("meta", property="og:image")
    image_url = img["content"] if img else None

    # CONTENT (bir nechta variant)
    content_block = (
        soup.find("div", class_="news-text")
        or soup.find("div", class_="news-item-message")
        or soup.find("div", class_="entry-content")
    )

    if not content_block:
        text = "Full article available on the website."
    else:
        paragraphs = content_block.find_all("p")
        if paragraphs:
            text = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
        else:
            text = content_block.get_text(strip=True)

    return title, text[:900], image_url


def send_to_telegram(title, text, image_url, link):
    caption = f"<b>{title}</b>\n\n{text}\n\n<a href='{link}'>Manba</a>"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": image_url,
        "caption": caption[:1024],
        "parse_mode": "HTML"
    }

    requests.post(url, data=payload)

def main():
    link = get_latest_post()
    title, text, image_url = get_post_data(link)
    send_to_telegram(title, text, image_url, link)

if __name__ == "__main__":
    main()

