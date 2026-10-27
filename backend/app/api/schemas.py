from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, field_serializer


def _rupees(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


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
        return _rupees(value)


class ComparisonOut(BaseModel):
    blocks: list[BlockComparisonOut]
    dam_total_rs: Decimal
    rtm_total_rs: Decimal
    hybrid_total_rs: Decimal
    dam_pending_blocks: int
    rtm_pending_blocks: int

    @field_serializer('dam_total_rs', 'rtm_total_rs', 'hybrid_total_rs')
    def serialize_total(self, value: Decimal) -> str:
        return _rupees(value)
