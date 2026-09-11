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

## Using a paid subscription (e.g. Economic Times)

RSS feeds only show a short teaser for paywalled articles. If you have a
paid subscription, the bot can fetch the full article page using your
logged-in session cookie instead of just the RSS excerpt.

1. Log into the source's website in your browser (e.g.
   economictimes.indiatimes.com) with your paid account.
2. Open browser DevTools → Network tab, reload the page, click any request
   to that domain, and copy the full value of the `Cookie` request header.
3. Add it as a GitHub secret named `ET_SESSION_COOKIE` (Settings → Secrets
   and variables → Actions). For local runs, `export ET_SESSION_COOKIE="..."`.
4. Make sure the source is listed under `authenticated_sources` in
   `config.yaml`, pointing at the secret's env var name.

Notes:
- Session cookies expire (typically days to weeks). If digest entries from
  that source go back to short snippets, re-copy a fresh cookie.
- Treat this cookie like a password — anyone with it can access your
  account. Only store it as a GitHub secret, never commit it to the repo.
- Full-text extraction uses a CSS selector (`scripts/fetch_full_text.py`)
  that may need updating if the site changes its page layout.
- This is intended for your own personal use of content you're already
  entitled to read — check the source's terms of service before relying on
  automated access at scale.

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
