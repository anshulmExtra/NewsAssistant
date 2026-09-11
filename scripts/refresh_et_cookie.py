"""Local helper: log into Economic Times yourself (email/phone + OTP) in a
real browser window, and have this script automatically grab the resulting
session cookie for you -- no digging through DevTools required.

Economic Times requires an OTP at login, so this cannot run unattended in
CI. Run it on your own machine whenever the daily digest starts showing
paywalled snippets again (i.e. the saved cookie has expired), then paste
the printed value into the ET_SESSION_COOKIE GitHub secret.

Usage:
    pip install -r requirements-refresh.txt
    playwright install chromium
    python scripts/refresh_et_cookie.py
"""

from __future__ import annotations

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://economictimes.indiatimes.com"
COOKIE_DOMAIN_HINT = "indiatimes.com"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL)

        print("A browser window has opened.")
        print("Log in normally there (email/phone + OTP), then come back here.")
        input("Press Enter once you're logged in... ")

        cookies = [c for c in context.cookies() if COOKIE_DOMAIN_HINT in c["domain"]]
        browser.close()

    if not cookies:
        raise SystemExit("No cookies found -- did the login succeed?")

    cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

    print("\nCopy the value below into the ET_SESSION_COOKIE GitHub secret")
    print("(repo Settings -> Secrets and variables -> Actions):\n")
    print(cookie_header)


if __name__ == "__main__":
    main()
