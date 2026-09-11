"""Summarize each article with the Anthropic API."""

from __future__ import annotations

from fetch_news import Article

SUMMARY_PROMPT = """Summarize the following news article in 2-3 concise sentences \
for a daily digest. Stick to the facts present in the text below, and do not \
speculate beyond it.

Title: {title}
Source: {source}
Excerpt: {description}"""


def summarize_articles(client, model: str, articles: list[Article]) -> dict[str, str]:
    """Return a map of article link -> generated summary."""
    summaries: dict[str, str] = {}
    for article in articles:
        if article.link in summaries:
            continue
        summaries[article.link] = _summarize_one(client, model, article)
    return summaries


def _summarize_one(client, model: str, article: Article) -> str:
    if not article.description:
        return article.title

    response = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": SUMMARY_PROMPT.format(
                    title=article.title,
                    source=article.source,
                    description=article.description,
                ),
            }
        ],
    )
    return response.content[0].text.strip()
