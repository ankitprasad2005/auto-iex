from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..chain.block import ChainBlock
from ..chain.ledger import Chain
from ..db import get_session_dep
from ..models.repository import load_price_ledger_blocks
from ..services.price_ledger_service import check_and_record_price_blocks

router = APIRouter()


def _to_domain(models) -> list[ChainBlock]:
    # See app/api/chain.py for why tzinfo is re-attached: DATETIME columns
    # round-trip naive, but blocks were hashed against a UTC-aware timestamp.
    return [
        ChainBlock(
            index=m.index,
            timestamp=m.timestamp if m.timestamp.tzinfo else m.timestamp.replace(tzinfo=timezone.utc),
            payload=m.payload_json,
            prev_hash=m.prev_hash,
            hash=m.hash,
        )
        for m in models
    ]


@router.get("/price-ledger")
def read_price_ledger(session: Session = Depends(get_session_dep)):
    models = load_price_ledger_blocks(session)
    return [
        {
            "index": m.index, "timestamp": m.timestamp.isoformat(), "payload": m.payload_json,
            "prev_hash": m.prev_hash, "hash": m.hash,
        }
        for m in models
    ]


@router.get("/price-ledger/verify")
def verify_price_ledger(session: Session = Depends(get_session_dep)):
    chain = Chain(blocks=_to_domain(load_price_ledger_blocks(session)))
    invalid_index = chain.verify()
    return {"valid": invalid_index is None, "invalid_block_index": invalid_index}


@router.post("/price-ledger/check")
def check_price_ledger(session: Session = Depends(get_session_dep)):
    recorded = check_and_record_price_blocks(session, datetime.now(timezone.utc))
    return {"recorded_count": len(recorded)}
