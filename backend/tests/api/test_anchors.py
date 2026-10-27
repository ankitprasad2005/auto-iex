from datetime import datetime, timezone

import pytest

from app import config
from app.api.anchors import get_anchor_publisher
from app.main import app
from app.models.tables import ChainBlockModel, PriceLedgerBlockModel
from tests.anchoring.fake_publisher import FakePublisher

Z = "0" * 64
ANCHOR_KEYS = {
    "id", "created_at", "scrape_head_index", "scrape_head_hash", "settlement_head_index", "settlement_head_hash",
    "price_ledger_head_index", "price_ledger_head_hash", "tx_hash", "status", "block_number", "error",
    "explorer_url",
}


@pytest.fixture()
def publisher(client):
    pub = FakePublisher()
    app.dependency_overrides[get_anchor_publisher] = lambda: pub
    return pub


@pytest.fixture()
def disabled(client):
    app.dependency_overrides[get_anchor_publisher] = lambda: None


def _seed(session):
    now = datetime.now(timezone.utc)
    session.add(ChainBlockModel(index=0, timestamp=now, payload_json={}, prev_hash=Z, hash="a0" * 32))
    session.add(PriceLedgerBlockModel(index=0, timestamp=now, payload_json={}, prev_hash=Z, hash="c0" * 32))
    session.commit()


def test_status_enabled(client, publisher):
    resp = client.get("/anchors/status")
    assert resp.status_code == 200
    assert resp.json() == {
        "enabled": True, "network": "Polygon Amoy", "chain_id": config.ANCHOR_CHAIN_ID,
        "wallet_address": publisher.address, "explorer_tx_url": config.ANCHOR_EXPLORER_TX_URL,
    }


def test_status_disabled(client, disabled):
    resp = client.get("/anchors/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["enabled"] is False
    assert body["wallet_address"] is None
    assert body["network"] == "Polygon Amoy"


def test_default_dependency_reflects_config(client, monkeypatch):
    monkeypatch.setattr(config, "ANCHOR_PRIVATE_KEY", "")
    assert client.get("/anchors/status").json()["enabled"] is False
    monkeypatch.setattr(config, "ANCHOR_PRIVATE_KEY", "0x" + "11" * 32)
    assert client.get("/anchors/status").json()["enabled"] is True


def test_list_empty(client, publisher):
    resp = client.get("/anchors")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_works_when_disabled(client, disabled):
    assert client.get("/anchors").status_code == 200


def test_anchor_now_then_list(client, db_session, publisher):
    _seed(db_session)
    resp = client.post("/anchors/now")
    assert resp.status_code == 200
    body = resp.json()
    assert body["anchored"] is True and body["reason"] is None
    anchor = body["anchor"]
    assert set(anchor) == ANCHOR_KEYS
    assert anchor["status"] == "confirmed"
    assert anchor["scrape_head_index"] == 0 and anchor["scrape_head_hash"] == "a0" * 32
    assert anchor["settlement_head_index"] == -1 and anchor["settlement_head_hash"] == Z
    assert anchor["price_ledger_head_index"] == 0
    assert anchor["explorer_url"] == config.ANCHOR_EXPLORER_TX_URL + anchor["tx_hash"]
    assert anchor["error"] is None
    assert datetime.fromisoformat(anchor["created_at"]).tzinfo is not None

    listed = client.get("/anchors").json()
    assert listed == [anchor]


def test_anchor_now_unchanged(client, db_session, publisher):
    _seed(db_session)
    client.post("/anchors/now")
    resp = client.post("/anchors/now")
    assert resp.status_code == 200
    assert resp.json() == {"anchored": False, "reason": "unchanged", "anchor": None}


def test_anchor_now_failed(client, db_session, publisher):
    publisher.error = RuntimeError("insufficient funds for gas")
    resp = client.post("/anchors/now")
    assert resp.status_code == 200
    body = resp.json()
    assert body["anchored"] is False and body["reason"] == "failed"
    assert body["anchor"]["status"] == "failed"
    assert body["anchor"]["tx_hash"] is None
    assert body["anchor"]["explorer_url"] is None
    assert "insufficient funds" in body["anchor"]["error"]


def test_anchor_now_disabled(client, disabled):
    resp = client.post("/anchors/now")
    assert resp.status_code == 503
    assert resp.json() == {"detail": "anchoring not configured"}


def test_list_newest_first(client, db_session, publisher):
    client.post("/anchors/now")
    _seed(db_session)
    client.post("/anchors/now")
    ids = [a["id"] for a in client.get("/anchors").json()]
    assert ids == sorted(ids, reverse=True) and len(ids) == 2


def test_verify_valid(client, db_session, publisher):
    _seed(db_session)
    anchor_id = client.post("/anchors/now").json()["anchor"]["id"]
    resp = client.get(f"/anchors/{anchor_id}/verify")
    assert resp.status_code == 200
    assert resp.json() == {
        "valid": True, "on_chain_matches_record": True, "ledger_matches_record": True, "mismatches": [],
    }


def test_verify_tampered(client, db_session, publisher):
    _seed(db_session)
    anchor_id = client.post("/anchors/now").json()["anchor"]["id"]
    db_session.get(PriceLedgerBlockModel, 0).hash = "11" * 32
    db_session.commit()
    body = client.get(f"/anchors/{anchor_id}/verify").json()
    assert body["valid"] is False
    assert body["mismatches"] == ["price ledger block 0 hash changed since anchoring"]


def test_verify_unknown_404(client, publisher):
    assert client.get("/anchors/999/verify").status_code == 404


def test_verify_failed_anchor_409(client, publisher):
    publisher.error = RuntimeError("down")
    anchor_id = client.post("/anchors/now").json()["anchor"]["id"]
    assert client.get(f"/anchors/{anchor_id}/verify").status_code == 409


def test_verify_disabled_503(client, disabled):
    resp = client.get("/anchors/1/verify")
    assert resp.status_code == 503
    assert resp.json() == {"detail": "anchoring not configured"}


def test_verify_non_integer_id_422(client, publisher):
    assert client.get("/anchors/abc/verify").status_code == 422
