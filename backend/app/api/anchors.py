from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import config
from ..anchoring.publisher import AnchorPublisher, get_publisher
from ..db import get_session_dep
from ..models.repository import list_anchors
from ..models.tables import AnchorModel
from ..services.anchor_service import (
    AnchorNotFoundError,
    AnchorNotPublishedError,
    anchor_chain_heads,
    verify_anchor,
)

router = APIRouter()


def get_anchor_publisher() -> AnchorPublisher | None:
    return get_publisher()


def _require(publisher: AnchorPublisher | None) -> AnchorPublisher:
    if publisher is None:
        raise HTTPException(status_code=503, detail="anchoring not configured")
    return publisher


def _serialize(anchor: AnchorModel) -> dict:
    created_at = anchor.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return {
        "id": anchor.id,
        "created_at": created_at.isoformat(),
        "scrape_head_index": anchor.scrape_head_index,
        "scrape_head_hash": anchor.scrape_head_hash,
        "settlement_head_index": anchor.settlement_head_index,
        "settlement_head_hash": anchor.settlement_head_hash,
        "price_ledger_head_index": anchor.price_ledger_head_index,
        "price_ledger_head_hash": anchor.price_ledger_head_hash,
        "tx_hash": anchor.tx_hash,
        "status": anchor.status,
        "block_number": anchor.block_number,
        "error": anchor.error,
        "explorer_url": config.ANCHOR_EXPLORER_TX_URL + anchor.tx_hash if anchor.tx_hash else None,
    }


@router.get("/anchors/status")
def read_anchor_status(publisher: AnchorPublisher | None = Depends(get_anchor_publisher)):
    return {
        "enabled": publisher is not None,
        "network": "Polygon Amoy",
        "chain_id": config.ANCHOR_CHAIN_ID,
        "wallet_address": publisher.address if publisher is not None else None,
        "explorer_tx_url": config.ANCHOR_EXPLORER_TX_URL,
    }


@router.get("/anchors")
def read_anchors(session: Session = Depends(get_session_dep)):
    return [_serialize(a) for a in list_anchors(session)]


@router.post("/anchors/now")
def anchor_now(
    session: Session = Depends(get_session_dep),
    publisher: AnchorPublisher | None = Depends(get_anchor_publisher),
):
    anchor, reason = anchor_chain_heads(session, _require(publisher), datetime.now(timezone.utc))
    return {
        "anchored": reason is None,
        "reason": reason,
        "anchor": _serialize(anchor) if anchor is not None else None,
    }


@router.get("/anchors/{anchor_id}/verify")
def verify(
    anchor_id: int,
    session: Session = Depends(get_session_dep),
    publisher: AnchorPublisher | None = Depends(get_anchor_publisher),
):
    try:
        return verify_anchor(session, _require(publisher), anchor_id)
    except AnchorNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AnchorNotPublishedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
