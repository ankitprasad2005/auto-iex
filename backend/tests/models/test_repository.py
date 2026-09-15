from datetime import date, datetime, time, timezone
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.chain.block import ChainBlock, GENESIS_PREV_HASH
from app.models.repository import (
    create_scenario,
    get_latest_scenario,
    get_price_blocks,
    get_scenario,
    load_chain_blocks,
    load_settlement_blocks,
    save_chain_block,
    save_settlement_block,
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


def test_save_and_load_settlement_block(db_session):
    genesis = ChainBlock.create(index=0, timestamp=datetime.now(timezone.utc), payload={"genesis": True}, prev_hash=GENESIS_PREV_HASH)
    save_settlement_block(db_session, genesis)
    blocks = load_settlement_blocks(db_session)
    assert len(blocks) == 1
    assert blocks[0].index == 0
    assert blocks[0].payload_json == {"genesis": True}


def test_settlement_blocks_are_independent_from_chain_blocks(db_session):
    genesis = ChainBlock.create(index=0, timestamp=datetime.now(timezone.utc), payload={"genesis": True}, prev_hash=GENESIS_PREV_HASH)
    save_chain_block(db_session, genesis)
    save_settlement_block(db_session, genesis)
    assert len(load_chain_blocks(db_session)) == 1
    assert len(load_settlement_blocks(db_session)) == 1


def test_get_latest_scenario_returns_most_recently_created(db_session):
    create_scenario(db_session, "first", [(0, 15, 1.0)])
    second = create_scenario(db_session, "second", [(15, 30, 2.0)])
    latest = get_latest_scenario(db_session)
    assert latest is not None
    assert latest.id == second.id


def test_get_latest_scenario_returns_none_when_no_scenarios_exist(db_session):
    assert get_latest_scenario(db_session) is None
