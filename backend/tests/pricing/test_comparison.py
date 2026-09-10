from decimal import Decimal

from app.pricing.allocation import ConsumptionRange
from app.pricing.blocks import generate_blocks, BLOCKS_PER_DAY
from app.pricing.comparison import BlockPrice, compute_comparison


def _all_pending_prices():
    return [
        BlockPrice(block_index=b.index, dam_mcp_rs_per_mwh=None, rtm_mcp_rs_per_mwh=None)
        for b in generate_blocks()
    ]


def _all_available_prices(dam=Decimal("4000"), rtm=Decimal("3000")):
    return [
        BlockPrice(block_index=b.index, dam_mcp_rs_per_mwh=dam, rtm_mcp_rs_per_mwh=rtm)
        for b in generate_blocks()
    ]


def test_compute_comparison_empty_ranges_zero_cost_not_pending():
    result = compute_comparison([], _all_available_prices())
    assert result.totals.dam_total_rs == Decimal("0")
    assert result.totals.rtm_total_rs == Decimal("0")
    assert result.totals.dam_pending_blocks == 0
    assert result.totals.rtm_pending_blocks == 0


def test_compute_comparison_all_blocks_pending():
    ranges = [ConsumptionRange(start_minute=0, end_minute=15, predicted_kw=4.0)]
    result = compute_comparison(ranges, _all_pending_prices())
    assert result.totals.dam_pending_blocks == BLOCKS_PER_DAY
    assert result.totals.rtm_pending_blocks == BLOCKS_PER_DAY
    assert result.totals.dam_total_rs == Decimal("0")
    assert result.totals.hybrid_total_rs == Decimal("0")


def test_compute_comparison_mixed_pending_and_available():
    ranges = [ConsumptionRange(start_minute=0, end_minute=1440, predicted_kw=4.0)]
    prices = [
        BlockPrice(block_index=b.index, dam_mcp_rs_per_mwh=Decimal("4000"), rtm_mcp_rs_per_mwh=None)
        for b in generate_blocks()
    ]
    result = compute_comparison(ranges, prices)
    assert result.totals.dam_pending_blocks == 0
    assert result.totals.rtm_pending_blocks == BLOCKS_PER_DAY
    assert result.totals.dam_total_rs > Decimal("0")
    assert result.totals.rtm_total_rs == Decimal("0")
    # hybrid excludes blocks where either side is pending
    assert result.totals.hybrid_total_rs == Decimal("0")


def test_compute_comparison_hybrid_picks_cheaper_per_block():
    ranges = [ConsumptionRange(start_minute=0, end_minute=15, predicted_kw=4.0)]
    prices = _all_available_prices(dam=Decimal("4000"), rtm=Decimal("3000"))
    result = compute_comparison(ranges, prices)
    block0 = result.blocks[0]
    expected_kwh = Decimal("1.0")  # 4kW * 0.25h
    assert block0.dam_cost_rs == expected_kwh * Decimal("4000") / Decimal("1000")
    assert block0.rtm_cost_rs == expected_kwh * Decimal("3000") / Decimal("1000")
    assert result.totals.hybrid_total_rs == result.totals.rtm_total_rs  # RTM cheaper every block
    assert result.totals.hybrid_total_rs < result.totals.dam_total_rs
