# auto-iex

auto-iex is a consumer-side platform for bulk electricity buyers on the Indian
Energy Exchange (IEX). A Playwright robot (the RPA part of the project) opens
the IEX market-snapshot pages on a schedule and scrapes the Day-Ahead Market
(DAM) and Real-Time Market (RTM) prices. The user enters predicted consumption
as time ranges with a load in kW; the app samples those ranges into the 96
fifteen-minute blocks of the day and compares the cost of buying under DAM,
RTM and a hybrid strategy. When each range's start time arrives (IST), the app
executes a simulated purchase and settles it into a settlement ledger. Every
scrape, settlement and recorded price block is stored in a SHA-256
hash-chained ledger that is shown and verified in the UI, and the ledger heads
can optionally be anchored to the Polygon Amoy public testnet.

**Course:** Robotic Process Automation, Semester 07, VIT Chennai
**Team:** Ankit Prasad (23BRS1303), Cathie Ignatius Andrea (23BRS1286)

---

## 1. Features

- **RPA price scraper**: a headless Chromium robot (Playwright) scrapes the IEX
  DAM and RTM market-snapshot pages.
- **Scheduler**: DAM is scraped daily at 13:00 IST (for the next delivery day);
  RTM is scraped every 30 seconds. The RTM interval is editable from the UI
  (minimum 10 s). All schedules run on IST.
- **Manual scrape**: "Scrape DAM now" / "Scrape RTM now" buttons.
- **Consumption planner**: enter ranges such as 06:00-09:00 at 4500 kW; they are
  split into 96 x 15-minute blocks.
- **Cost comparison**: total cost under DAM, RTM and hybrid (per block, the
  cheaper of DAM and RTM), shown in rupees with two decimals. Blocks with no
  price yet are counted as pending.
- **Simulated purchase and settlement**: at each range's start time (IST) the
  purchase is executed (simulated) and written to the settlement ledger.
- **Three SHA-256 hash chains**, each viewable and verifiable in the UI:
  - scrape audit chain (one block per scrape),
  - settlement ledger (one block per settled range),
  - price ledger (one block per 15-minute price block as its delivery time arrives).
- **Billing tab**: a "Load demo data" button generates a fabricated, reproducible
  30-day billing month for demonstration.
- **Testnet anchoring (optional)**: publishes the three chain heads to Polygon
  Amoy every 15 minutes (editable, minimum 300 s) and verifies them against the
  on-chain transaction. Disabled when no key is configured.

> **Note:** Bid submission to the exchange is **simulated**. Placing real orders
> on IEX requires going through a registered exchange trader member.

---

## 2. Tech stack

| Layer | Technology |
|---|---|
| RPA / scraping | Playwright (Python) 1.47 with headless Chromium |
| Backend API | Python, FastAPI 0.115, Uvicorn, SQLAlchemy 2.0, Pydantic 2 |
| Scheduling | APScheduler 3.10 (IST timezone) |
| Database | PostgreSQL 16 (Docker); SQLite for tests |
| Frontend | React 18, TypeScript, Vite 5, Tailwind CSS 3 |
| Web server / proxy | nginx (serves the frontend, proxies `/api/` to the backend) |
| Blockchain anchoring | web3.py 7 on Polygon Amoy testnet (chain id 80002) |
| Tests | pytest + pytest-cov (backend), Vitest + Testing Library + v8 coverage (frontend) |
| Deployment | Docker Compose (three services: `db`, `backend`, `frontend`) |

---

## 3. What to install

### Recommended: run with Docker

| Tool | Check the version |
|---|---|
| Docker Engine (20.10 or newer) | `docker --version` |
| Docker Compose v2 (the `docker compose` plugin) | `docker compose version` |
| git (only if cloning) | `git --version` |

An internet connection is required: the robot scrapes the live IEX website.
The Docker build downloads the Playwright base image (Chromium is already inside
it), so nothing else needs to be installed on the host.

### Optional: run without Docker, or run the tests

| Tool | Check the version |
|---|---|
| Python 3.11 or newer | `python3 --version` |
| Node.js 20 or newer | `node --version` |
| npm | `npm --version` |
| Playwright Chromium (installed through pip, see section 7) | `.venv/bin/playwright --version` |

---

## 4. How to run (Docker, step by step)

1. **Get the code.** Either unzip the submitted folder, or clone it:
   ```bash
   git clone <repository-url> auto-iex
   cd auto-iex
   ```

2. **Create the environment file.**
   ```bash
   cp .env.example .env
   ```

