from datetime import date, datetime, time, timezone
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.chain.block import ChainBlock, GENESIS_PREV_HASH
from app.models.repository import (
    create_scenario,
    get_price_blocks,
    get_scenario,
    load_chain_blocks,
    save_chain_block,
    upsert_price_blocks,
)
from app.scraper.parser import PriceBlockRecord


def _price_record(mcp="3245.50", market="DAM"):
    return PriceBlockRecord(
        date=date(2026, 9, 10), market=market, block_start=time(0, 0), block_end=time(0, 15),
        mcp_rs_per_mwh=Decimal(mcp),
    )


def test_upsert_price_blocks_inserts_new_rows(db_session):
    written = upsert_price_blocks(db_session, [_price_record()])
    assert written == 1
    blocks = get_price_blocks(db_session, date(2026, 9, 10), "DAM")
    assert len(blocks) == 1
    assert blocks[0].mcp_rs_per_mwh == Decimal("3245.50")


def test_upsert_price_blocks_is_idempotent_no_duplicates(db_session):
    upsert_price_blocks(db_session, [_price_record()])
    written_second = upsert_price_blocks(db_session, [_price_record(mcp="3300.00")])
    assert written_second == 0  # updated, not inserted
    blocks = get_price_blocks(db_session, date(2026, 9, 10), "DAM")
    assert len(blocks) == 1
    assert blocks[0].mcp_rs_per_mwh == Decimal("3300.00")


def test_create_and_get_scenario(db_session):
    scenario = create_scenario(db_session, "evening load", [(1080, 1200, 4.0)])
    fetched = get_scenario(db_session, scenario.id)
    assert fetched is not None
    assert fetched.name == "evening load"
    assert len(fetched.ranges) == 1
    assert fetched.ranges[0].start_minute == 1080


def test_get_scenario_unknown_id_returns_none(db_session):
    assert get_scenario(db_session, 9999) is None


def test_save_and_load_chain_block(db_session):
    genesis = ChainBlock.create(index=0, timestamp=datetime.now(timezone.utc), payload={"genesis": True}, prev_hash=GENESIS_PREV_HASH)
    save_chain_block(db_session, genesis)
    blocks = load_chain_blocks(db_session)
    assert len(blocks) == 1
    assert blocks[0].index == 0
    assert blocks[0].payload_json == {"genesis": True}


def test_save_chain_block_duplicate_index_rejected(db_session):
    genesis = ChainBlock.create(index=0, timestamp=datetime.now(timezone.utc), payload={"a": 1}, prev_hash=GENESIS_PREV_HASH)
    save_chain_block(db_session, genesis)
    duplicate = ChainBlock.create(index=0, timestamp=datetime.now(timezone.utc), payload={"a": 2}, prev_hash=GENESIS_PREV_HASH)
    with pytest.raises(IntegrityError):
        save_chain_block(db_session, duplicate)
