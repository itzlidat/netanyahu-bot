"""
Netanyahu Alert Bot
Checks Google News RSS for new articles mentioning Netanyahu,
sends new ones to a Telegram chat, and keeps track of what's
already been sent (so nothing gets repeated) in seen.json.
"""

import os
import json
import feedparser
import requests

RSS_URL = "https://news.google.com/rss/search?q=Netanyahu&hl=en-US&gl=US&ceid=US:en"
SEEN_FILE = "seen.json"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": False
    })
    resp.raise_for_status()


def main():
    feed = feedparser.parse(RSS_URL)
    seen = load_seen()
    new_seen = set(seen)
    new_items = []

    for entry in feed.entries:
        article_id = entry.get("id") or entry.link
        if article_id not in seen:
            new_items.append(entry)
            new_seen.add(article_id)

    for entry in reversed(new_items):
        message = f"{entry.title}\n{entry.link}"
        send_telegram(message)

    if new_items:
        save_seen(new_seen)
        print(f"Sent {len(new_items)} new article(s).")
    else:
        print("No new articles.")


if __name__ == "__main__":
    main()