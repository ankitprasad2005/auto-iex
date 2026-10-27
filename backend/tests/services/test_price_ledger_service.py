from datetime import date, datetime, time, timezone
from decimal import Decimal

from app.models.repository import load_price_ledger_blocks, upsert_price_blocks
from app.pricing.time_utils import IST
from app.scraper.parser import PriceBlockRecord
from app.services.price_ledger_service import check_and_record_price_blocks

TODAY = date(2026, 9, 15)


def _now(hour: int, minute: int) -> datetime:
    return datetime(TODAY.year, TODAY.month, TODAY.day, hour, minute, tzinfo=IST)


def _seed_price(session, market: str, block_start: time, block_end: time, mcp: str):
    upsert_price_blocks(
        session,
        [PriceBlockRecord(date=TODAY, market=market, block_start=block_start, block_end=block_end, mcp_rs_per_mwh=Decimal(mcp))],
    )


def test_no_prices_yet_records_nothing(db_session):
    result = check_and_record_price_blocks(db_session, _now(0, 0))
    assert result == []
    assert load_price_ledger_blocks(db_session) == []


def test_records_block_once_its_delivery_time_arrives(db_session):
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")

    # block hasn't started yet at 05:00
    before = check_and_record_price_blocks(db_session, _now(5, 0))
    assert before == []

    # block starts at 06:00
    at_start = check_and_record_price_blocks(db_session, _now(6, 0))
    assert len(at_start) == 1
    payload = at_start[0].payload
    assert payload["block_index"] == 24  # 06:00 = minute 360 = block 24
    assert payload["dam_price"] == 4000.0
    assert payload["rtm_price"] is None
    assert len(load_price_ledger_blocks(db_session)) == 2  # genesis + 1


def test_records_rtm_price_alongside_dam_when_both_available(db_session):
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")
    _seed_price(db_session, "RTM", time(6, 0), time(6, 15), "3800")

    result = check_and_record_price_blocks(db_session, _now(6, 0))

    assert len(result) == 1
    assert result[0].payload["dam_price"] == 4000.0
    assert result[0].payload["rtm_price"] == 3800.0


def test_block_with_no_price_at_all_is_not_recorded(db_session):
    result = check_and_record_price_blocks(db_session, _now(6, 0))
    assert result == []


def test_already_recorded_block_is_not_recorded_again(db_session):
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")
    first = check_and_record_price_blocks(db_session, _now(6, 0))
    second = check_and_record_price_blocks(db_session, _now(6, 5))
    assert len(first) == 1
    assert second == []
    assert len(load_price_ledger_blocks(db_session)) == 2


def test_multiple_due_blocks_all_recorded_in_one_call(db_session):
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")
    _seed_price(db_session, "DAM", time(6, 15), time(6, 30), "4100")

    result = check_and_record_price_blocks(db_session, _now(6, 20))

    assert len(result) == 2
    assert len(load_price_ledger_blocks(db_session)) == 3  # genesis + 2


def test_recorded_price_is_never_revised_after_the_fact(db_session):
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")
    first = check_and_record_price_blocks(db_session, _now(6, 0))
    assert first[0].payload["dam_price"] == 4000.0

    # price data changes after the block was already recorded
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "9999")
    second = check_and_record_price_blocks(db_session, _now(6, 30))
    assert second == []  # not re-recorded, even though the price "changed"


def test_utc_instant_is_read_as_ist_market_time(db_session):
    _seed_price(db_session, "DAM", time(18, 0), time(18, 15), "4000")

    # 12:29 UTC is 17:59 IST: not due; 12:30 UTC is 18:00 IST: due
    assert check_and_record_price_blocks(db_session, datetime(2026, 9, 15, 12, 29, tzinfo=timezone.utc)) == []
    result = check_and_record_price_blocks(db_session, datetime(2026, 9, 15, 12, 30, tzinfo=timezone.utc))

    assert [b.payload["block_index"] for b in result] == [72]


def test_utc_instant_late_in_the_day_records_the_next_ist_date(db_session):
    _seed_price(db_session, "DAM", time(0, 0), time(0, 15), "4000")

    # 2026-09-14 19:00 UTC is 2026-09-15 00:30 IST
    result = check_and_record_price_blocks(db_session, datetime(2026, 9, 14, 19, 0, tzinfo=timezone.utc))

    assert [b.payload["block_index"] for b in result] == [0]
