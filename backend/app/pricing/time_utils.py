from datetime import datetime, timedelta, timezone

MINUTES_PER_DAY = 1440

# IEX market days and time blocks are defined in IST, which has no DST.
IST = timezone(timedelta(hours=5, minutes=30), "IST")


def hhmm_to_minutes(value: str) -> int:
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError(f"invalid time format: {value!r}, expected HH:MM")
    hours_str, minutes_str = parts
    if not (hours_str.isdigit() and minutes_str.isdigit()):
        raise ValueError(f"invalid time format: {value!r}, expected HH:MM")
    hours, minutes = int(hours_str), int(minutes_str)
    if not (0 <= hours <= 24 and 0 <= minutes < 60):
        raise ValueError(f"invalid time value: {value!r}")
    total = hours * 60 + minutes
    if total > MINUTES_PER_DAY:
        raise ValueError(f"time out of range: {value!r}")
    return total


def to_market_time(instant: datetime) -> datetime:
    return instant.astimezone(IST)
