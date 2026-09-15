# auto-iex

Scrapes IEX Day-Ahead and Real-Time Market electricity prices, maps predicted
consumption ranges onto 15-minute price blocks, and records every scrape in a
hash-chained ledger visualized in the UI.

## Run locally

1. Copy `.env.example` to `.env` and adjust values if needed.
2. `docker compose up --build`
3. Frontend: published to a random host port — find it with
   `docker compose port frontend 80` (or `docker compose ps`).

The **backend and database are not published to the host at all** — only
the frontend container is. The frontend's nginx reverse-proxies `/api/*` to
the backend over the compose network's service-name DNS
(`http://backend:8000`, set via `BACKEND_URL` in `docker-compose.yml`), so
the browser only ever talks to the frontend's origin and never needs to
resolve a Docker-internal hostname itself. See
`frontend/nginx.conf.template`.

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
