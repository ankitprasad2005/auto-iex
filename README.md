# auto-iex

Scrapes IEX Day-Ahead and Real-Time Market electricity prices, maps predicted
consumption ranges onto 15-minute price blocks, and records every scrape in a
hash-chained ledger visualized in the UI.

## Run locally

1. Copy `.env.example` to `.env` and adjust values if needed.
2. `docker compose up --build`
3. Frontend: http://localhost:3000 — Backend API: http://localhost:8000

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
