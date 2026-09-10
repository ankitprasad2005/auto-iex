from dataclasses import dataclass

from .blocks import TimeBlock, generate_blocks, MINUTES_PER_DAY


@dataclass(frozen=True)
class ConsumptionRange:
    start_minute: int
    end_minute: int
    predicted_kw: float

    def __post_init__(self):
        if self.start_minute < 0 or self.end_minute > MINUTES_PER_DAY:
            raise ValueError("range must be within a single day (0-1440 minutes)")
        if self.end_minute <= self.start_minute:
            raise ValueError("end_minute must be greater than start_minute")
        if self.predicted_kw <= 0:
            raise ValueError("predicted_kw must be positive")


def allocate_to_blocks(
    ranges: list[ConsumptionRange],
    blocks: list[TimeBlock] | None = None,
) -> dict[int, float]:
    blocks = blocks if blocks is not None else generate_blocks()
    result: dict[int, float] = {b.index: 0.0 for b in blocks}
    for r in ranges:
        for b in blocks:
            overlap_minutes = min(r.end_minute, b.end_minute) - max(r.start_minute, b.start_minute)
            if overlap_minutes > 0:
                result[b.index] += r.predicted_kw * (overlap_minutes / 60)
    return result
