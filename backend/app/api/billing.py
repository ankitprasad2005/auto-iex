from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_session_dep
from ..models.repository import get_demo_billing_records
from ..services.billing_service import generate_demo_billing_history

router = APIRouter()


@router.post("/billing/demo")
def load_demo_billing(session: Session = Depends(get_session_dep)):
    records = generate_demo_billing_history(session, datetime.now(timezone.utc).date())
    return {"created_count": len(records)}


@router.get("/billing/history")
def read_billing_history(session: Session = Depends(get_session_dep)):
    records = get_demo_billing_records(session)
    total_kwh = sum((r.kwh for r in records), Decimal(0))
    total_cost_rs = sum((r.cost_rs for r in records), Decimal(0))
    return {
        "records": [
            {
                "date": r.date.isoformat(),
                "time_label": r.time_label,
                "market": r.market,
                "kwh": str(r.kwh),
                "cost_rs": str(r.cost_rs),
            }
            for r in records
        ],
        "total_kwh": str(total_kwh),
        "total_cost_rs": str(total_cost_rs),
    }
