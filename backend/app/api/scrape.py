import logging
from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_session_dep
from ..scraper.browser import ScrapeError
from ..scraper.parser import TableParseError
from ..services.scrape_service import scrape_and_record

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/scrape/{market}")
def trigger_scrape(market: str, date: date_type, session: Session = Depends(get_session_dep)):
    if market not in ("DAM", "RTM"):
        raise HTTPException(status_code=422, detail="market must be DAM or RTM")
    try:
        result = scrape_and_record(session, market, date)
    except (ScrapeError, TableParseError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        # Any exception that escapes here as a plain 500 unwinds past
        # CORSMiddleware without CORS headers attached (a Starlette/FastAPI
        # quirk: ServerErrorMiddleware sits outside user-added middleware),
        # which a browser reports as an opaque "Failed to fetch" instead of
        # the real status. Converting every failure mode to HTTPException
        # keeps the response on the path that preserves CORS headers.
        logger.exception("unexpected error while scraping %s for %s", market, date)
        raise HTTPException(status_code=502, detail="unexpected error while scraping") from exc
    return {
        "written": result["written"],
        "skipped_duplicate": result["skipped_duplicate"],
        "chain_block_index": result["chain_block"].index if result["chain_block"] else None,
    }
