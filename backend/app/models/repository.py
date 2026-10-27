from datetime import date as date_type, datetime, timezone
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..chain.block import ChainBlock
from ..scraper.parser import PriceBlockRecord
from .tables import (
    AnchorModel,
    ChainBlockModel,
    ConsumptionRangeModel,
    DemoBillingRecordModel,
    PriceBlockModel,
    PriceLedgerBlockModel,
    ScenarioModel,
    SettlementBlockModel,
)


def upsert_price_blocks(session: Session, records: list[PriceBlockRecord]) -> int:
    inserted = 0
    for r in records:
        existing = session.execute(
            select(PriceBlockModel).where(
                PriceBlockModel.date == r.date,
                PriceBlockModel.market == r.market,
                PriceBlockModel.block_start == r.block_start,
            )
        ).scalar_one_or_none()
        if existing:
            existing.mcp_rs_per_mwh = r.mcp_rs_per_mwh
            existing.block_end = r.block_end
            existing.scraped_at = datetime.now(timezone.utc)
        else:
            session.add(
                PriceBlockModel(
                    date=r.date, market=r.market, block_start=r.block_start, block_end=r.block_end,
                    mcp_rs_per_mwh=r.mcp_rs_per_mwh, scraped_at=datetime.now(timezone.utc),
                )
            )
            inserted += 1
    session.commit()
    return inserted


def get_price_blocks(session: Session, delivery_date: date_type, market: str) -> list[PriceBlockModel]:
    return list(
        session.execute(
            select(PriceBlockModel)
            .where(PriceBlockModel.date == delivery_date, PriceBlockModel.market == market)
            .order_by(PriceBlockModel.block_start)
        ).scalars()
    )


def create_scenario(session: Session, name: str, ranges: list[tuple[int, int, float]]) -> ScenarioModel:
    scenario = ScenarioModel(name=name, created_at=datetime.now(timezone.utc))
    for start_minute, end_minute, predicted_kw in ranges:
        scenario.ranges.append(
            ConsumptionRangeModel(start_minute=start_minute, end_minute=end_minute, predicted_kw=predicted_kw)
        )
    session.add(scenario)
    session.commit()
    session.refresh(scenario)
    return scenario


def get_scenario(session: Session, scenario_id: int) -> ScenarioModel | None:
    return session.get(ScenarioModel, scenario_id)


def get_latest_scenario(session: Session) -> ScenarioModel | None:
    # Ordered by id (monotonic autoincrement), not created_at: two scenarios
    # created within the same clock tick would otherwise tie on timestamp.
    return session.execute(select(ScenarioModel).order_by(ScenarioModel.id.desc()).limit(1)).scalar_one_or_none()


def load_chain_blocks(session: Session) -> list[ChainBlockModel]:
    return list(session.execute(select(ChainBlockModel).order_by(ChainBlockModel.index)).scalars())


def save_chain_block(session: Session, block: ChainBlock) -> ChainBlockModel:
    model = ChainBlockModel(
        index=block.index, timestamp=block.timestamp, payload_json=block.payload,
        prev_hash=block.prev_hash, hash=block.hash,
    )
    session.add(model)
    session.commit()
    return model


def load_settlement_blocks(session: Session) -> list[SettlementBlockModel]:
    return list(session.execute(select(SettlementBlockModel).order_by(SettlementBlockModel.index)).scalars())


def save_settlement_block(session: Session, block: ChainBlock) -> SettlementBlockModel:
    model = SettlementBlockModel(
        index=block.index, timestamp=block.timestamp, payload_json=block.payload,
        prev_hash=block.prev_hash, hash=block.hash,
    )
    session.add(model)
    session.commit()
    return model


def load_price_ledger_blocks(session: Session) -> list[PriceLedgerBlockModel]:
    return list(session.execute(select(PriceLedgerBlockModel).order_by(PriceLedgerBlockModel.index)).scalars())


def save_price_ledger_block(session: Session, block: ChainBlock) -> PriceLedgerBlockModel:
    model = PriceLedgerBlockModel(
        index=block.index, timestamp=block.timestamp, payload_json=block.payload,
        prev_hash=block.prev_hash, hash=block.hash,
    )
    session.add(model)
    session.commit()
    return model


def get_demo_billing_records(session: Session) -> list[DemoBillingRecordModel]:
    return list(
        session.execute(
            select(DemoBillingRecordModel).order_by(DemoBillingRecordModel.date, DemoBillingRecordModel.time_label)
        ).scalars()
    )


def create_demo_billing_records(session: Session, records: list[dict[str, Any]]) -> list[DemoBillingRecordModel]:
    models = [DemoBillingRecordModel(**r) for r in records]
    session.add_all(models)
    session.commit()
    return models


def clear_demo_billing_records(session: Session) -> None:
    session.execute(delete(DemoBillingRecordModel))
    session.commit()


def save_anchor(session: Session, anchor: AnchorModel) -> AnchorModel:
    session.add(anchor)
    session.commit()
    return anchor


def list_anchors(session: Session) -> list[AnchorModel]:
    return list(session.execute(select(AnchorModel).order_by(AnchorModel.id.desc())).scalars())


def get_anchor(session: Session, anchor_id: int) -> AnchorModel | None:
    return session.get(AnchorModel, anchor_id)


def get_latest_confirmed_anchor(session: Session) -> AnchorModel | None:
    return session.execute(
        select(AnchorModel).where(AnchorModel.status == "confirmed").order_by(AnchorModel.id.desc()).limit(1)
    ).scalar_one_or_none()
