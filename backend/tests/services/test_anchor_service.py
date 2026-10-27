from datetime import datetime, timezone

from sqlalchemy import delete

from app.anchoring.payload import decode_anchor_payload, encode_anchor_payload
from app.models.repository import get_anchor, list_anchors, save_anchor
from app.models.tables import AnchorModel, ChainBlockModel, PriceLedgerBlockModel, SettlementBlockModel
from app.services.anchor_service import (
    AnchorNotFoundError,
    AnchorNotPublishedError,
    anchor_chain_heads,
    verify_anchor,
)
from tests.anchoring.fake_publisher import FakePublisher

import pytest

NOW = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
Z = "0" * 64


def _add(session, model_cls, index, hash_):
    session.add(model_cls(index=index, timestamp=NOW, payload_json={}, prev_hash=Z, hash=hash_))
    session.commit()


def _seed(session):
    _add(session, ChainBlockModel, 0, "a0" * 32)
    _add(session, ChainBlockModel, 1, "a1" * 32)
    _add(session, SettlementBlockModel, 0, "b0" * 32)
    _add(session, PriceLedgerBlockModel, 0, "c0" * 32)
    _add(session, PriceLedgerBlockModel, 1, "c1" * 32)
    _add(session, PriceLedgerBlockModel, 2, "c2" * 32)


def test_anchors_current_heads(db_session):
    _seed(db_session)
    pub = FakePublisher()
    anchor, reason = anchor_chain_heads(db_session, pub, NOW)

    assert reason is None
    assert anchor.status == "confirmed"
    assert (anchor.scrape_head_index, anchor.scrape_head_hash) == (1, "a1" * 32)
    assert (anchor.settlement_head_index, anchor.settlement_head_hash) == (0, "b0" * 32)
    assert (anchor.price_ledger_head_index, anchor.price_ledger_head_hash) == (2, "c2" * 32)
    assert anchor.tx_hash == "0x" + "0" * 63 + "1"
    assert anchor.block_number == 1001
    assert anchor.error is None
    assert anchor.created_at.replace(tzinfo=timezone.utc) == NOW
    assert pub.sent == [encode_anchor_payload("a1" * 32, "b0" * 32, "c2" * 32)]
    assert get_anchor(db_session, anchor.id) is not None


def test_anchors_empty_chains_as_minus_one_zero_hash(db_session):
    pub = FakePublisher()
    anchor, reason = anchor_chain_heads(db_session, pub, NOW)
    assert reason is None
    assert anchor.scrape_head_index == anchor.settlement_head_index == anchor.price_ledger_head_index == -1
    assert anchor.scrape_head_hash == anchor.settlement_head_hash == anchor.price_ledger_head_hash == Z
    assert decode_anchor_payload(pub.sent[0]) == (Z, Z, Z)


def test_skips_when_heads_unchanged_since_last_confirmed(db_session):
    _seed(db_session)
    pub = FakePublisher()
    anchor_chain_heads(db_session, pub, NOW)
    anchor, reason = anchor_chain_heads(db_session, pub, NOW)
    assert (anchor, reason) == (None, "unchanged")
    assert len(pub.sent) == 1
    assert len(list_anchors(db_session)) == 1


def test_skips_unchanged_even_when_all_chains_empty(db_session):
    pub = FakePublisher()
    anchor_chain_heads(db_session, pub, NOW)
    assert anchor_chain_heads(db_session, pub, NOW) == (None, "unchanged")


@pytest.mark.parametrize("model_cls", [ChainBlockModel, SettlementBlockModel, PriceLedgerBlockModel])
def test_reanchors_when_any_single_chain_advances(db_session, model_cls):
    _seed(db_session)
    pub = FakePublisher()
    anchor_chain_heads(db_session, pub, NOW)
    _add(db_session, model_cls, 5, "ee" * 32)
    anchor, reason = anchor_chain_heads(db_session, pub, NOW)
    assert reason is None and anchor is not None
    assert len(pub.sent) == 2


def test_does_not_skip_based_on_a_failed_anchor(db_session):
    _seed(db_session)
    failing = FakePublisher(error=RuntimeError("rpc down"))
    anchor_chain_heads(db_session, failing, NOW)
    pub = FakePublisher()
    anchor, reason = anchor_chain_heads(db_session, pub, NOW)
    assert reason is None and anchor.status == "confirmed"


def test_publish_exception_saves_failed_record_and_never_raises(db_session):
    _seed(db_session)
    anchor, reason = anchor_chain_heads(db_session, FakePublisher(error=ValueError("insufficient funds")), NOW)
    assert reason == "failed"
    assert anchor.status == "failed"
    assert anchor.tx_hash is None and anchor.block_number is None
    assert "insufficient funds" in anchor.error
    assert anchor.scrape_head_hash == "a1" * 32
    assert list_anchors(db_session)[0].id == anchor.id


def test_publish_exception_with_empty_message_still_has_error(db_session):
    anchor, reason = anchor_chain_heads(db_session, FakePublisher(error=TimeoutError()), NOW)
    assert reason == "failed"
    assert anchor.error == "TimeoutError"


# --- verify ---------------------------------------------------------------


def _anchored(session):
    _seed(session)
    pub = FakePublisher()
    anchor, _ = anchor_chain_heads(session, pub, NOW)
    return pub, anchor


