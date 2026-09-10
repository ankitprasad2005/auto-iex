from app.chain.block import ChainBlock, GENESIS_PREV_HASH
from app.models.repository import save_chain_block
from datetime import datetime, timezone


def test_read_chain_empty(client):
    resp = client.get("/chain")
    assert resp.status_code == 200
    assert resp.json() == []


def test_read_chain_returns_blocks(client, db_session):
    genesis = ChainBlock.create(index=0, timestamp=datetime.now(timezone.utc), payload={"genesis": True}, prev_hash=GENESIS_PREV_HASH)
    save_chain_block(db_session, genesis)
    resp = client.get("/chain")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["index"] == 0


def test_verify_chain_valid_when_empty(client):
    resp = client.get("/chain/verify")
    assert resp.status_code == 200
    assert resp.json() == {"valid": True, "invalid_block_index": None}


def test_verify_chain_detects_tampering(client, db_session):
    genesis = ChainBlock.create(index=0, timestamp=datetime.now(timezone.utc), payload={"genesis": True}, prev_hash=GENESIS_PREV_HASH)
    save_chain_block(db_session, genesis)
    tampered = ChainBlock.create(index=1, timestamp=datetime.now(timezone.utc), payload={"n": 1}, prev_hash="f" * 64)
    save_chain_block(db_session, tampered)

    resp = client.get("/chain/verify")
    body = resp.json()
    assert body["valid"] is False
    assert body["invalid_block_index"] == 1
