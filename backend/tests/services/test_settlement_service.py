from datetime import date, datetime, time, timezone
from decimal import Decimal

from app.models.repository import create_scenario, load_settlement_blocks, upsert_price_blocks
from app.pricing.time_utils import IST
from app.scraper.parser import PriceBlockRecord
from app.services.settlement_service import check_and_settle_due_ranges

TODAY = date(2026, 9, 15)


def _now(hour: int, minute: int) -> datetime:
    return datetime(TODAY.year, TODAY.month, TODAY.day, hour, minute, tzinfo=IST)


def _seed_price(session, market: str, block_start: time, block_end: time, mcp: str):
    upsert_price_blocks(
        session,
        [PriceBlockRecord(date=TODAY, market=market, block_start=block_start, block_end=block_end, mcp_rs_per_mwh=Decimal(mcp))],
    )


def test_no_scenarios_returns_empty(db_session):
    assert check_and_settle_due_ranges(db_session, _now(6, 0)) == []
    assert load_settlement_blocks(db_session) == []


def test_range_not_yet_due_is_not_settled(db_session):
    create_scenario(db_session, "scenario", [(360, 540, 5.0)])  # 06:00-09:00
    result = check_and_settle_due_ranges(db_session, _now(5, 0))  # 05:00, before start
    assert result == []
    assert load_settlement_blocks(db_session) == []


def test_due_range_settles_using_dam_price(db_session):
    create_scenario(db_session, "scenario", [(360, 375, 5.0)])  # 06:00-06:15, 15 min
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")

    result = check_and_settle_due_ranges(db_session, _now(6, 0))

    assert len(result) == 1
    payload = result[0].payload
    assert payload["markets_used"] == ["DAM"]
    assert payload["fully_priced"] is True
    # 5kW * 0.25h = 1.25 kWh; 1.25 * 4000 / 1000 = 5.0
    assert payload["cost_rs"] == 5.0
    assert len(load_settlement_blocks(db_session)) == 2  # genesis + 1


def test_due_range_falls_back_to_rtm_when_dam_missing(db_session):
    create_scenario(db_session, "scenario", [(360, 375, 5.0)])
    _seed_price(db_session, "RTM", time(6, 0), time(6, 15), "3000")

    result = check_and_settle_due_ranges(db_session, _now(6, 0))

    assert len(result) == 1
    payload = result[0].payload
    assert payload["markets_used"] == ["RTM"]
    assert payload["cost_rs"] == 3.75  # 1.25 kWh * 3000 / 1000


def test_due_range_with_no_price_anywhere_is_not_settled(db_session):
    create_scenario(db_session, "scenario", [(360, 375, 5.0)])
    result = check_and_settle_due_ranges(db_session, _now(6, 0))
    assert result == []
    assert load_settlement_blocks(db_session) == []


def test_already_settled_range_is_not_settled_again(db_session):
    create_scenario(db_session, "scenario", [(360, 375, 5.0)])
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")

    first = check_and_settle_due_ranges(db_session, _now(6, 0))
    second = check_and_settle_due_ranges(db_session, _now(6, 5))

    assert len(first) == 1
    assert second == []
    assert len(load_settlement_blocks(db_session)) == 2  # genesis + 1, not 3


def test_only_the_most_recent_scenario_is_watched(db_session):
    create_scenario(db_session, "old", [(360, 375, 5.0)])
    create_scenario(db_session, "new", [(420, 435, 2.0)])  # 07:00-07:15
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")
    _seed_price(db_session, "DAM", time(7, 0), time(7, 15), "3500")

    result = check_and_settle_due_ranges(db_session, _now(7, 0))

    # only "new" scenario's 07:00 range should settle; "old" scenario's
    # 06:00 range is due too but belongs to a superseded scenario
    assert len(result) == 1
    assert result[0].payload["start_minute"] == 420


def test_multiple_due_ranges_in_one_call_all_settle(db_session):
    create_scenario(db_session, "scenario", [(360, 375, 5.0), (420, 435, 2.0)])
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")
    _seed_price(db_session, "DAM", time(7, 0), time(7, 15), "3500")

    result = check_and_settle_due_ranges(db_session, _now(8, 0))

    assert len(result) == 2
    assert len(load_settlement_blocks(db_session)) == 3  # genesis + 2


def test_range_spanning_multiple_blocks_partially_priced_marks_not_fully_priced(db_session):
    create_scenario(db_session, "scenario", [(360, 390, 4.0)])  # 06:00-06:30, 2 blocks
    _seed_price(db_session, "DAM", time(6, 0), time(6, 15), "4000")
    # second block (06:15-06:30) has no price at all

    result = check_and_settle_due_ranges(db_session, _now(6, 30))

    assert len(result) == 1
    payload = result[0].payload
    assert payload["fully_priced"] is False
    assert payload["total_kwh"] == 2.0  # 4kW * 0.5h, fully known regardless of pricing
    assert payload["priced_kwh"] == 1.0  # only the priced first block
    assert payload["cost_rs"] == 4.0  # 1.0 kWh * 4000 / 1000


def test_utc_instant_is_read_as_ist_market_time(db_session):
    create_scenario(db_session, "scenario", [(1080, 1095, 5.0)])  # 18:00-18:15 IST
    _seed_price(db_session, "DAM", time(18, 0), time(18, 15), "4000")

    # 12:29 UTC is 17:59 IST: not due yet; 12:30 UTC is 18:00 IST: due
    assert check_and_settle_due_ranges(db_session, datetime(2026, 9, 15, 12, 29, tzinfo=timezone.utc)) == []
    result = check_and_settle_due_ranges(db_session, datetime(2026, 9, 15, 12, 30, tzinfo=timezone.utc))

    assert len(result) == 1
    assert result[0].payload["date"] == "2026-09-15"


def test_utc_instant_late_in_the_day_settles_for_the_next_ist_date(db_session):
    create_scenario(db_session, "scenario", [(0, 15, 5.0)])  # 00:00-00:15 IST
    _seed_price(db_session, "DAM", time(0, 0), time(0, 15), "4000")

    # 2026-09-14 19:00 UTC is 2026-09-15 00:30 IST
    result = check_and_settle_due_ranges(db_session, datetime(2026, 9, 14, 19, 0, tzinfo=timezone.utc))

    assert len(result) == 1
    assert result[0].payload["date"] == TODAY.isoformat()
    assert result[0].payload["cost_rs"] == 5.0
