from datetime import timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..chain.block import ChainBlock
from ..chain.ledger import Chain
from ..db import get_session_dep
from ..models.repository import load_chain_blocks

router = APIRouter()


def _to_domain(models) -> list[ChainBlock]:
    # DATETIME columns round-trip as naive (tzinfo stripped by the DB driver),
    # but every block was hashed against a UTC-aware timestamp when created.
    # Re-attaching UTC here keeps compute_hash()'s input identical to what it
    # was at creation time, so verify() doesn't flag untampered blocks.
    return [
        ChainBlock(
            index=m.index,
            timestamp=m.timestamp if m.timestamp.tzinfo else m.timestamp.replace(tzinfo=timezone.utc),
            payload=m.payload_json,
            prev_hash=m.prev_hash,
            hash=m.hash
        )
        for m in models
    ]


@router.get("/chain")
def read_chain(session: Session = Depends(get_session_dep)):
    models = load_chain_blocks(session)
    return [
        {
            "index": m.index, "timestamp": m.timestamp.isoformat(), "payload": m.payload_json,
            "prev_hash": m.prev_hash, "hash": m.hash,
        }
        for m in models
    ]


@router.get("/chain/verify")
def verify_chain(session: Session = Depends(get_session_dep)):
    chain = Chain(blocks=_to_domain(load_chain_blocks(session)))
    invalid_index = chain.verify()
    return {"valid": invalid_index is None, "invalid_block_index": invalid_index}
