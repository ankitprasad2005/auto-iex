from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from ..chain.block import ChainBlock
from ..chain.ledger import Chain
from ..models.repository import get_price_blocks, load_price_ledger_blocks, save_price_ledger_block
from ..pricing.time_utils import to_market_time
from ..pricing.blocks import block_index_for_minute, generate_blocks, minutes_from_time


def _price_map(models) -> dict[int, Decimal]:
    return {block_index_for_minute(minutes_from_time(m.block_start)): m.mcp_rs_per_mwh for m in models}


def _to_domain_blocks(models) -> list[ChainBlock]:
    return [
        ChainBlock(index=m.index, timestamp=m.timestamp, payload=m.payload_json, prev_hash=m.prev_hash, hash=m.hash)
        for m in models
    ]


def check_and_record_price_blocks(session: Session, now: datetime) -> list[ChainBlock]:
    """Record today's 15-minute blocks into the price ledger as their
    delivery time arrives — independent of any user scenario.

    A block is "due" once wall-clock time (`now`) reaches its start-of-day
    minute today. Like settlement, this is a one-time immutable snapshot:
    once a block is recorded it is never revisited, even if the underlying
    price data changes afterwards.
    """
    market_now = to_market_time(now)
    today = market_now.date()
    now_minute = market_now.hour * 60 + market_now.minute

    existing_models = load_price_ledger_blocks(session)
    chain_was_empty = not existing_models
    chain = Chain(blocks=_to_domain_blocks(existing_models))

    already_recorded = {
        (b.payload.get("date"), b.payload.get("block_index"))
        for b in chain.blocks
        if "block_index" in b.payload
    }

    dam_map = _price_map(get_price_blocks(session, today, "DAM"))
    rtm_map = _price_map(get_price_blocks(session, today, "RTM"))

    newly_recorded: list[ChainBlock] = []

    for block in generate_blocks():
        if now_minute < block.start_minute:
            continue
        key = (today.isoformat(), block.index)
        if key in already_recorded:
            continue

        dam_price = dam_map.get(block.index)
        rtm_price = rtm_map.get(block.index)
        if dam_price is None and rtm_price is None:
            continue  # nothing published for this block yet; retry next tick

        payload = {
            "date": today.isoformat(),
            "block_index": block.index,
            "start_minute": block.start_minute,
            "end_minute": block.end_minute,
            "dam_price": float(dam_price) if dam_price is not None else None,
            "rtm_price": float(rtm_price) if rtm_price is not None else None,
            "recorded_at": now.isoformat(),
        }
        newly_recorded.append(chain.append(payload, now=now))

    if newly_recorded:
        if chain_was_empty:
            save_price_ledger_block(session, chain.blocks[0])
        for block in newly_recorded:
            save_price_ledger_block(session, block)

    return newly_recorded
