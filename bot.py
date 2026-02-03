import requests
from bs4 import BeautifulSoup
import os

BOT_TOKEN = os.environ["8156145088:AAFPCh1S5aZDdByyEViD8n6U26MXNkksz4s"]
CHAT_ID = os.environ["999639255"]

SITE_URL = "https://www.talkchelsea.net/"
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


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    })


def get_latest_post():
    r = requests.get(SITE_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    article = soup.find("article", class_="cs-entry__featured")
    if not article:
        return None, None

    title = article.find("h2").get_text(strip=True)
    link = article.find("a", class_="cs-overlay-link")["href"]

    return title, link


title, link = get_latest_post()

if not link:
    print("❌ Post topilmadi")
    exit()

last = get_last_link()
if link == last:
    print("⏭ Oldin yuborilgan")
    exit()

msg = f"📰 NEW POST (EN)\n\n{title}\n\n{link}"
send_message(msg)
save_last_link(link)

print("✅ Yangi post yuborildi")
