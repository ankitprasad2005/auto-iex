from datetime import datetime, timezone

from app.models.repository import get_anchor, get_latest_confirmed_anchor, list_anchors, save_anchor
from app.models.tables import AnchorModel

Z = "0" * 64


def _anchor(status="confirmed", tx_hash="0x01", scrape_hash="a" * 64):
    return AnchorModel(
        created_at=datetime(2026, 10, 27, 10, 0, tzinfo=timezone.utc),
        scrape_head_index=3, scrape_head_hash=scrape_hash,
        settlement_head_index=-1, settlement_head_hash=Z,
        price_ledger_head_index=0, price_ledger_head_hash="c" * 64,
        tx_hash=tx_hash, status=status, block_number=10 if tx_hash else None,
        error=None if tx_hash else "boom",
    )


def test_save_and_get_anchor_roundtrip(db_session):
    saved = save_anchor(db_session, _anchor())
    assert saved.id is not None
    loaded = get_anchor(db_session, saved.id)
    assert loaded.scrape_head_index == 3
    assert loaded.settlement_head_index == -1
    assert loaded.settlement_head_hash == Z
    assert loaded.tx_hash == "0x01"
    assert loaded.block_number == 10


def test_failed_anchor_stores_nulls_and_long_error(db_session):
    anchor = _anchor(status="failed", tx_hash=None)
    anchor.error = "x" * 10_000
    saved = save_anchor(db_session, anchor)
    loaded = get_anchor(db_session, saved.id)
    assert loaded.tx_hash is None and loaded.block_number is None
    assert loaded.error == "x" * 10_000


def test_get_anchor_unknown_id_returns_none(db_session):
    assert get_anchor(db_session, 999) is None


def test_list_anchors_newest_first(db_session):
    ids = [save_anchor(db_session, _anchor()).id for _ in range(3)]
    assert [a.id for a in list_anchors(db_session)] == list(reversed(ids))


def test_list_anchors_empty(db_session):
    assert list_anchors(db_session) == []


def test_latest_confirmed_ignores_failed(db_session):
    assert get_latest_confirmed_anchor(db_session) is None
    save_anchor(db_session, _anchor(status="failed", tx_hash=None))
    assert get_latest_confirmed_anchor(db_session) is None
    first = save_anchor(db_session, _anchor(scrape_hash="1" * 64))
    second = save_anchor(db_session, _anchor(scrape_hash="2" * 64, tx_hash="0x02"))
    save_anchor(db_session, _anchor(status="failed", tx_hash=None))
    assert get_latest_confirmed_anchor(db_session).id == second.id != first.id
