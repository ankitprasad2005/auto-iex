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


def test_trigger_scrape_parse_failure_returns_502_with_cors_headers(client, monkeypatch):
    # Regression test: an unhandled exception (any exception FastAPI's
    # router doesn't recognize as an HTTPException) unwinds past
    # CORSMiddleware without getting CORS headers attached, which a browser
    # reports as an opaque "Failed to fetch" rather than surfacing the real
    # status code. Every expected scraper failure mode must be caught and
    # converted to a proper HTTPException so CORS headers are preserved.
    import app.api.scrape as scrape_module
    from app.scraper.parser import TableParseError

    def _raise(session, market, d):
        raise TableParseError("no time-block rows found for market DAM")

    monkeypatch.setattr(scrape_module, "scrape_and_record", _raise)
    resp = client.post(
        "/scrape/DAM",
        params={"date": "2026-09-10"},
        headers={"Origin": "http://localhost:5173"},
    )
    assert resp.status_code == 502
    assert resp.headers.get("access-control-allow-origin") == "*"


def test_trigger_scrape_unexpected_failure_returns_502_with_cors_headers(client, monkeypatch):
    import app.api.scrape as scrape_module

    def _raise(session, market, d):
        raise RuntimeError("something the scraper didn't anticipate")

    monkeypatch.setattr(scrape_module, "scrape_and_record", _raise)
    resp = client.post(
        "/scrape/DAM",
        params={"date": "2026-09-10"},
        headers={"Origin": "http://localhost:5173"},
    )
    assert resp.status_code == 502
    assert resp.headers.get("access-control-allow-origin") == "*"
