# auto-iex

Scrapes IEX Day-Ahead and Real-Time Market electricity prices, maps predicted
consumption ranges onto 15-minute price blocks, and records every scrape in a
hash-chained ledger visualized in the UI.

## Run locally

1. Copy `.env.example` to `.env` and adjust values if needed.
2. `docker compose up --build`
3. Frontend: http://localhost:3000 — Backend API: http://localhost:8000

**If you change `POSTGRES_PASSWORD` after the stack has already run once:**
Postgres only applies `POSTGRES_PASSWORD` when it first initializes an empty
data directory — it ignores the env var on every subsequent start against an
existing volume. Changing the password in `.env` without resetting the
volume leaves the backend unable to authenticate (it will crash-loop, and
the frontend's API calls will fail with a generic "Failed to fetch" since
the backend never becomes reachable). Fix by resetting the volume so
Postgres re-initializes with the current password:
```bash
docker compose down
docker volume rm auto-iex_db_data
docker compose up -d
```
This discards any locally scraped/demo data in Postgres — fine for a dev
deployment, since it just gets re-scraped.

## Run backend tests

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
.venv/bin/pytest --cov=app --cov-report=term-missing --cov-fail-under=95
```

## Run frontend tests

```bash
cd frontend
npm install
npm test
```

Design spec and implementation plan: see `docs/specs/` and `docs/plans/`
(local-only, not tracked in git).
