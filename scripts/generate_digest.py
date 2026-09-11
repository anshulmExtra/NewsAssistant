"""Render the fetched, summarized articles into a static HTML digest."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from fetch_news import Article

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def render_digest(
    topics: dict[str, list[Article]],
    summaries: dict[str, str],
    output_path: Path,
) -> None:
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)
    template = env.get_template("digest.html.jinja")

    for articles in topics.values():
        for article in articles:
            article.published = (
                dt.datetime.fromtimestamp(article.published_ts).strftime("%b %d, %Y")
                if article.published_ts
                else ""
            )

    html = template.render(
        generated_at=dt.datetime.now().strftime("%A, %B %d, %Y"),
        topics=topics,
        summaries=summaries,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
