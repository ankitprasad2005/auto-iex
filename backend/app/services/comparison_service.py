from datetime import date as date_type
from decimal import Decimal

from sqlalchemy.orm import Session

from ..models.repository import get_price_blocks
from ..pricing.allocation import ConsumptionRange
from ..pricing.blocks import block_index_for_minute, generate_blocks, minutes_from_time
from ..pricing.comparison import BlockPrice, ComparisonResult, compute_comparison


def _price_map(models) -> dict[int, Decimal]:
    return {block_index_for_minute(minutes_from_time(m.block_start)): m.mcp_rs_per_mwh for m in models}


def build_comparison(session: Session, delivery_date: date_type, ranges: list[ConsumptionRange]) -> ComparisonResult:
    dam_map = _price_map(get_price_blocks(session, delivery_date, "DAM"))
    rtm_map = _price_map(get_price_blocks(session, delivery_date, "RTM"))

    prices = [
        BlockPrice(
            block_index=b.index,
            dam_mcp_rs_per_mwh=dam_map.get(b.index),
            rtm_mcp_rs_per_mwh=rtm_map.get(b.index),
        )
        for b in generate_blocks()
    ]
    return compute_comparison(ranges, prices)
