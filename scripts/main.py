"""Entry point: fetch -> filter -> summarize -> render the daily digest."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml
from anthropic import Anthropic

from fetch_full_text import fetch_full_text
from fetch_news import fetch_all_entries, group_by_topic
from generate_digest import render_digest
from summarize import summarize_articles

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"
OUTPUT_PATH = ROOT / "output" / "index.html"


def _enrich_authenticated_sources(articles, authenticated_sources: list[dict]) -> None:
    """Replace RSS teasers with full article text for paywalled sources.

    Requires a logged-in session cookie in the environment variable named by
    each entry's `cookie_env`; sources without a cookie set are left as-is.
    """
    cookies_by_source = {
        entry["name"]: os.environ.get(entry["cookie_env"]) for entry in authenticated_sources
    }

    for article in articles:
        cookie = cookies_by_source.get(article.source)
        if not cookie:
            continue
        full_text = fetch_full_text(article.link, cookie)
        if full_text:
            article.description = full_text


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY environment variable is not set.")

    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))

    print(f"Fetching {len(config['sources'])} sources...")
    entries = fetch_all_entries(config["sources"])
    print(f"Fetched {len(entries)} total articles.")

    topics = group_by_topic(entries, config["topics"], config["max_articles_per_topic"])
    all_selected = [article for articles in topics.values() for article in articles]
    print(f"Selected {len(all_selected)} articles across {len(topics)} topics.")

    _enrich_authenticated_sources(all_selected, config.get("authenticated_sources", []))

    client = Anthropic(api_key=api_key)
    summaries = summarize_articles(client, config["model"], all_selected)

    render_digest(topics, summaries, OUTPUT_PATH)
    print(f"Digest written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
