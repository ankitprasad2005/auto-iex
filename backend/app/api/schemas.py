from decimal import Decimal

from pydantic import BaseModel, field_serializer


class ConsumptionRangeIn(BaseModel):
    start_time: str
    end_time: str
    predicted_kw: float


class ScenarioIn(BaseModel):
    name: str
    ranges: list[ConsumptionRangeIn]


class BlockComparisonOut(BaseModel):
    block_index: int
    predicted_kwh: float
    dam_cost_rs: Decimal | None
    rtm_cost_rs: Decimal | None
    dam_pending: bool
    rtm_pending: bool

    @field_serializer('dam_cost_rs', 'rtm_cost_rs')
    def serialize_cost(self, value: Decimal | None) -> str | None:
        if value is None:
            return None
        return str(value.normalize())


class ComparisonOut(BaseModel):
    blocks: list[BlockComparisonOut]
    dam_total_rs: Decimal
    rtm_total_rs: Decimal
    hybrid_total_rs: Decimal
    dam_pending_blocks: int
    rtm_pending_blocks: int

    @field_serializer('dam_total_rs', 'rtm_total_rs', 'hybrid_total_rs')
    def serialize_total(self, value: Decimal) -> str:
        return str(value.normalize())
