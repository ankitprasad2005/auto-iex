from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, Numeric, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PriceBlockModel(Base):
    __tablename__ = "price_blocks"
    __table_args__ = (UniqueConstraint("date", "market", "block_start", name="uq_price_block"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    market: Mapped[str] = mapped_column(String(3), nullable=False)
    block_start: Mapped[time] = mapped_column(Time, nullable=False)
    block_end: Mapped[time] = mapped_column(Time, nullable=False)
    mcp_rs_per_mwh: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class ScenarioModel(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    ranges: Mapped[list["ConsumptionRangeModel"]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan"
    )


class ConsumptionRangeModel(Base):
    __tablename__ = "consumption_ranges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("scenarios.id"), nullable=False)
    start_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    end_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_kw: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)

    scenario: Mapped["ScenarioModel"] = relationship(back_populates="ranges")


class ChainBlockModel(Base):
    __tablename__ = "chain_blocks"

    index: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    prev_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    hash: Mapped[str] = mapped_column(String(64), nullable=False)