3. **Set the database password.** Generate a random password:
   ```bash
   openssl rand -hex 32
   ```
   Open `.env` and put that value in **both** places (they must match):
   ```env
   POSTGRES_PASSWORD=<generated-password>
   DATABASE_URL=postgresql+psycopg2://autoiex:<generated-password>@db:5432/autoiex
   ```
   Leave `POSTGRES_USER=autoiex`, `POSTGRES_DB=autoiex` and `DAM_SCRAPE_HOUR=13`
   as they are.

4. **(Optional) Enable testnet anchoring.** Leave `ANCHOR_PRIVATE_KEY` empty to
   keep anchoring disabled (everything else works without it). To enable it,
   create a **throwaway, testnet-only** wallet, fund it with free test POL from a
   Polygon Amoy faucet, and set:
   ```env
   ANCHOR_PRIVATE_KEY=0x<private-key-of-the-test-wallet>
   ```
   The other `ANCHOR_*` values (`ANCHOR_RPC_URL`, `ANCHOR_CHAIN_ID=80002`,
   `ANCHOR_EXPLORER_TX_URL`) already point at Polygon Amoy. Never use a key that
   holds real funds.

5. **Build and start the stack.**
   ```bash
   docker compose up -d --build
   ```
   The first build takes a few minutes.

6. **Find the port.** Only the frontend is published, on a random free host port:
   ```bash
   docker compose port frontend 80
   ```
   Example output: `0.0.0.0:32768` (the port is `32768`).

7. **Open the app** at `http://localhost:<port>`, for example
   `http://localhost:32768`.

8. **Stop the stack** when done:
   ```bash
   docker compose down
   ```
   Data stays in the `db_data` volume and is there again on the next
   `docker compose up -d`.

**How it is wired:** the backend and the database are not published to the
host. The browser only talks to the frontend's nginx, which forwards every
`/api/...` request to the backend (`http://backend:8000`) inside the Compose
network. So the API is reachable from the host at `http://localhost:<port>/api/...`.

### Running without Docker (optional)

```bash
# Terminal 1 - backend (uses a local SQLite file instead of PostgreSQL)
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
DATABASE_URL=sqlite:///./autoiex.db .venv/bin/uvicorn app.main:app --port 8000

# Terminal 2 - frontend
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```
Open the URL Vite prints (normally `http://localhost:5173`). In this mode the
API is at `http://localhost:8000` (no `/api` prefix).

---

## 5. Using the app

All times in the UI are IST.

**Dashboard**
1. Click **Scrape DAM now** and **Scrape RTM now**. The "last scraped" time
   updates; an error is shown if the IEX site could not be reached.
2. Optionally change the **RTM polling interval** (seconds) and the
   **Testnet anchor interval** (seconds) and click **Update**.
3. Pick the **Delivery date** (for example today).
4. Add consumption ranges with **Start time**, **End time** and **Predicted kW**,
   clicking **Add range** each time, for example:
   - 06:00 to 09:00, 4500 kW
   - 12:00 to 15:00, 6000 kW
   - 18:00 to 21:00, 5200 kW
5. The comparison below shows the DAM, RTM and hybrid totals and the number of
   pending blocks (blocks that have no price yet). Ranges can be removed from the
   list; the comparison updates automatically.

**Prices** - choose a date to see the 96 blocks with DAM and RTM prices
(Rs/MWh) as a chart and a table.

**Chain** - the scrape audit chain drawn as linked blocks. Each block shows its
index, timestamp, payload, previous hash and hash.

**Ledger** - the settlement ledger. Once the start time of a range has passed,
it is settled automatically within one minute (or click **Check now**). Each row
shows the range, predicted kW, energy (kWh), market used, cost (Rs), status
(SETTLED, or PARTIAL if some blocks had no price yet) and settlement time.

**Price Ledger** - every 15-minute block of today is recorded with its price as
its delivery time arrives. Click **Check now** to record due blocks immediately.

**Billing** - click **Load demo data** to generate a fabricated 30-day billing
history (fixed seed, so it is the same every time) with date, time, market,
energy and cost, plus totals.

**Testnet** - shows whether anchoring is enabled, the network (Polygon Amoy),
and the wallet address. Click **Anchor now** to publish the current three chain
heads, open the transaction on the explorer, and click **Verify** to confirm the
on-chain data still matches the local ledgers (VALID or TAMPERED). If
`ANCHOR_PRIVATE_KEY` is empty, this tab says anchoring is disabled.

