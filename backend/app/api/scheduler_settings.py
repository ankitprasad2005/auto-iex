from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..scheduler import (
    ANCHOR_JOB_ID,
    MIN_ANCHOR_INTERVAL_SECONDS,
    MIN_RTM_INTERVAL_SECONDS,
    RTM_SCRAPE_JOB_ID,
    get_job_interval,
    set_job_interval,
)

router = APIRouter()


class IntervalIn(BaseModel):
    seconds: int


def _read(request: Request, job_id: str) -> dict:
    return {"seconds": get_job_interval(request.app.state.scheduler, job_id)}


def _update(request: Request, job_id: str, seconds: int, minimum: int) -> dict:
    try:
        set_job_interval(request.app.state.scheduler, job_id, seconds, minimum)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"seconds": seconds}


@router.get("/scheduler/rtm-interval")
def read_rtm_interval(request: Request):
    return _read(request, RTM_SCRAPE_JOB_ID)


@router.patch("/scheduler/rtm-interval")
def update_rtm_interval(payload: IntervalIn, request: Request):
    return _update(request, RTM_SCRAPE_JOB_ID, payload.seconds, MIN_RTM_INTERVAL_SECONDS)


@router.get("/scheduler/anchor-interval")
def read_anchor_interval(request: Request):
    return _read(request, ANCHOR_JOB_ID)


@router.patch("/scheduler/anchor-interval")
def update_anchor_interval(payload: IntervalIn, request: Request):
    return _update(request, ANCHOR_JOB_ID, payload.seconds, MIN_ANCHOR_INTERVAL_SECONDS)
