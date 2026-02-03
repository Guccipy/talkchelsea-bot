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

    # Title
    title = soup.find("h1").get_text(strip=True)

    # Image
    img = soup.find("meta", property="og:image")
    image_url = img["content"] if img else None

    # Content
    content_block = soup.find("div", class_="news-text") \
                 or soup.find("div", class_="entry-content")

    paragraphs = content_block.find_all("p")
    text = "\n\n".join(p.get_text(strip=True) for p in paragraphs)

    return title, text, image_url

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