---

## 6. Sample input and output files

The `samples/` folder holds files captured from a real run on **2026-10-27**.

| File | Content |
|---|---|
| `samples/input/consumption_scenario.json` | Body for `POST /scenarios`: three ranges, 06:00-09:00 at 4500 kW, 12:00-15:00 at 6000 kW, 18:00-21:00 at 5200 kW |
| `samples/output/dam_prices_2026-10-27.csv` | Scraped DAM prices, 15-minute blocks (`block_start, block_end, mcp_rs_per_mwh`) |
| `samples/output/rtm_prices_2026-10-27.csv` | Scraped RTM prices, same columns |
| `samples/output/comparison_2026-10-27.json` | DAM / RTM / hybrid cost comparison for the scenario |
| `samples/output/settlement_ledger.json` | Settlement ledger hash chain |
| `samples/output/scrape_chain.json` | Scrape audit hash chain |
| `samples/output/price_ledger.json` | Price ledger hash chain |
| `samples/output/chain_verify.json` | Verification results of the three chains |
| `samples/output/billing_history.csv` | Demo billing month |

### Reproducing them

With the Docker stack running, set the base URL (replace the port with the one
from `docker compose port frontend 80`) and the date. `jq` is used to convert
JSON to CSV; install it if needed (`jq --version`).

```bash
BASE=http://localhost:32768/api
DATE=2026-10-27
mkdir -p out
```

Scrape the prices and save them as CSV:
```bash
curl -s -X POST "$BASE/scrape/DAM?date=$DATE"
curl -s -X POST "$BASE/scrape/RTM?date=$DATE"

for M in DAM RTM; do
  curl -s "$BASE/prices?date=$DATE&market=$M" \
    | jq -r '["block_start","block_end","mcp_rs_per_mwh"], (.[] | [.block_start, .block_end, .mcp_rs_per_mwh]) | @csv' \
    > "out/$(echo $M | tr A-Z a-z)_prices_$DATE.csv"
done
```

Create the scenario and get its comparison (the response of `POST /scenarios`
is `{"id": ..., "name": ...}`):
```bash
ID=$(curl -s -X POST "$BASE/scenarios" \
  -H "Content-Type: application/json" \
  -d @samples/input/consumption_scenario.json | jq .id)

curl -s "$BASE/scenarios/$ID/comparison?date=$DATE" > "out/comparison_$DATE.json"
```

Save the three hash chains and their verification results:
```bash
curl -s "$BASE/chain"        > out/scrape_chain.json
curl -s "$BASE/ledger"       > out/settlement_ledger.json
curl -s "$BASE/price-ledger" > out/price_ledger.json

jq -n \
  --argjson scrape     "$(curl -s $BASE/chain/verify)" \
  --argjson settlement "$(curl -s $BASE/ledger/verify)" \
  --argjson price      "$(curl -s $BASE/price-ledger/verify)" \
  '{scrape_chain: $scrape, settlement_ledger: $settlement, price_ledger: $price}' \
  > out/chain_verify.json
```
Each verify endpoint returns `{"valid": true, "invalid_block_index": null}` when
the chain is intact.

Load the demo billing month and save it as CSV:
```bash
curl -s -X POST "$BASE/billing/demo"
curl -s "$BASE/billing/history" \
  | jq -r '["date","time_label","market","kwh","cost_rs"], (.records[] | [.date, .time_label, .market, .kwh, .cost_rs]) | @csv' \
  > out/billing_history.csv
```

Notes:
- The settlement ledger only fills once a range's start time has passed on the
  current IST date (the scheduler checks every minute; `POST /ledger/check`
  forces a check). The scenario created last is the one that gets settled.
- The price ledger records today's blocks as their time arrives
  (`POST /price-ledger/check` forces a check).
- Prices for a date only exist after IEX publishes them; DAM prices for the next
  day are published in the early afternoon IST.

### API endpoints used

