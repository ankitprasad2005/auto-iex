from datetime import datetime, time, timezone
from decimal import Decimal

from app.chain.block import ChainBlock, GENESIS_PREV_HASH
from app.models.repository import create_scenario, save_settlement_block, upsert_price_blocks
from app.pricing.time_utils import to_market_time
from app.scraper.parser import PriceBlockRecord


def test_read_ledger_empty(client):
    resp = client.get("/ledger")
    assert resp.status_code == 200
    assert resp.json() == []


def test_read_ledger_returns_blocks(client, db_session):
    genesis = ChainBlock.create(index=0, timestamp=datetime.now(timezone.utc), payload={"genesis": True}, prev_hash=GENESIS_PREV_HASH)
    save_settlement_block(db_session, genesis)
    resp = client.get("/ledger")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["index"] == 0


def test_verify_ledger_valid_when_empty(client):
    resp = client.get("/ledger/verify")
    assert resp.status_code == 200
    assert resp.json() == {"valid": True, "invalid_block_index": None}


def test_verify_ledger_detects_tampering(client, db_session):
    genesis = ChainBlock.create(index=0, timestamp=datetime.now(timezone.utc), payload={"genesis": True}, prev_hash=GENESIS_PREV_HASH)
    save_settlement_block(db_session, genesis)
    tampered = ChainBlock.create(index=1, timestamp=datetime.now(timezone.utc), payload={"n": 1}, prev_hash="f" * 64)
    save_settlement_block(db_session, tampered)

    resp = client.get("/ledger/verify")
    body = resp.json()
    assert body["valid"] is False
    assert body["invalid_block_index"] == 1


def test_check_ledger_settles_due_ranges(client, db_session):
    create_scenario(db_session, "scenario", [(0, 15, 4.0)])  # 00:00-00:15
    upsert_price_blocks(
        db_session,
        [PriceBlockRecord(date=to_market_time(datetime.now(timezone.utc)).date(), market="DAM", block_start=time(0, 0), block_end=time(0, 15), mcp_rs_per_mwh=Decimal("4000"))],
    )

    resp = client.post("/ledger/check")
    assert resp.status_code == 200
    body = resp.json()
    assert body["settled_count"] == 1

    settled_resp = client.get("/ledger")
    blocks = settled_resp.json()
    assert len(blocks) == 2  # genesis + 1
    assert blocks[-1]["payload"]["markets_used"] == ["DAM"]


def test_check_ledger_with_nothing_due_returns_zero(client):
    resp = client.post("/ledger/check")
    assert resp.status_code == 200
    assert resp.json() == {"settled_count": 0}