def test_verify_all_valid(db_session):
    pub, anchor = _anchored(db_session)
    assert verify_anchor(db_session, pub, anchor.id) == {
        "valid": True, "on_chain_matches_record": True, "ledger_matches_record": True, "mismatches": [],
    }


def test_verify_still_valid_after_chains_grow(db_session):
    pub, anchor = _anchored(db_session)
    _add(db_session, ChainBlockModel, 2, "a2" * 32)
    _add(db_session, SettlementBlockModel, 1, "b1" * 32)
    assert verify_anchor(db_session, pub, anchor.id)["valid"] is True


def test_verify_empty_chain_anchor_stays_valid_after_chain_grows(db_session):
    pub = FakePublisher()
    anchor, _ = anchor_chain_heads(db_session, pub, NOW)
    _seed(db_session)
    assert verify_anchor(db_session, pub, anchor.id)["valid"] is True


def test_verify_detects_on_chain_mismatch(db_session):
    pub, anchor = _anchored(db_session)
    pub.on_chain[anchor.tx_hash] = encode_anchor_payload("a1" * 32, "ff" * 32, "c2" * 32)
    result = verify_anchor(db_session, pub, anchor.id)
    assert result["valid"] is False
    assert result["on_chain_matches_record"] is False
    assert result["ledger_matches_record"] is True
    assert result["mismatches"] == ["on-chain settlement ledger head hash differs from the stored anchor record"]


def test_verify_detects_tampered_stored_record(db_session):
    pub, anchor = _anchored(db_session)
    anchor.price_ledger_head_hash = "dd" * 32
    db_session.commit()
    result = verify_anchor(db_session, pub, anchor.id)
    assert result["on_chain_matches_record"] is False
    assert result["ledger_matches_record"] is False
    assert "on-chain price ledger head hash differs from the stored anchor record" in result["mismatches"]
    assert "price ledger block 2 hash changed since anchoring" in result["mismatches"]


def test_verify_detects_undecodable_on_chain_data(db_session):
    pub, anchor = _anchored(db_session)
    pub.on_chain[anchor.tx_hash] = b"garbage"
    result = verify_anchor(db_session, pub, anchor.id)
    assert result["valid"] is False
    assert result["on_chain_matches_record"] is False
    assert result["ledger_matches_record"] is True
    assert len(result["mismatches"]) == 1
    assert result["mismatches"][0].startswith("on-chain data is not a valid anchor payload")


def test_verify_reports_fetch_failure_as_on_chain_mismatch(db_session):
    pub, anchor = _anchored(db_session)
    del pub.on_chain[anchor.tx_hash]
    result = verify_anchor(db_session, pub, anchor.id)
    assert result["valid"] is False
    assert result["on_chain_matches_record"] is False
    assert result["mismatches"][0].startswith("could not fetch on-chain transaction")


def test_verify_detects_tampered_db_block(db_session):
    pub, anchor = _anchored(db_session)
    block = db_session.get(PriceLedgerBlockModel, 2)
    block.hash = "99" * 32
    db_session.commit()
    result = verify_anchor(db_session, pub, anchor.id)
    assert result == {
        "valid": False, "on_chain_matches_record": True, "ledger_matches_record": False,
        "mismatches": ["price ledger block 2 hash changed since anchoring"],
    }


def test_verify_detects_missing_block(db_session):
    pub, anchor = _anchored(db_session)
    db_session.execute(delete(ChainBlockModel).where(ChainBlockModel.index == 1))
    db_session.commit()
    result = verify_anchor(db_session, pub, anchor.id)
    assert result["ledger_matches_record"] is False
    assert result["mismatches"] == ["scrape chain block 1 is missing"]


def test_verify_detects_multiple_ledger_problems(db_session):
    pub, anchor = _anchored(db_session)
    db_session.get(ChainBlockModel, 1).hash = "98" * 32
    db_session.execute(delete(SettlementBlockModel))
    db_session.commit()
    result = verify_anchor(db_session, pub, anchor.id)
    assert result["mismatches"] == [
        "scrape chain block 1 hash changed since anchoring",
        "settlement ledger block 0 is missing",
    ]


def test_verify_empty_head_with_nonzero_hash_is_mismatch(db_session):
    pub = FakePublisher()
    anchor = save_anchor(db_session, AnchorModel(
        created_at=NOW, scrape_head_index=-1, scrape_head_hash="ab" * 32,
        settlement_head_index=-1, settlement_head_hash=Z, price_ledger_head_index=-1, price_ledger_head_hash=Z,
        tx_hash="0xfeed", status="confirmed", block_number=1, error=None,
    ))
    pub.on_chain["0xfeed"] = encode_anchor_payload("ab" * 32, Z, Z)
    result = verify_anchor(db_session, pub, anchor.id)
    assert result["on_chain_matches_record"] is True
    assert result["ledger_matches_record"] is False
    assert result["mismatches"] == ["scrape chain head recorded as empty but has a non-zero hash"]


def test_verify_unknown_id_raises_not_found(db_session):
    with pytest.raises(AnchorNotFoundError):
        verify_anchor(db_session, FakePublisher(), 12345)


def test_verify_failed_anchor_raises_not_published(db_session):
    anchor, _ = anchor_chain_heads(db_session, FakePublisher(error=RuntimeError("x")), NOW)
    with pytest.raises(AnchorNotPublishedError):
        verify_anchor(db_session, FakePublisher(), anchor.id)
