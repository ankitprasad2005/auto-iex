from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_session_dep
from ..models.repository import create_scenario, get_scenario
from ..pricing.allocation import ConsumptionRange
from ..pricing.time_utils import hhmm_to_minutes
from ..services.comparison_service import build_comparison
from .schemas import BlockComparisonOut, ComparisonOut, ScenarioIn

router = APIRouter()


@router.post("/scenarios")
def post_scenario(payload: ScenarioIn, session: Session = Depends(get_session_dep)):
    try:
        parsed_ranges = [
            (hhmm_to_minutes(r.start_time), hhmm_to_minutes(r.end_time), r.predicted_kw) for r in payload.ranges
        ]
        for start, end, kw in parsed_ranges:
            ConsumptionRange(start_minute=start, end_minute=end, predicted_kw=kw)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    scenario = create_scenario(session, payload.name, parsed_ranges)
    return {"id": scenario.id, "name": scenario.name}


@router.get("/scenarios/{scenario_id}/comparison", response_model=ComparisonOut)
def get_comparison(scenario_id: int, date: date_type, session: Session = Depends(get_session_dep)):
    scenario = get_scenario(session, scenario_id)
    if scenario is None:
        raise HTTPException(status_code=404, detail="scenario not found")

    ranges = [
        ConsumptionRange(start_minute=r.start_minute, end_minute=r.end_minute, predicted_kw=float(r.predicted_kw))
        for r in scenario.ranges
    ]
    result = build_comparison(session, date, ranges)
    return ComparisonOut(
        blocks=[BlockComparisonOut(**vars(b)) for b in result.blocks],
        dam_total_rs=result.totals.dam_total_rs,
        rtm_total_rs=result.totals.rtm_total_rs,
        hybrid_total_rs=result.totals.hybrid_total_rs,
        dam_pending_blocks=result.totals.dam_pending_blocks,
        rtm_pending_blocks=result.totals.rtm_pending_blocks,
    )
