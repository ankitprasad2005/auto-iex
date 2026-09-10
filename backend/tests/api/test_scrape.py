def test_trigger_scrape_success(client, monkeypatch):
    import app.api.scrape as scrape_module

    monkeypatch.setattr(scrape_module, "scrape_and_record", lambda session, market, d: {
        "written": 96, "skipped_duplicate": False,
        "chain_block": type("B", (), {"index": 1})(),
    })

    resp = client.post("/scrape/DAM", params={"date": "2026-09-10"})
    assert resp.status_code == 200
    assert resp.json() == {"written": 96, "skipped_duplicate": False, "chain_block_index": 1}


def test_trigger_scrape_invalid_market_returns_422(client):
    resp = client.post("/scrape/FOO", params={"date": "2026-09-10"})
    assert resp.status_code == 422


def test_trigger_scrape_upstream_failure_returns_502(client, monkeypatch):
    import app.api.scrape as scrape_module
    from app.scraper.browser import ScrapeError

    def _raise(session, market, d):
        raise ScrapeError("site down")

    monkeypatch.setattr(scrape_module, "scrape_and_record", _raise)
    resp = client.post("/scrape/DAM", params={"date": "2026-09-10"})
    assert resp.status_code == 502
