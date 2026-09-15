from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..scheduler import get_rtm_scrape_interval, set_rtm_scrape_interval

router = APIRouter()


class RtmIntervalIn(BaseModel):
    seconds: int


@router.get("/scheduler/rtm-interval")
def read_rtm_interval(request: Request):
    return {"seconds": get_rtm_scrape_interval(request.app.state.scheduler)}


@router.patch("/scheduler/rtm-interval")
def update_rtm_interval(payload: RtmIntervalIn, request: Request):
    try:
        set_rtm_scrape_interval(request.app.state.scheduler, payload.seconds)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"seconds": payload.seconds}