| Method and path | Purpose |
|---|---|
| `POST /scrape/{market}?date=YYYY-MM-DD` | Run the robot now (`market` is `DAM` or `RTM`) |
| `GET /prices?date=YYYY-MM-DD&market=DAM` | Stored 15-minute prices |
| `POST /scenarios` | Save consumption ranges |
| `GET /scenarios/{id}/comparison?date=YYYY-MM-DD` | DAM / RTM / hybrid cost comparison |
| `GET /chain`, `GET /chain/verify` | Scrape audit chain |
| `GET /ledger`, `GET /ledger/verify`, `POST /ledger/check` | Settlement ledger |
| `GET /price-ledger`, `GET /price-ledger/verify`, `POST /price-ledger/check` | Price ledger |
| `POST /billing/demo`, `GET /billing/history` | Demo billing data |
| `GET`/`PATCH /scheduler/rtm-interval`, `GET`/`PATCH /scheduler/anchor-interval` | Scheduler intervals (`{"seconds": N}`) |
| `GET /anchors/status`, `GET /anchors`, `POST /anchors/now`, `GET /anchors/{id}/verify` | Testnet anchoring |

Through Docker, prefix every path with `http://localhost:<port>/api`.

---

## 7. Running the tests

The tests do not need Docker, the database or internet access (the backend
tests use an in-memory SQLite database and do not contact IEX).

**Backend** (265 tests, 99% coverage):
```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium
.venv/bin/pytest --cov=app --cov-report=term-missing --cov-fail-under=95
```

**Frontend** (156 tests, 99% line coverage):
```bash
cd frontend
npm install
npm test                      # run all tests once
npx vitest run --coverage     # run with a coverage report
```

---

## 8. Project structure

```
auto-iex/
├── docker-compose.yml         # db (PostgreSQL), backend, frontend
├── .env.example               # copy to .env
├── samples/
│   ├── input/                 # consumption_scenario.json
│   └── output/                # scraped prices, comparison, chains, billing
├── backend/
│   ├── Dockerfile             # Playwright Python image (Chromium included)
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # FastAPI app, starts the scheduler
│   │   ├── scheduler.py       # DAM / RTM / settlement / price-ledger / anchor jobs
│   │   ├── scraper/           # Playwright robot and HTML table parser
│   │   ├── pricing/           # 96 x 15-min blocks, allocation, comparison
│   │   ├── chain/             # SHA-256 hash-chain block and verification
│   │   ├── services/          # scrape, settlement, price ledger, billing, anchoring
│   │   ├── anchoring/         # Polygon Amoy payload and publisher
│   │   ├── models/            # SQLAlchemy tables and repository
│   │   └── api/               # REST routers
│   └── tests/                 # pytest suite
└── frontend/
    ├── Dockerfile             # build with Node, serve with nginx
    ├── nginx.conf.template    # serves the UI, proxies /api/ to the backend
    ├── package.json
    └── src/
        ├── App.tsx            # tabs: Dashboard, Prices, Chain, Ledger, Price Ledger, Billing, Testnet
        ├── api/               # API client and types
        ├── components/        # one component per view (with tests)
        └── lib/               # IST formatting, price series helpers
```

---

## 9. Troubleshooting

**The app shows "Failed to fetch" / the backend keeps restarting after changing
`POSTGRES_PASSWORD`.**
PostgreSQL only reads `POSTGRES_PASSWORD` the first time it initializes an empty
data volume; on later starts it ignores the variable. If you change the password
in `.env` after the stack has run once, the backend can no longer log in.
Also make sure the password inside `DATABASE_URL` matches. Reset the volume so
PostgreSQL re-initializes with the current password:
```bash
docker compose down
docker volume ls | grep db_data      # normally auto-iex_db_data
docker volume rm auto-iex_db_data
docker compose up -d
```
This deletes the locally stored prices, ledgers and demo data; they are
re-created by scraping again.

**Which port is the app on?**
The port is random. Run `docker compose port frontend 80` or `docker compose ps`.
It can change after `docker compose down` / `up`.

**Scrape fails (error under the scrape button, or HTTP 502 from `/scrape`).**
The robot needs internet access to `www.iexindia.com`. Check the connection and
try again; the site may also be slow or temporarily unavailable. Look at the
backend log with `docker compose logs backend`.

**Comparison shows pending blocks or zero totals.**
No prices are stored yet for that date and market. Scrape the market first, and
remember DAM prices for tomorrow only appear after IEX publishes them (around
13:00 IST).

**Testnet tab says anchoring is disabled / `/anchors/now` returns 503.**
`ANCHOR_PRIVATE_KEY` is empty in `.env`. This is the default and is fine. To
enable it, set the key of a funded test wallet and run `docker compose up -d`
again so the backend picks up the change.

**Anchor rows show "failed".**
Usually the test wallet has insufficient funds for gas (hover the row to see the
error). Top it up from a Polygon Amoy faucet and click **Anchor now** again.
"No change since last anchor" means the chain heads have not changed since the last confirmed
anchor, so nothing new was published.
