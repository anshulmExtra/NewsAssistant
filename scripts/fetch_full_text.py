"""Fetch full article text for authenticated (paywalled) sources.

Some sources only expose a short teaser in their RSS feed for subscriber-only
articles. If you have a paid subscription, you can supply a logged-in session
cookie and this module will fetch the actual article page with it, so the
digest summarizes the full article instead of the paywalled snippet.
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# CSS selectors tried in order to find the article body container.
# Site markup changes over time; update these if extraction stops working.
BODY_SELECTORS = [
    "div.artText",  # Economic Times article body
    "article",
]

MAX_CHARS = 4000


def fetch_full_text(url: str, cookie: str | None) -> str | None:
    """Return the full article text, or None if it couldn't be fetched/parsed."""
    headers = {"User-Agent": USER_AGENT}
    if cookie:
        headers["Cookie"] = cookie

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for selector in BODY_SELECTORS:
        container = soup.select_one(selector)
        if not container:
            continue
        paragraphs = [p.get_text(" ", strip=True) for p in container.find_all("p")]
        text = " ".join(p for p in paragraphs if p)
        if text:
            return text[:MAX_CHARS]

    return None
