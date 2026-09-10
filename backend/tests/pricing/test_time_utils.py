import pytest

from app.pricing.time_utils import hhmm_to_minutes


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
