from dataclasses import dataclass
from datetime import time

MINUTES_PER_DAY = 1440
BLOCK_MINUTES = 15
BLOCKS_PER_DAY = MINUTES_PER_DAY // BLOCK_MINUTES  # 96


@dataclass(frozen=True)
class TimeBlock:
    index: int
    start_minute: int
    end_minute: int


def generate_blocks() -> list[TimeBlock]:
    return [
        TimeBlock(
            index=i,
            start_minute=i * BLOCK_MINUTES,
            end_minute=(i + 1) * BLOCK_MINUTES,
        )
        for i in range(BLOCKS_PER_DAY)
    ]


def block_index_for_minute(minute: int) -> int:
    if not (0 <= minute < MINUTES_PER_DAY):
        raise ValueError(f"minute out of range: {minute}")
    return minute // BLOCK_MINUTES


def minutes_from_time(value: time) -> int:
    return value.hour * 60 + value.minute
