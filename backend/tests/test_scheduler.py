from app.scheduler import build_scheduler


def test_build_scheduler_registers_expected_jobs():
    scheduler = build_scheduler()
    job_ids = {job.id for job in scheduler.get_jobs()}
    assert job_ids == {"dam_scrape", "rtm_scrape"}
    scheduler.shutdown(wait=False)
