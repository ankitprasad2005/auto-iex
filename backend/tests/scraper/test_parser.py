from datetime import date, time
from decimal import Decimal

import pytest

from app.scraper.parser import parse_rows, TableParseError


DAM_ROWS = [
    ["00:00 - 00:15", "1000", "900", "850", "850", "3,245.50"],
    ["00:15 - 00:30", "1100", "950", "900", "900", "3,100.00"],
]

RTM_ROWS = [
    ["10-09-2026", "00", "1", "00:00 - 00:15", "500", "450", "420", "420", "2,900.00"],
]


def test_parse_rows_dam():
    records = parse_rows(DAM_ROWS, "DAM", date(2026, 9, 10))
    assert len(records) == 2
    assert records[0].block_start == time(0, 0)
    assert records[0].block_end == time(0, 15)
    assert records[0].mcp_rs_per_mwh == Decimal("3245.50")
    assert records[0].market == "DAM"
    assert records[0].date == date(2026, 9, 10)


def test_parse_rows_rtm_uses_correct_time_block_column():
    records = parse_rows(RTM_ROWS, "RTM", date(2026, 9, 10))
    assert len(records) == 1
    assert records[0].block_start == time(0, 0)
    assert records[0].block_end == time(0, 15)
    assert records[0].mcp_rs_per_mwh == Decimal("2900.00")


def test_parse_rows_last_block_wraps_to_midnight():
    rows = [["23:45 - 24:00", "1", "1", "1", "1", "100"]]
    records = parse_rows(rows, "DAM", date(2026, 9, 10))
    assert records[0].block_start == time(23, 45)
    assert records[0].block_end == time(0, 0)


def test_parse_rows_empty_raises():
    with pytest.raises(TableParseError):
        parse_rows([], "DAM", date(2026, 9, 10))


def test_parse_rows_row_too_short_raises():
    with pytest.raises(TableParseError):
        parse_rows([["only one cell"]], "RTM", date(2026, 9, 10))


def test_parse_rows_malformed_time_block_raises():
    with pytest.raises(TableParseError):
        parse_rows([["not a time", "1", "1", "1", "1", "100"]], "DAM", date(2026, 9, 10))


def test_parse_rows_malformed_mcp_raises():
    with pytest.raises(TableParseError):
        parse_rows([["00:00 - 00:15", "1", "1", "1", "1", "N/A"]], "DAM", date(2026, 9, 10))
