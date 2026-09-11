# NewsAssistant

A daily news digest bot: it pulls articles from your favorite RSS feeds,
filters them by your favorite topics, summarizes each one with Claude, and
publishes a clean static page you can check every morning.

## How it works

1. `scripts/fetch_news.py` downloads every feed in `config.yaml` and
   filters entries whose title/description match one of your topics.
2. `scripts/summarize.py` sends each selected article to Claude for a
   2-3 sentence summary.
3. `scripts/generate_digest.py` renders everything into
   `output/index.html` using `templates/digest.html.jinja`.
4. `.github/workflows/daily-digest.yml` runs this automatically every day
   and publishes `output/` to GitHub Pages.

## Setup

1. **Personalize `config.yaml`** — add your favorite sources (as RSS feed
   URLs) and your favorite topics (as keywords to match against
   headlines/descriptions).
2. **Add an API key secret** — in the repo's Settings → Secrets and
   variables → Actions, add `ANTHROPIC_API_KEY` with a valid
   [Anthropic API](https://console.anthropic.com/) key.
3. **Enable GitHub Pages** — in Settings → Pages, set Source to
   "GitHub Actions".
4. The workflow runs daily at 12:00 UTC (edit the `cron` line in
   `.github/workflows/daily-digest.yml` to change the time), or trigger it
   manually from the Actions tab ("Run workflow").

## Running locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/main.py
```

This writes `output/index.html`, which you can open directly in a browser.

## Notes / next steps

- Topic matching is a simple keyword search over RSS title/description.
  For finer-grained filtering you could add full-article-text extraction
  or LLM-based relevance scoring.
- Sources are limited to what publishes an RSS feed. Swapping in a paid
  news API (NewsAPI, GNews, etc.) would broaden coverage at the cost of
  an extra API key and usage limits.
