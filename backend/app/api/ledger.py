from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..chain.block import ChainBlock
from ..chain.ledger import Chain
from ..db import get_session_dep
from ..models.repository import load_settlement_blocks
from ..services.settlement_service import check_and_settle_due_ranges

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


@router.get("/ledger")
def read_ledger(session: Session = Depends(get_session_dep)):
    models = load_settlement_blocks(session)
    return [
        {
            "index": m.index, "timestamp": m.timestamp.isoformat(), "payload": m.payload_json,
            "prev_hash": m.prev_hash, "hash": m.hash,
        }
        for m in models
    ]


@router.get("/ledger/verify")
def verify_ledger(session: Session = Depends(get_session_dep)):
    chain = Chain(blocks=_to_domain(load_settlement_blocks(session)))
    invalid_index = chain.verify()
    return {"valid": invalid_index is None, "invalid_block_index": invalid_index}


@router.post("/ledger/check")
def check_ledger(session: Session = Depends(get_session_dep)):
    settled = check_and_settle_due_ranges(session, datetime.now(timezone.utc))
    return {"settled_count": len(settled)}
