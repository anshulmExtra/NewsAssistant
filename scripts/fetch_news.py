"""Fetch articles from RSS feeds and filter them against favorite topics."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Article:
    title: str
    link: str
    source: str
    description: str
    published_ts: float
    matched_topics: list[str] = field(default_factory=list)


def fetch_all_entries(sources: list[dict]) -> list[Article]:
    """Download every configured RSS feed and return a flat list of entries."""
    import feedparser

    entries: list[Article] = []
    for source in sources:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries:
            published_ts = _entry_timestamp(entry)
            entries.append(
                Article(
                    title=entry.get("title", "").strip(),
                    link=entry.get("link", ""),
                    source=source["name"],
                    description=entry.get("summary", entry.get("description", "")).strip(),
                    published_ts=published_ts,
                )
            )
    return entries


def _entry_timestamp(entry) -> float:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            return time.mktime(value)
    return 0.0


def group_by_topic(
    entries: list[Article], topics: list[str], max_per_topic: int
) -> dict[str, list[Article]]:
    """Match entries against each topic keyword and keep the most recent ones."""
    seen_links: set[str] = set()
    grouped: dict[str, list[Article]] = {}

    for topic in topics:
        keyword = topic.lower()
        matches = [
            entry
            for entry in entries
            if keyword in entry.title.lower() or keyword in entry.description.lower()
        ]
        matches.sort(key=lambda e: e.published_ts, reverse=True)

        topic_articles: list[Article] = []
        for entry in matches:
            if entry.link in seen_links:
                continue
            seen_links.add(entry.link)
            topic_articles.append(entry)
            if len(topic_articles) >= max_per_topic:
                break

        grouped[topic] = topic_articles

    return grouped
