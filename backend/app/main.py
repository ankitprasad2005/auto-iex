from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.chain import router as chain_router
from .api.prices import router as prices_router
from .api.scenarios import router as scenarios_router
from .api.scrape import router as scrape_router
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
app.include_router(prices_router)
app.include_router(scenarios_router)
app.include_router(scrape_router)
app.include_router(chain_router)
