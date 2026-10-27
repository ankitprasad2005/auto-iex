from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from ..chain.block import ChainBlock
from ..chain.ledger import Chain
from ..models.repository import (
    get_latest_scenario,
    get_price_blocks,
    load_settlement_blocks,
    save_settlement_block,
)
from ..pricing.allocation import ConsumptionRange, allocate_to_blocks
from ..pricing.time_utils import to_market_time
from ..pricing.blocks import block_index_for_minute, generate_blocks, minutes_from_time


def _price_map(models) -> dict[int, Decimal]:
    return {block_index_for_minute(minutes_from_time(m.block_start)): m.mcp_rs_per_mwh for m in models}


def _to_domain_blocks(models) -> list[ChainBlock]:
    return [
        ChainBlock(index=m.index, timestamp=m.timestamp, payload=m.payload_json, prev_hash=m.prev_hash, hash=m.hash)
        for m in models
    ]


def check_and_settle_due_ranges(session: Session, now: datetime) -> list[ChainBlock]:
    """Settle any due-and-unsettled range on the most recently created scenario.

    A range is "due" once wall-clock time (`now`) reaches its start-of-day
    minute today. Settlement is a one-time, immutable snapshot: it prices
    the range using whichever of DAM/RTM is available at the moment of the
    check and never revisits it, even if better price data appears later.
    """
    scenario = get_latest_scenario(session)
    if scenario is None:
        return []

    market_now = to_market_time(now)
    today = market_now.date()
    now_minute = market_now.hour * 60 + market_now.minute

    existing_models = load_settlement_blocks(session)
    chain_was_empty = not existing_models
    chain = Chain(blocks=_to_domain_blocks(existing_models))

    already_settled = {
        (b.payload.get("scenario_id"), b.payload.get("range_id"), b.payload.get("date"))
        for b in chain.blocks
        if "range_id" in b.payload
    }

    dam_map = _price_map(get_price_blocks(session, today, "DAM"))
    rtm_map = _price_map(get_price_blocks(session, today, "RTM"))

    newly_settled: list[ChainBlock] = []

    for r in scenario.ranges:
        if now_minute < r.start_minute:
            continue
        key = (scenario.id, r.id, today.isoformat())
        if key in already_settled:
            continue

        consumption_range = ConsumptionRange(
            start_minute=r.start_minute, end_minute=r.end_minute, predicted_kw=float(r.predicted_kw)
        )
        kwh_by_block = allocate_to_blocks([consumption_range])

        total_kwh = Decimal(0)
        priced_kwh = Decimal(0)
        cost = Decimal(0)
        markets_used: set[str] = set()
        fully_priced = True

        for block in generate_blocks():
            kwh = kwh_by_block[block.index]
            if kwh == 0:
                continue
            kwh_decimal = Decimal(str(kwh))
            total_kwh += kwh_decimal

            price = dam_map.get(block.index)
            market = "DAM"
            if price is None:
                price = rtm_map.get(block.index)
                market = "RTM"
            if price is None:
                fully_priced = False
                continue

            priced_kwh += kwh_decimal
            cost += kwh_decimal * price / Decimal(1000)
            markets_used.add(market)

        if priced_kwh == 0:
            continue  # nothing priced yet anywhere in the range; retry next tick

        payload = {
            "scenario_id": scenario.id,
            "range_id": r.id,
            "date": today.isoformat(),
            "start_minute": r.start_minute,
            "end_minute": r.end_minute,
            "predicted_kw": float(r.predicted_kw),
            "total_kwh": float(total_kwh),
            "priced_kwh": float(priced_kwh),
            "cost_rs": float(cost),
            "markets_used": sorted(markets_used),
            "fully_priced": fully_priced,
            "settled_at": now.isoformat(),
        }
        newly_settled.append(chain.append(payload, now=now))

    if newly_settled:
        if chain_was_empty:
            save_settlement_block(session, chain.blocks[0])
        for block in newly_settled:
            save_settlement_block(session, block)

    return newly_settled
