import requests
import os
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

BASE_URL = "https://chelseablues.ru"
LAST_FILE = "last_link.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_last_link():
    if os.path.exists(LAST_FILE):
        return open(LAST_FILE).read().strip()
    return ""


def save_last_link(link):
    open(LAST_FILE, "w").write(link)


def get_latest_post_link():
    r = requests.get(BASE_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    first_post = soup.select_one(".news-item-title a")
    if not first_post:
        return None

    return BASE_URL + first_post["href"]


def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("h1").get_text(strip=True)

    image = soup.select_one(".news-view-hero img")
    image_url = BASE_URL + image["src"] if image else None

    content_block = soup.select_one(".news-text")
    paragraphs = content_block.find_all("p")

    full_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs)

    return title, full_text, image_url


def send_photo(caption, photo):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": photo,
        "caption": caption[:1024]
    })


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text[:4096]
    })


def main():
    post_link = get_latest_post_link()
    if not post_link:
        print("❌ Post topilmadi")
        return

    if post_link == get_last_link():
        print("⏭ Yangi post yo‘q")
        return

    title, text, image = get_post_data(post_link)

    caption = f"📰 {title}\n\n{text}\n\n🔗 {post_link}"

    if image:
        send_photo(caption, image)
    else:
        send_message(caption)

    save_last_link(post_link)
    print("✅ Yangi post yuborildi")


if __name__ == "__main__":
    main()


