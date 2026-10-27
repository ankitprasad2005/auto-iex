from datetime import datetime, timedelta, timezone

import pytest

from app.pricing.time_utils import IST, hhmm_to_minutes, to_market_time


@pytest.mark.parametrize(
    "value,expected",
    [
        ("00:00", 0),
        ("09:30", 570),
        ("23:45", 1425),
        ("24:00", 1440),
    ],
)
def test_hhmm_to_minutes_valid(value, expected):
    assert hhmm_to_minutes(value) == expected


@pytest.mark.parametrize(
    "value",
    ["abc", "12", "12:60", "25:00", "-1:00", "12:3:4", ""],
)
def test_hhmm_to_minutes_invalid(value):
    with pytest.raises(ValueError):
        hhmm_to_minutes(value)


def test_ist_is_utc_plus_five_thirty():
    assert IST.utcoffset(None) == timedelta(hours=5, minutes=30)


def test_to_market_time_converts_utc_instant_to_ist_wall_clock():
    local = to_market_time(datetime(2026, 10, 27, 12, 30, tzinfo=timezone.utc))
    assert (local.date().isoformat(), local.hour, local.minute) == ("2026-10-27", 18, 0)


def test_to_market_time_rolls_over_to_next_ist_day_after_1830_utc():
    local = to_market_time(datetime(2026, 10, 27, 18, 30, tzinfo=timezone.utc))
    assert (local.date().isoformat(), local.hour, local.minute) == ("2026-10-28", 0, 0)


def test_to_market_time_keeps_ist_input_unchanged():
    ist_now = datetime(2026, 10, 27, 9, 15, tzinfo=IST)
    assert to_market_time(ist_now) == ist_now
    assert to_market_time(ist_now).hour == 9
