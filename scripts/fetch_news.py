#!/usr/bin/env python3
import html
import json
import re
import urllib.parse
from collections import OrderedDict
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import List
from urllib.request import Request, urlopen
from xml.etree import ElementTree


TOPICS = [
    {"name": "OpenAI", "query": "OpenAI", "tag": "openai"},
    {"name": "OpenClaw", "query": "OpenClaw", "tag": "openclaw"},
]
MAX_ITEMS = 24
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0 Safari/537.36"


def parse_pub_date(value: str):
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return None


def strip_html(raw: str):
    if not raw:
        return ""
    without_tags = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(without_tags).strip()


def source_domain(url: str):
    if not url:
        return "Google News"
    match = re.search(r"https?://([^/]+)", url)
    if not match:
        return "Google News"
    host = match.group(1).replace("www.", "")
    return host.split(":")[0]


def fetch_rss(topic_name: str, query: str, tag: str) -> List[dict]:
    base = "https://news.google.com/rss/search"
    params = {
        "q": query,
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en",
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    req = Request(
        url,
        headers={
            "User-Agent": UA,
        },
    )
    try:
        with urlopen(req, timeout=20) as resp:
            xml_bytes = resp.read()
    except Exception as exc:
        print(f"Unable to fetch topic '{topic_name}': {exc}")
        return []

    try:
        root = ElementTree.fromstring(xml_bytes)
    except Exception as exc:
        print(f"Invalid RSS payload for '{topic_name}': {exc}")
        return []
    items = []
    for item in root.findall(".//item"):
        title_el = item.findtext("title", "")
        link_el = item.findtext("link", "")
        pub_el = item.findtext("pubDate", "")
        desc_el = item.findtext("description", "")

        title = html.unescape((title_el or "").strip())
        if not title:
            continue

        summary = strip_html(desc_el)
        if summary and len(summary) > 200:
            summary = summary[:197] + "…"

        items.append(
            {
                "title": title,
                "url": (link_el or "").strip(),
                "source": source_domain(link_el),
                "publishedAt": parse_pub_date(pub_el),
                "summary": summary,
                "topic": tag,
                "topicLabel": topic_name,
            }
        )

    return items


def dedupe(items):
    by_url = OrderedDict()
    by_title = OrderedDict()

    for item in items:
        key_url = (item.get("url") or "").strip()
        key_title = (item.get("title") or "").strip().lower()
        if key_url and key_url in by_url:
            continue
        if key_title and key_title in by_title:
            continue
        if key_url:
            by_url[key_url] = item
            by_title[key_title] = True
        else:
            by_title[key_title] = True
            by_url[f"title::{key_title}"] = item
        yield item


def main():
    all_items = []
    for topic in TOPICS:
        all_items.extend(fetch_rss(topic["name"], topic["query"], topic["tag"]))

    deduped = list(dedupe(all_items))
    deduped.sort(
        key=lambda x: x.get("publishedAt") or "",
        reverse=True,
    )
    keep = deduped[:MAX_ITEMS]

    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "topics": [topic["tag"] for topic in TOPICS],
        "items": keep,
    }

    out_path = Path(__file__).resolve().parents[1] / "data" / "news.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
