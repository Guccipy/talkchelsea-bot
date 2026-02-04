import os
import requests
import feedparser
import subprocess

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_URL = "https://feeds.bbci.co.uk/sport/football/rss.xml"
LAST_FILE = "last_id.txt"


def get_last_id():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_last_id(post_id):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        f.write(post_id)


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=20,
    )


def git_commit():
    try:
        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(
            ["git", "config", "user.email", "github-actions@github.com"], check=True
        )
        subprocess.run(["git", "add", LAST_FILE], check=True)
        subprocess.run(
            ["git", "commit", "-m", "update last BBC post id"], check=True
        )
        subprocess.run(["git", "push"], check=True)
        print("✅ last_id.txt commit qilindi")
    except subprocess.CalledProcessError:
        print("ℹ️ O‘zgarish yo‘q, commit qilinmadi")


def main():
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("❌ RSS bo‘sh")
        return

    post = feed.entries[0]

    post_id = post.get("id") or post.get("link")
    last_id = get_last_id()

    if post_id == last_id:
        print("⏭ Yangi xabar yo‘q")
        return

    title = post.get("title", "No title")
    summary = post.get("summary", "")
    link = post.get("link", "")

    message = (
        f"📰 <b>{title}</b>\n\n"
        f"{summary}\n\n"
        f"👉 <a href=\"{link}\">BBC’da o‘qish</a>"
    )

    send_message(message)
    save_last_id(post_id)
    git_commit()

    print("🚀 Yangi BBC xabari yuborildi")


if __name__ == "__main__":
    main()
