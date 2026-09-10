import hashlib
import json
from datetime import date as date_type

from sqlalchemy.orm import Session

from ..chain.block import ChainBlock
from ..chain.ledger import Chain
from ..models.repository import load_chain_blocks, save_chain_block, upsert_price_blocks
from ..scraper.browser import fetch_snapshot_rows
from ..scraper.parser import Market, PriceBlockRecord, parse_rows


def _price_hash(records: list[PriceBlockRecord]) -> str:
    canonical = sorted(
        [{"block_start": r.block_start.isoformat(), "mcp": str(r.mcp_rs_per_mwh)} for r in records],
        key=lambda d: d["block_start"],
    )
    return hashlib.sha256(json.dumps(canonical, sort_keys=True).encode("utf-8")).hexdigest()


def _to_domain_blocks(models) -> list[ChainBlock]:
    return [
        ChainBlock(index=m.index, timestamp=m.timestamp, payload=m.payload_json, prev_hash=m.prev_hash, hash=m.hash)
        for m in models
    ]


def scrape_and_record(
    session: Session,
    market: Market,
    delivery_date: date_type,
    fetch_fn=None,
) -> dict:
    rows = fetch_snapshot_rows(market, fetch_fn=fetch_fn)
    records = parse_rows(rows, market, delivery_date)
    price_hash = _price_hash(records)

    existing_models = load_chain_blocks(session)
    chain_was_empty = not existing_models
    chain = Chain(blocks=_to_domain_blocks(existing_models))

    is_duplicate = any(
        b.payload.get("price_hash") == price_hash
        and b.payload.get("market") == market
        and b.payload.get("date") == delivery_date.isoformat()
        for b in chain.blocks
    )

    written = upsert_price_blocks(session, records)

    if is_duplicate:
        return {"chain_block": None, "written": written, "skipped_duplicate": True}

    new_block = chain.append(
        {"market": market, "date": delivery_date.isoformat(), "block_count": len(records), "price_hash": price_hash}
    )
    if chain_was_empty:
        # append() auto-created the genesis block in-memory; persist it too.
        save_chain_block(session, chain.blocks[0])
    save_chain_block(session, new_block)
    return {"chain_block": new_block, "written": written, "skipped_duplicate": False}
