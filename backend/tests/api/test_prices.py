from datetime import date, time
from decimal import Decimal

from app.models.repository import upsert_price_blocks
from app.scraper.parser import PriceBlockRecord


def test_read_prices_returns_stored_blocks(client, db_session):
    upsert_price_blocks(
        db_session,
        [PriceBlockRecord(date=date(2026, 9, 10), market="DAM", block_start=time(0, 0), block_end=time(0, 15), mcp_rs_per_mwh=Decimal("3245.50"))],
    )
    resp = client.get("/prices", params={"date": "2026-09-10", "market": "DAM"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["mcp_rs_per_mwh"] == "3245.5000"


def test_read_prices_invalid_date_returns_422(client):
    resp = client.get("/prices", params={"date": "not-a-date", "market": "DAM"})
    assert resp.status_code == 422


def test_read_prices_no_data_returns_empty_list(client):
    resp = client.get("/prices", params={"date": "2026-01-01", "market": "DAM"})
    assert resp.status_code == 200
    assert resp.json() == []
