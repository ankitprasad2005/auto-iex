from datetime import date

from app.models.repository import upsert_price_blocks
from app.pricing.allocation import ConsumptionRange
from app.scraper.parser import PriceBlockRecord
from app.services.comparison_service import build_comparison
from datetime import time
from decimal import Decimal


def test_build_comparison_uses_stored_prices(db_session):
    records = [
        PriceBlockRecord(date=date(2026, 9, 10), market="DAM", block_start=time(0, 0), block_end=time(0, 15), mcp_rs_per_mwh=Decimal("4000")),
        PriceBlockRecord(date=date(2026, 9, 10), market="RTM", block_start=time(0, 0), block_end=time(0, 15), mcp_rs_per_mwh=Decimal("3000")),
    ]
    upsert_price_blocks(db_session, records)

    ranges = [ConsumptionRange(start_minute=0, end_minute=15, predicted_kw=4.0)]
    result = build_comparison(db_session, date(2026, 9, 10), ranges)

    assert result.blocks[0].dam_cost_rs == Decimal("4")
    assert result.blocks[0].rtm_cost_rs == Decimal("3")
    assert result.totals.dam_pending_blocks == 95  # only block 0 has a DAM price


def test_build_comparison_no_prices_all_pending(db_session):
    ranges = [ConsumptionRange(start_minute=0, end_minute=15, predicted_kw=4.0)]
    result = build_comparison(db_session, date(2026, 9, 10), ranges)
    assert result.totals.dam_pending_blocks == 96
    assert result.totals.rtm_pending_blocks == 96
