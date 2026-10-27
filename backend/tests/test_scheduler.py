import pytest

from app.scheduler import (
    ANCHOR_JOB_ID,
    DEFAULT_ANCHOR_INTERVAL_SECONDS,
    DEFAULT_RTM_INTERVAL_SECONDS,
    MIN_ANCHOR_INTERVAL_SECONDS,
    MIN_RTM_INTERVAL_SECONDS,
    RTM_SCRAPE_JOB_ID,
    build_scheduler,
    get_job_interval,
    set_job_interval,
)


@pytest.fixture()
def scheduler():
    s = build_scheduler()
    s.start()
    yield s
    s.shutdown(wait=False)


def test_build_scheduler_registers_expected_jobs(scheduler):
    job_ids = {job.id for job in scheduler.get_jobs()}
    assert job_ids == {"dam_scrape", "rtm_scrape", "settlement_check", "price_ledger_check", "anchor_chain_heads"}


def test_constants():
    assert ANCHOR_JOB_ID == "anchor_chain_heads"
    assert DEFAULT_ANCHOR_INTERVAL_SECONDS == 900
    assert MIN_ANCHOR_INTERVAL_SECONDS == 300
    assert DEFAULT_RTM_INTERVAL_SECONDS == 30
    assert MIN_RTM_INTERVAL_SECONDS == 10


def test_rtm_scrape_defaults_to_thirty_seconds(scheduler):
    assert get_job_interval(scheduler, RTM_SCRAPE_JOB_ID) == 30


def test_anchor_defaults_to_nine_hundred_seconds(scheduler):
    assert get_job_interval(scheduler, ANCHOR_JOB_ID) == 900


@pytest.mark.parametrize(
    "job_id,minimum,seconds",
    [(RTM_SCRAPE_JOB_ID, MIN_RTM_INTERVAL_SECONDS, 120), (ANCHOR_JOB_ID, MIN_ANCHOR_INTERVAL_SECONDS, 3600)],
)
def test_set_job_interval_reschedules_the_job(scheduler, job_id, minimum, seconds):
    set_job_interval(scheduler, job_id, seconds, minimum)
    assert get_job_interval(scheduler, job_id) == seconds


@pytest.mark.parametrize(
    "job_id,minimum", [(RTM_SCRAPE_JOB_ID, MIN_RTM_INTERVAL_SECONDS), (ANCHOR_JOB_ID, MIN_ANCHOR_INTERVAL_SECONDS)]
)
def test_set_job_interval_accepts_exact_minimum(scheduler, job_id, minimum):
    set_job_interval(scheduler, job_id, minimum, minimum)
    assert get_job_interval(scheduler, job_id) == minimum


@pytest.mark.parametrize(
    "job_id,minimum", [(RTM_SCRAPE_JOB_ID, MIN_RTM_INTERVAL_SECONDS), (ANCHOR_JOB_ID, MIN_ANCHOR_INTERVAL_SECONDS)]
)
def test_set_job_interval_rejects_below_minimum(scheduler, job_id, minimum):
    with pytest.raises(ValueError, match=str(minimum)):
        set_job_interval(scheduler, job_id, minimum - 1, minimum)
    assert get_job_interval(scheduler, job_id) != minimum - 1


def test_set_job_interval_rejects_negative_and_zero(scheduler):
    for value in (0, -5):
        with pytest.raises(ValueError):
            set_job_interval(scheduler, ANCHOR_JOB_ID, value, MIN_ANCHOR_INTERVAL_SECONDS)
