from dataclasses import dataclass
from decimal import Decimal

from .allocation import ConsumptionRange, allocate_to_blocks
from .blocks import generate_blocks


@dataclass(frozen=True)
class BlockPrice:
    block_index: int
    dam_mcp_rs_per_mwh: Decimal | None
    rtm_mcp_rs_per_mwh: Decimal | None


@dataclass(frozen=True)
class BlockComparison:
    block_index: int
    predicted_kwh: float
    dam_cost_rs: Decimal | None
    rtm_cost_rs: Decimal | None
    dam_pending: bool
    rtm_pending: bool


@dataclass(frozen=True)
class ComparisonTotals:
    dam_total_rs: Decimal
    rtm_total_rs: Decimal
    hybrid_total_rs: Decimal
    dam_pending_blocks: int
    rtm_pending_blocks: int


@dataclass(frozen=True)
class ComparisonResult:
    blocks: list[BlockComparison]
    totals: ComparisonTotals


def _block_cost(predicted_kwh: float, mcp_rs_per_mwh: Decimal | None) -> Decimal | None:
    if mcp_rs_per_mwh is None:
        return None
    return Decimal(str(predicted_kwh)) * mcp_rs_per_mwh / Decimal(1000)


def compute_comparison(
    ranges: list[ConsumptionRange],
    prices: list[BlockPrice],
) -> ComparisonResult:
    blocks = generate_blocks()
    kwh_by_block = allocate_to_blocks(ranges, blocks)
    price_by_block = {p.block_index: p for p in prices}

    block_results: list[BlockComparison] = []
    dam_total = Decimal(0)
    rtm_total = Decimal(0)
    hybrid_total = Decimal(0)
    dam_pending = 0
    rtm_pending = 0

    for b in blocks:
        kwh = kwh_by_block[b.index]
        price = price_by_block.get(b.index)
        dam_mcp = price.dam_mcp_rs_per_mwh if price else None
        rtm_mcp = price.rtm_mcp_rs_per_mwh if price else None

        dam_cost = _block_cost(kwh, dam_mcp)
        rtm_cost = _block_cost(kwh, rtm_mcp)

        if dam_cost is None:
            dam_pending += 1
        else:
            dam_total += dam_cost

        if rtm_cost is None:
            rtm_pending += 1
        else:
            rtm_total += rtm_cost

        if dam_cost is not None and rtm_cost is not None:
            hybrid_total += min(dam_cost, rtm_cost)

        block_results.append(
            BlockComparison(
                block_index=b.index,
                predicted_kwh=kwh,
                dam_cost_rs=dam_cost,
                rtm_cost_rs=rtm_cost,
                dam_pending=dam_cost is None,
                rtm_pending=rtm_cost is None,
            )
        )

    return ComparisonResult(
        blocks=block_results,
        totals=ComparisonTotals(
            dam_total_rs=dam_total,
            rtm_total_rs=rtm_total,
            hybrid_total_rs=hybrid_total,
            dam_pending_blocks=dam_pending,
            rtm_pending_blocks=rtm_pending,
        ),
    )
