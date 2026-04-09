#!/usr/bin/env python3
"""YouTube RSS 피드에서 새 영상을 감지하고 키워드 필터링하는 스크립트."""

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
PROCESSED_PATH = PROJECT_DIR / "data" / "processed.json"

RSS_URL_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={}"

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_processed():
    if not PROCESSED_PATH.exists():
        return {"video_ids": [], "last_updated": ""}
    with open(PROCESSED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_processed(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(PROCESSED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_rss(channel_id):
    url = RSS_URL_TEMPLATE.format(channel_id)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")


def parse_feed(xml_text):
    root = ET.fromstring(xml_text)
    entries = []
    for entry in root.findall("atom:entry", NS):
        video_id = entry.find("yt:videoId", NS).text
        title = entry.find("atom:title", NS).text
        published = entry.find("atom:published", NS).text
        link = entry.find("atom:link", NS).attrib.get("href", "")
        entries.append({
            "video_id": video_id,
            "title": title,
            "published": published,
            "url": link,
        })
    return entries


def matches_keywords(title, keywords):
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)


def detect_series(title, series_map):
    for keyword, series_name in series_map.items():
        if keyword.lower() in title.lower():
            return series_name
    return ""


def main():
    config = load_config()
    processed = load_processed()
    processed_ids = set(processed["video_ids"])
    series_map = config.get("content_series_map", {})

    new_videos = []

    for channel in config["channels"]:
        channel_name = channel["name"]
        channel_id = channel["channel_id"]
        keywords = channel["keywords"]
        filter_all = channel.get("filter_all", False)

        try:
            xml_text = fetch_rss(channel_id)
        except Exception as e:
            print(f"[ERROR] {channel_name} RSS 가져오기 실패: {e}", file=sys.stderr)
            continue

        entries = parse_feed(xml_text)

        for entry in entries:
            if entry["video_id"] in processed_ids:
                continue

            if filter_all or matches_keywords(entry["title"], keywords):
                series = detect_series(entry["title"], series_map)
                if not series and filter_all:
                    series = channel_name

                new_videos.append({
                    "video_id": entry["video_id"],
                    "title": entry["title"],
                    "channel": channel_name,
                    "series": series,
                    "published": entry["published"],
                    "url": entry["url"],
                })

    output = {
        "count": len(new_videos),
        "videos": new_videos,
        "checked_at": datetime.now().isoformat(),
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
