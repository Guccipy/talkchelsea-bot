import os
import requests
from bs4 import BeautifulSoup
import subprocess

# ====== ENV ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GH_TOKEN = os.getenv("GH_TOKEN")

BASE_URL = "https://chelseablues.ru"
NEWS_LIST = "https://chelseablues.ru/news"
LAST_FILE = "last_link.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ====== HELPERS ======
def read_last():
    if os.path.exists(LAST_FILE):
        return open(LAST_FILE, "r", encoding="utf-8").read().strip()
    return ""

def save_last(link):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(link)

def auto_commit():
    subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
    subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True)

    repo = os.environ.get("GITHUB_REPOSITORY")
    subprocess.run([
        "git", "remote", "set-url", "origin",
        f"https://x-access-token:{GH_TOKEN}@github.com/{repo}.git"
    ], check=True)

    subprocess.run(["git", "add", LAST_FILE], check=True)
    subprocess.run(["git", "commit", "-m", "update last_link"], check=True)
    subprocess.run(["git", "push"], check=True)

# ====== GET LATEST POST ======
def get_latest_link():
    r = requests.get(NEWS_LIST, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    a = soup.select_one(".newsline-tab-item-title a")
    return BASE_URL + a["href"]

# ====== PARSE POST ======
def get_post_data(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.select_one("h1.entry-title").get_text(strip=True)
    image = soup.select_one("figure.entry-poster img")["src"]
    if image.startswith("/"):
        image = BASE_URL + image

    blocks = soup.select(".entry-message p, .entry-message h3")

    parts = []
    for b in blocks:
        text = b.get_text(" ", strip=True)
        if b.name == "h3":
            parts.append(f"🟦 <b>{text}</b>")
        else:
            parts.append(text)

    return title, "\n\n".join(parts), image

# ====== TELEGRAM ======
def send_photo(caption, photo):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": photo,
        "caption": caption[:1020],
        "parse_mode": "HTML"
    })

def send_text(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    })

# ====== MAIN ======
def main():
    last = read_last()
    link = get_latest_link()

    if link == last:
        print("⏭ Eski post, chiqildi")
        return

    title, text, image = get_post_data(link)

    chunks = [text[i:i+3500] for i in range(0, len(text), 3500)]

    send_photo(f"📰 <b>{title}</b>\n\n{chunks[0]}", image)

    for part in chunks[1:]:
        send_text("📄 <b>Davomi:</b>\n\n" + part)

    save_last(link)
    auto_commit()

if __name__ == "__main__":
    main()


