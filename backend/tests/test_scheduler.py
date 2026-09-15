import pytest

from app.scheduler import (
    DEFAULT_RTM_INTERVAL_SECONDS,
    MIN_RTM_INTERVAL_SECONDS,
    build_scheduler,
    get_rtm_scrape_interval,
    set_rtm_scrape_interval,
)


def test_build_scheduler_registers_expected_jobs():
    scheduler = build_scheduler()
    scheduler.start()
    job_ids = {job.id for job in scheduler.get_jobs()}
    assert job_ids == {"dam_scrape", "rtm_scrape", "settlement_check", "price_ledger_check"}
    scheduler.shutdown(wait=False)


def test_rtm_scrape_defaults_to_thirty_seconds():
    scheduler = build_scheduler()
    scheduler.start()
    assert get_rtm_scrape_interval(scheduler) == DEFAULT_RTM_INTERVAL_SECONDS == 30
    scheduler.shutdown(wait=False)


def test_set_rtm_scrape_interval_reschedules_the_job():
    scheduler = build_scheduler()
    scheduler.start()
    set_rtm_scrape_interval(scheduler, 120)
    assert get_rtm_scrape_interval(scheduler) == 120
    scheduler.shutdown(wait=False)


def test_set_rtm_scrape_interval_rejects_too_small_a_value():
    scheduler = build_scheduler()
    scheduler.start()
    with pytest.raises(ValueError):
        set_rtm_scrape_interval(scheduler, MIN_RTM_INTERVAL_SECONDS - 1)
    scheduler.shutdown(wait=False)
