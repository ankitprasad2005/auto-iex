from datetime import date as date_type

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_session_dep
from ..models.repository import get_price_blocks

router = APIRouter()


@router.get("/prices")
def read_prices(date: date_type = Query(...), market: str = Query(...), session: Session = Depends(get_session_dep)):
    blocks = get_price_blocks(session, date, market)
    return [
        {
            "block_start": b.block_start.isoformat(),
            "block_end": b.block_end.isoformat(),
            "mcp_rs_per_mwh": str(b.mcp_rs_per_mwh),
        }
        for b in blocks
    ]
