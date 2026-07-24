#!/usr/bin/env python3
"""
Mrs. Gordon's & Plumbing - Lead Checker
Polls Craigslist RSS feeds (Hudson Valley / Rockland County) for plumbing-related
posts, filters by keyword, and sends new matches as push notifications via ntfy.sh.

Only pulls from sources that explicitly allow automated/RSS access:
- Craigslist RSS feeds (public, no scraping involved)

Does NOT and will not pull from Thumbtack, Angi, HomeAdvisor, Yelp, or Facebook -
those platforms prohibit automated access in their terms of service.
"""

import json
import os
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------- CONFIG ----------------

# Craigslist metro + subregion for Rockland County, NY
CRAIGSLIST_BASE = "https://hudsonvalley.craigslist.org"
CRAIGSLIST_AREA = "rock"  # Rockland County subarea code on hudsonvalley.craigslist.org

# Craigslist category codes to search:
#   ggg = gigs (all)      tgs = skilled trade gigs      lbg = labor gigs
#   bbb = business/service ads wanted   ppp = "for sale" services wanted-type posts
CATEGORIES = ["ggg", "tgs", "lbg"]

# Keywords to match (case-insensitive). Edit this list freely.
KEYWORDS = [
    "plumb", "plumber", "plumbing",
    "leak", "pipe", "pipes",
    "water heater", "hot water heater",
    "drain", "clog", "clogged",
    "sump pump", "sewer", "faucet",
    "toilet repair", "water line",
]

# ntfy.sh topic - phone gets a push notification when something is posted here
NTFY_TOPIC = "mrs-gordons-plumbing-7x9k"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# Where we remember which posts we've already alerted on (committed back to repo)
STATE_FILE = Path(__file__).parent / "seen_posts.json"

# -----------------------------------------


def load_seen():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()


def save_seen(seen):
    # Keep the file from growing forever - cap at last 500 seen IDs
    trimmed = list(seen)[-500:]
    STATE_FILE.write_text(json.dumps(trimmed))


def fetch_rss(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def parse_items(rss_bytes):
    root = ET.fromstring(rss_bytes)
    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        guid = (item.findtext("guid") or link).strip()
        items.append({"title": title, "link": link, "desc": desc, "guid": guid})
    return items


def matches_keywords(item):
    text = (item["title"] + " " + item["desc"]).lower()
    return any(kw.lower() in text for kw in KEYWORDS)


def send_notification(item):
    body = f"{item['title']}\n{item['link']}"
    req = urllib.request.Request(
        NTFY_URL,
        data=body.encode("utf-8"),
        headers={
            "Title": "New plumbing lead",
            "Priority": "high",
            "Tags": "wrench",
        },
        method="POST",
    )
    urllib.request.urlopen(req, timeout=20)


def build_feed_urls():
    urls = []
    for cat in CATEGORIES:
        for kw in ["plumb", "leak", "water heater", "drain", "sewer"]:
            q = urllib.parse.quote(kw)
            urls.append(
                f"{CRAIGSLIST_BASE}/search/{CRAIGSLIST_AREA}/{cat}?query={q}&format=rss"
            )
    return urls


def main():
    seen = load_seen()
    new_matches = []
    feed_urls = build_feed_urls()

    for url in feed_urls:
        try:
            rss = fetch_rss(url)
            items = parse_items(rss)
        except Exception as e:
            print(f"[warn] failed to fetch {url}: {e}")
            continue

        for item in items:
            if item["guid"] in seen:
                continue
            if not matches_keywords(item):
                continue
            new_matches.append(item)
            seen.add(item["guid"])

    for item in new_matches:
        try:
            send_notification(item)
            print(f"[notified] {item['title']}")
        except Exception as e:
            print(f"[warn] failed to notify for {item['title']}: {e}")

    save_seen(seen)
    print(f"Done. {len(new_matches)} new lead(s) found this run.")


if __name__ == "__main__":
    main()
