from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.tables import (
    ChainBlockModel,
    ConsumptionRangeModel,
    PriceBlockModel,
    ScenarioModel,
    SettlementBlockModel,
)


def test_tables_create_and_roundtrip():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, future=True)()

    price = PriceBlockModel(
        date=date(2026, 9, 10), market="DAM", block_start=time(0, 0), block_end=time(0, 15),
        mcp_rs_per_mwh=Decimal("3245.50"), scraped_at=datetime.now(timezone.utc),
    )
    scenario = ScenarioModel(name="test", created_at=datetime.now(timezone.utc))
    scenario.ranges.append(ConsumptionRangeModel(start_minute=0, end_minute=15, predicted_kw=Decimal("4.0")))
    chain_block = ChainBlockModel(
        index=0, timestamp=datetime.now(timezone.utc), payload_json={"genesis": True},
        prev_hash="0" * 64, hash="a" * 64,
    )
    settlement_block = SettlementBlockModel(
        index=0, timestamp=datetime.now(timezone.utc), payload_json={"genesis": True},
        prev_hash="0" * 64, hash="b" * 64,
    )

    session.add_all([price, scenario, chain_block, settlement_block])
    session.commit()

    assert session.query(PriceBlockModel).count() == 1
    assert session.query(ScenarioModel).one().ranges[0].predicted_kw == Decimal("4.0")
    assert session.query(ChainBlockModel).one().payload_json == {"genesis": True}
    assert session.query(SettlementBlockModel).one().payload_json == {"genesis": True}
    session.close()
    engine.dispose()
