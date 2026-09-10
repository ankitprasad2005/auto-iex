from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_session_dep
from ..scraper.browser import ScrapeError
from ..services.scrape_service import scrape_and_record

router = APIRouter()


@router.post("/scrape/{market}")
def trigger_scrape(market: str, date: date_type, session: Session = Depends(get_session_dep)):
    if market not in ("DAM", "RTM"):
        raise HTTPException(status_code=422, detail="market must be DAM or RTM")
    try:
        result = scrape_and_record(session, market, date)
    except ScrapeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "written": result["written"],
        "skipped_duplicate": result["skipped_duplicate"],
        "chain_block_index": result["chain_block"].index if result["chain_block"] else None,
    }
