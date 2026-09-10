from datetime import datetime, timezone

from app.chain.block import ChainBlock, compute_hash, GENESIS_PREV_HASH


def test_compute_hash_deterministic():
    ts = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
    h1 = compute_hash(0, ts, {"a": 1}, GENESIS_PREV_HASH)
    h2 = compute_hash(0, ts, {"a": 1}, GENESIS_PREV_HASH)
    assert h1 == h2
    assert len(h1) == 64


def test_compute_hash_changes_with_payload():
    ts = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
    h1 = compute_hash(0, ts, {"a": 1}, GENESIS_PREV_HASH)
    h2 = compute_hash(0, ts, {"a": 2}, GENESIS_PREV_HASH)
    assert h1 != h2


def test_compute_hash_changes_with_prev_hash():
    ts = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
    h1 = compute_hash(1, ts, {"a": 1}, "a" * 64)
    h2 = compute_hash(1, ts, {"a": 1}, "b" * 64)
    assert h1 != h2


def test_chain_block_create_matches_recomputed_hash():
    ts = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
    block = ChainBlock.create(index=0, timestamp=ts, payload={"genesis": True}, prev_hash=GENESIS_PREV_HASH)
    assert block.hash == compute_hash(0, ts, {"genesis": True}, GENESIS_PREV_HASH)
    assert block.prev_hash == GENESIS_PREV_HASH
    assert block.index == 0
