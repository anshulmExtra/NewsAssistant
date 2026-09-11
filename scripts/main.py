"""Entry point: fetch -> filter -> summarize -> render the daily digest."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml
from anthropic import Anthropic

from fetch_news import fetch_all_entries, group_by_topic
from generate_digest import render_digest
from summarize import summarize_articles

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"
OUTPUT_PATH = ROOT / "output" / "index.html"


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

    client = Anthropic(api_key=api_key)
    summaries = summarize_articles(client, config["model"], all_selected)

    render_digest(topics, summaries, OUTPUT_PATH)
    print(f"Digest written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
