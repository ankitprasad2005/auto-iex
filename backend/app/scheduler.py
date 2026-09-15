from datetime import date, datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from .config import DAM_SCRAPE_HOUR
from .db import SessionLocal
from .services.price_ledger_service import check_and_record_price_blocks
from .services.scrape_service import scrape_and_record
from .services.settlement_service import check_and_settle_due_ranges

RTM_SCRAPE_JOB_ID = "rtm_scrape"
DEFAULT_RTM_INTERVAL_SECONDS = 30
MIN_RTM_INTERVAL_SECONDS = 10


def _run_scrape(market: str, date_offset: int) -> None:  # pragma: no cover
    session = SessionLocal()
    try:
        scrape_and_record(session, market, date.today() + timedelta(days=date_offset))
    finally:
        session.close()


def _run_settlement_check() -> None:  # pragma: no cover
    session = SessionLocal()
    try:
        check_and_settle_due_ranges(session, datetime.now(timezone.utc))
    finally:
        session.close()


def _run_price_ledger_check() -> None:  # pragma: no cover
    session = SessionLocal()
    try:
        check_and_record_price_blocks(session, datetime.now(timezone.utc))
    finally:
        session.close()


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: _run_scrape("DAM", 1), "cron", hour=DAM_SCRAPE_HOUR, minute=0, id="dam_scrape")
    scheduler.add_job(
        lambda: _run_scrape("RTM", 0), "interval", seconds=DEFAULT_RTM_INTERVAL_SECONDS, id=RTM_SCRAPE_JOB_ID
    )
    scheduler.add_job(_run_settlement_check, "interval", minutes=1, id="settlement_check")
    scheduler.add_job(_run_price_ledger_check, "interval", minutes=1, id="price_ledger_check")
    return scheduler


def get_rtm_scrape_interval(scheduler: BackgroundScheduler) -> int:
    job = scheduler.get_job(RTM_SCRAPE_JOB_ID)
    return int(job.trigger.interval.total_seconds())


def set_rtm_scrape_interval(scheduler: BackgroundScheduler, seconds: int) -> None:
    if seconds < MIN_RTM_INTERVAL_SECONDS:
        raise ValueError(f"interval must be at least {MIN_RTM_INTERVAL_SECONDS} seconds")
    scheduler.reschedule_job(RTM_SCRAPE_JOB_ID, trigger="interval", seconds=seconds)
