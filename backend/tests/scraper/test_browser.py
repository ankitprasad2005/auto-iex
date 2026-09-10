import pytest

from app.scraper.browser import fetch_snapshot_rows, ScrapeError


def test_fetch_snapshot_rows_succeeds_first_try():
    calls = []

    def fetch_fn():
        calls.append(1)
        return [["row"]] * 96

    sleeps = []
    rows = fetch_snapshot_rows("DAM", fetch_fn=fetch_fn, sleep=sleeps.append)
    assert len(rows) == 96
    assert len(calls) == 1
    assert sleeps == []


def test_fetch_snapshot_rows_retries_then_succeeds():
    attempts = {"n": 0}

    def fetch_fn():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ScrapeError("temporary failure")
        return [["row"]]

    sleeps = []
    rows = fetch_snapshot_rows("RTM", fetch_fn=fetch_fn, sleep=sleeps.append)
    assert len(rows) == 1
    assert attempts["n"] == 3
    assert len(sleeps) == 2


def test_fetch_snapshot_rows_exhausts_retries_and_raises():
    def fetch_fn():
        raise ScrapeError("permanent failure")

    sleeps = []
    with pytest.raises(ScrapeError):
        fetch_snapshot_rows("RTM", fetch_fn=fetch_fn, sleep=sleeps.append)
    assert len(sleeps) == 2  # MAX_ATTEMPTS(3) - 1


def test_fetch_snapshot_rows_empty_table_treated_as_failure():
    def fetch_fn():
        return []

    sleeps = []
    with pytest.raises(ScrapeError):
        fetch_snapshot_rows("RTM", fetch_fn=fetch_fn, sleep=sleeps.append)


def test_fetch_snapshot_rows_partial_dam_table_treated_as_failure():
    def fetch_fn():
        return [["row"]] * 50  # DAM expects 96

    sleeps = []
    with pytest.raises(ScrapeError):
        fetch_snapshot_rows("DAM", fetch_fn=fetch_fn, sleep=sleeps.append)


def test_fetch_snapshot_rows_rtm_accepts_partial_session_data():
    def fetch_fn():
        return [["row"]]  # RTM min_rows is 1, so this is fine

    rows = fetch_snapshot_rows("RTM", fetch_fn=fetch_fn, sleep=lambda s: None)
    assert len(rows) == 1
