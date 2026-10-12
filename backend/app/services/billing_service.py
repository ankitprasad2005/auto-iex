import random
from datetime import date as date_type, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from ..models.repository import clear_demo_billing_records, create_demo_billing_records
from ..models.tables import DemoBillingRecordModel

DEMO_DAYS = 30
DEMO_SEED = 42  # fixed: same reproducible demo dataset on every click/run
TIME_SLOTS = ["06:00-09:00", "09:00-12:00", "12:00-15:00", "18:00-21:00", "21:00-23:00"]
MARKETS = ["DAM", "RTM"]
KWH_RANGE = (1.0, 8.0)
PRICE_RS_PER_MWH_RANGE = (2500.0, 6000.0)


def generate_demo_billing_history(session: Session, today: date_type) -> list[DemoBillingRecordModel]:
    """Replace any existing demo data with a fresh, reproducible month of
    fabricated billing history ending the day before `today`.

    Deterministic (fixed RNG seed) so the "Load Demo Data" button always
    shows the same dataset — useful for a repeatable demo/presentation
    rather than different numbers every click.
    """
    clear_demo_billing_records(session)
    rng = random.Random(DEMO_SEED)

    records = []
    for day_offset in range(DEMO_DAYS, 0, -1):
        day = today - timedelta(days=day_offset)
        for _ in range(rng.randint(1, 3)):
            kwh = round(rng.uniform(*KWH_RANGE), 3)
            price_rs_per_mwh = round(rng.uniform(*PRICE_RS_PER_MWH_RANGE), 2)
            cost_rs = round(kwh * price_rs_per_mwh / 1000, 2)
            records.append(
                {
                    "date": day,
                    "time_label": rng.choice(TIME_SLOTS),
                    "market": rng.choice(MARKETS),
                    "kwh": Decimal(str(kwh)),
                    "cost_rs": Decimal(str(cost_rs)),
                    "created_at": datetime.now(timezone.utc),
                }
            )

    return create_demo_billing_records(session, records)
