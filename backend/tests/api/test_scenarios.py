from datetime import date, time
from decimal import Decimal

from app.models.repository import upsert_price_blocks
from app.scraper.parser import PriceBlockRecord


def test_post_scenario_creates_and_returns_id(client):
    resp = client.post(
        "/scenarios",
        json={"name": "evening", "ranges": [{"start_time": "18:00", "end_time": "19:00", "predicted_kw": 4.0}]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "evening"
    assert isinstance(body["id"], int)


def test_post_scenario_invalid_range_returns_422(client):
    resp = client.post(
        "/scenarios",
        json={"name": "bad", "ranges": [{"start_time": "19:00", "end_time": "18:00", "predicted_kw": 4.0}]},
    )
    assert resp.status_code == 422


def test_get_comparison_for_unknown_scenario_returns_404(client):
    resp = client.get("/scenarios/9999/comparison", params={"date": "2026-09-10"})
    assert resp.status_code == 404


def test_get_comparison_returns_full_breakdown(client, db_session):
    upsert_price_blocks(
        db_session,
        [PriceBlockRecord(date=date(2026, 9, 10), market="DAM", block_start=time(0, 0), block_end=time(0, 15), mcp_rs_per_mwh=Decimal("4000"))],
    )
    create_resp = client.post(
        "/scenarios",
        json={"name": "morning", "ranges": [{"start_time": "00:00", "end_time": "00:15", "predicted_kw": 4.0}]},
    )
    scenario_id = create_resp.json()["id"]

    resp = client.get(f"/scenarios/{scenario_id}/comparison", params={"date": "2026-09-10"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["blocks"]) == 96
    assert body["blocks"][0]["dam_cost_rs"] == "4.00"
    assert body["dam_pending_blocks"] == 95
