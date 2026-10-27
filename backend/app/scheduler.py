from datetime import date, datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from .anchoring.publisher import get_publisher
from .config import DAM_SCRAPE_HOUR
from .db import SessionLocal
from .pricing.time_utils import IST, to_market_time
from .services.anchor_service import anchor_chain_heads
from .services.price_ledger_service import check_and_record_price_blocks
from .services.scrape_service import scrape_and_record
from .services.settlement_service import check_and_settle_due_ranges

RTM_SCRAPE_JOB_ID = "rtm_scrape"
DEFAULT_RTM_INTERVAL_SECONDS = 30
MIN_RTM_INTERVAL_SECONDS = 10
ANCHOR_JOB_ID = "anchor_chain_heads"
DEFAULT_ANCHOR_INTERVAL_SECONDS = 900
MIN_ANCHOR_INTERVAL_SECONDS = 300


def market_date(date_offset: int, now: datetime) -> date:
    return to_market_time(now).date() + timedelta(days=date_offset)


def _run_scrape(market: str, date_offset: int) -> None:  # pragma: no cover
    session = SessionLocal()
    try:
        scrape_and_record(session, market, market_date(date_offset, datetime.now(timezone.utc)))
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


def _run_anchor() -> None:  # pragma: no cover
    publisher = get_publisher()
    if publisher is None:
        return
    session = SessionLocal()
    try:
        anchor_chain_heads(session, publisher, datetime.now(timezone.utc))
    finally:
        session.close()


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=IST)
    scheduler.add_job(lambda: _run_scrape("DAM", 1), "cron", hour=DAM_SCRAPE_HOUR, minute=0, id="dam_scrape")
    scheduler.add_job(
        lambda: _run_scrape("RTM", 0), "interval", seconds=DEFAULT_RTM_INTERVAL_SECONDS, id=RTM_SCRAPE_JOB_ID
    )
    scheduler.add_job(_run_settlement_check, "interval", minutes=1, id="settlement_check")
    scheduler.add_job(_run_price_ledger_check, "interval", minutes=1, id="price_ledger_check")
    scheduler.add_job(_run_anchor, "interval", seconds=DEFAULT_ANCHOR_INTERVAL_SECONDS, id=ANCHOR_JOB_ID)
    return scheduler


def get_job_interval(scheduler: BackgroundScheduler, job_id: str) -> int:
    return int(scheduler.get_job(job_id).trigger.interval.total_seconds())


def set_job_interval(scheduler: BackgroundScheduler, job_id: str, seconds: int, minimum: int) -> None:
    if seconds < minimum:
        raise ValueError(f"interval must be at least {minimum} seconds")
    scheduler.reschedule_job(job_id, trigger="interval", seconds=seconds)
