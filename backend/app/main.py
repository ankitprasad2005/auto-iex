from fastapi import FastAPI

from .api.prices import router as prices_router
from .api.scenarios import router as scenarios_router
from .api.scrape import router as scrape_router
from .db import init_db

app = FastAPI(title="auto-iex")
app.include_router(prices_router)
app.include_router(scenarios_router)
app.include_router(scrape_router)


@app.on_event("startup")
def _startup() -> None:  # pragma: no cover
    init_db()
