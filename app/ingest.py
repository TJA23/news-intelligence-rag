"""News article ingestion: fetch from RSS feeds, deduplicate, persist."""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import feedparser
import httpx
from bs4 import BeautifulSoup

from app.config import ARTICLES_PATH, MAX_ARTICLES_PER_FEED, RSS_FEEDS

USER_AGENT = "Mozilla/5.0 (compatible; NewsIntelligenceRAG/0.1; +https://github.com/TJA23/news-intelligence-rag)"


def _clean_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def _hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _load_existing(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return {a["id"]: a for a in json.load(f)}


def _http_get(url: str, timeout: float = 15.0) -> bytes:
    with httpx.Client(
        follow_redirects=True,
        timeout=timeout,
        headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml, */*"},
    ) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.content


def fetch_feed(source: str, url: str, limit: int = MAX_ARTICLES_PER_FEED) -> list[dict]:
    raw = _http_get(url)
    parsed = feedparser.parse(raw)
    items: list[dict] = []
    for entry in parsed.entries[:limit]:
        title = (entry.get("title") or "").strip()
        summary = _clean_html(entry.get("summary", ""))
        link = entry.get("link", "")
        published = entry.get("published", "") or entry.get("updated", "")
        if not title or not summary:
            continue
        items.append(
            {
                "id": _hash(link or title),
                "source": source,
                "title": title,
                "url": link,
                "published": published,
                "text": summary,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return items


def ingest_all(feeds=None) -> dict:
    feeds = feeds or RSS_FEEDS
    existing = _load_existing(ARTICLES_PATH)
    new_count = 0
    per_source: dict[str, int] = {}

    for source, url in feeds:
        try:
            articles = fetch_feed(source, url)
        except Exception as exc:
            per_source[source] = -1
            print(f"  ! {source}: failed ({exc})")
            continue
        added = 0
        for art in articles:
            if art["id"] not in existing:
                existing[art["id"]] = art
                added += 1
        per_source[source] = added
        new_count += added

    with open(ARTICLES_PATH, "w", encoding="utf-8") as f:
        json.dump(list(existing.values()), f, ensure_ascii=False, indent=2)

    return {
        "total_in_corpus": len(existing),
        "new_articles": new_count,
        "per_source": per_source,
    }
