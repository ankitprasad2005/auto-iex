from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.chain import router as chain_router
from .api.ledger import router as ledger_router
from .api.price_ledger import router as price_ledger_router
from .api.prices import router as prices_router
from .api.scenarios import router as scenarios_router
from .api.scheduler_settings import router as scheduler_settings_router
from .api.scrape import router as scrape_router
from .config import CORS_ALLOWED_ORIGINS
from .db import init_db
from .scheduler import build_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    init_db()
    scheduler = build_scheduler()
    scheduler.start()
    app.state.scheduler = scheduler
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="auto-iex", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS.split(",") if CORS_ALLOWED_ORIGINS != "*" else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(prices_router)
app.include_router(scenarios_router)
app.include_router(scrape_router)
app.include_router(chain_router)
app.include_router(ledger_router)
app.include_router(price_ledger_router)
app.include_router(scheduler_settings_router)
