from datetime import date, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from .config import DAM_SCRAPE_HOUR
from .db import SessionLocal
from .services.scrape_service import scrape_and_record


def _run_scrape(market: str, date_offset: int) -> None:  # pragma: no cover
    session = SessionLocal()
    try:
        scrape_and_record(session, market, date.today() + timedelta(days=date_offset))
    finally:
        session.close()


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: _run_scrape("DAM", 1), "cron", hour=DAM_SCRAPE_HOUR, minute=0, id="dam_scrape")
    scheduler.add_job(lambda: _run_scrape("RTM", 0), "interval", minutes=15, id="rtm_scrape")
    return scheduler
