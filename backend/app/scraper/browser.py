import logging
import time as time_module

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

SNAPSHOT_URLS = {
    "DAM": "https://www.iexindia.com/market-data/day-ahead-market/market-snapshot",
    "RTM": "https://www.iexindia.com/market-data/real-time-market/market-snapshot",
}

MIN_ROWS = {"DAM": 96, "RTM": 1}
MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 2


class ScrapeError(Exception):
    pass


def _extract_table_rows(page) -> list[list[str]]:  # pragma: no cover
    page.wait_for_selector("table tbody tr", timeout=15000)
    rows = page.query_selector_all("table tbody tr")
    return [[cell.inner_text().strip() for cell in row.query_selector_all("td")] for row in rows]


def _fetch_once(market: str) -> list[list[str]]:  # pragma: no cover
    # Drives a real headless browser against the live IEX site; excluded from
    # unit coverage on purpose, exercised via manual/integration runs instead.
    url = SNAPSHOT_URLS[market]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, timeout=20000)
            return _extract_table_rows(page)
        finally:
            browser.close()


def fetch_snapshot_rows(
    market: str,
    fetch_fn=None,
    sleep=time_module.sleep,
    min_rows: int | None = None,
) -> list[list[str]]:
    fetch_fn = fetch_fn or (lambda: _fetch_once(market))
    min_rows = min_rows if min_rows is not None else MIN_ROWS[market]
    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            rows = fetch_fn()
            if len(rows) < min_rows:
                raise ScrapeError(f"partial table for {market}: got {len(rows)} rows, expected at least {min_rows}")
            return rows
        except (PlaywrightTimeoutError, ScrapeError) as exc:
            last_error = exc
            logger.warning("scrape attempt %d/%d failed for %s: %s", attempt, MAX_ATTEMPTS, market, exc)
            if attempt < MAX_ATTEMPTS:
                sleep(RETRY_BACKOFF_SECONDS * attempt)

    raise ScrapeError(f"failed to scrape {market} after {MAX_ATTEMPTS} attempts") from last_error
