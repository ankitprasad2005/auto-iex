from datetime import datetime
from typing import Any, Callable, NamedTuple

from sqlalchemy.orm import Session

from ..anchoring.payload import EMPTY_HEAD_HASH, EMPTY_HEAD_INDEX, chain_head, decode_anchor_payload, encode_anchor_payload
from ..anchoring.publisher import AnchorPublisher
from ..models.repository import (
    get_anchor,
    get_latest_confirmed_anchor,
    load_chain_blocks,
    load_price_ledger_blocks,
    load_settlement_blocks,
    save_anchor,
)
from ..models.tables import AnchorModel, ChainBlockModel, PriceLedgerBlockModel, SettlementBlockModel


class _Chain(NamedTuple):
    name: str
    prefix: str
    load: Callable[[Session], list[Any]]
    model: type


# Payload order: scrape, settlement, price ledger.
_CHAINS = [
    _Chain("scrape chain", "scrape", load_chain_blocks, ChainBlockModel),
    _Chain("settlement ledger", "settlement", load_settlement_blocks, SettlementBlockModel),
    _Chain("price ledger", "price_ledger", load_price_ledger_blocks, PriceLedgerBlockModel),
]


class AnchorNotFoundError(LookupError):
    pass


class AnchorNotPublishedError(ValueError):
    pass


def _heads(anchor: AnchorModel) -> list[tuple[int, str]]:
    return [(getattr(anchor, f"{p}_head_index"), getattr(anchor, f"{p}_head_hash")) for p in (c.prefix for c in _CHAINS)]


def anchor_chain_heads(
    session: Session, publisher: AnchorPublisher, now: datetime
) -> tuple[AnchorModel | None, str | None]:
    heads = [chain_head(c.load(session)) for c in _CHAINS]
    latest = get_latest_confirmed_anchor(session)
    if latest is not None and _heads(latest) == heads:
        return None, "unchanged"

    anchor = AnchorModel(created_at=now, status="confirmed")
    for chain, (index, hash_) in zip(_CHAINS, heads):
        setattr(anchor, f"{chain.prefix}_head_index", index)
        setattr(anchor, f"{chain.prefix}_head_hash", hash_)
    try:
        anchor.tx_hash, anchor.block_number = publisher.publish(encode_anchor_payload(*(h for _, h in heads)))
        reason = None
    except Exception as exc:  # noqa: BLE001 - any RPC/signing failure is recorded, never raised
        anchor.status = "failed"
        anchor.error = str(exc) or type(exc).__name__
        reason = "failed"
    return save_anchor(session, anchor), reason


def _check_on_chain(publisher: AnchorPublisher, anchor: AnchorModel) -> list[str]:
    try:
        data = publisher.fetch_tx_data(anchor.tx_hash)
    except Exception as exc:  # noqa: BLE001
        return [f"could not fetch on-chain transaction: {exc}"]
    try:
        on_chain = decode_anchor_payload(data)
    except ValueError as exc:
        return [f"on-chain data is not a valid anchor payload: {exc}"]
    return [
        f"on-chain {chain.name} head hash differs from the stored anchor record"
        for chain, chain_hash, (_, record_hash) in zip(_CHAINS, on_chain, _heads(anchor))
        if chain_hash != record_hash.lower()
    ]


def _check_ledger(session: Session, anchor: AnchorModel) -> list[str]:
    mismatches = []
    for chain, (index, hash_) in zip(_CHAINS, _heads(anchor)):
        if index == EMPTY_HEAD_INDEX:
            if hash_ != EMPTY_HEAD_HASH:
                mismatches.append(f"{chain.name} head recorded as empty but has a non-zero hash")
            continue
        block = session.get(chain.model, index)
        if block is None:
            mismatches.append(f"{chain.name} block {index} is missing")
        elif block.hash != hash_:
            mismatches.append(f"{chain.name} block {index} hash changed since anchoring")
    return mismatches


def verify_anchor(session: Session, publisher: AnchorPublisher, anchor_id: int) -> dict[str, Any]:
    anchor = get_anchor(session, anchor_id)
    if anchor is None:
        raise AnchorNotFoundError(f"anchor {anchor_id} not found")
    if anchor.tx_hash is None:
        raise AnchorNotPublishedError(f"anchor {anchor_id} has no transaction")
    on_chain = _check_on_chain(publisher, anchor)
    ledger = _check_ledger(session, anchor)
    return {
        "valid": not on_chain and not ledger,
        "on_chain_matches_record": not on_chain,
        "ledger_matches_record": not ledger,
        "mismatches": on_chain + ledger,
    }
