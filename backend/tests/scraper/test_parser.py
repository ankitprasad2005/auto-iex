from datetime import date, time
from decimal import Decimal

import pytest

from app.scraper.parser import parse_rows, TableParseError


# Real IEX tables use HTML rowspan on the leading Date/Hour/Session columns,
# so most rows only carry the trailing cells; the first row of each spanned
# group carries extra leading cells. Column position of the time-block cell
# therefore varies row to row — these fixtures mirror what the live DAM and
# RTM snapshot pages actually return.
DAM_ROWS = [
    ["12-09-2026", "1", "00:00 - 00:15", "77800.80", "867.10", "867.08", "867.08", "3,245.50"],
    ["00:15 - 00:30", "77386.70", "887.80", "887.79", "887.79", "3,100.00"],
    ["2", "01:00 - 01:15", "71315.90", "942.30", "942.29", "942.29", "3,000.00"],
    ["12-09-2026", "Total (MWh)", "1346505.08", "190221.88", "139575.53", "139575.53", "-"],
    ["12-09-2026", "Max (MW)", "83249.30", "27446.50", "16635.38", "16635.38", "10000.00"],
    ["12-09-2026", "Min (MW)", "29103.40", "760.60", "760.60", "760.60", "2710.52"],
    ["12-09-2026", "Avg (MW)", "56104.38", "7925.91", "5815.65", "5815.65", "8364.10"],
]

RTM_ROWS = [
    ["12-09-2026", "1", "1", "00:00-00:15", "64027.10", "3323.30", "3323.30", "3323.30", "2,900.00"],
    ["00:15-00:30", "63998.50", "3100.40", "3100.40", "3100.40", "2,950.00"],
    ["2", "00:30-00:45", "70163.70", "3212.90", "3212.90", "3212.90", "3,000.00"],
    ["12-09-2026", "Total (MWh)", "613728.53", "100534.93", "88451.87", "88451.87", "-"],
]


def test_parse_rows_dam_finds_time_block_regardless_of_leading_column_count():
    records = parse_rows(DAM_ROWS, "DAM", date(2026, 9, 12))
    assert len(records) == 3
    assert records[0].block_start == time(0, 0)
    assert records[0].block_end == time(0, 15)
    assert records[0].mcp_rs_per_mwh == Decimal("3245.50")
    assert records[0].market == "DAM"
    assert records[0].date == date(2026, 9, 12)
    assert records[1].block_start == time(0, 15)
    assert records[2].block_start == time(1, 0)


def test_parse_rows_rtm_handles_dash_without_spaces():
    records = parse_rows(RTM_ROWS, "RTM", date(2026, 9, 12))
    assert len(records) == 3
    assert records[0].block_start == time(0, 0)
    assert records[0].block_end == time(0, 15)
    assert records[0].mcp_rs_per_mwh == Decimal("2900.00")


def test_parse_rows_skips_trailing_summary_rows():
    records = parse_rows(DAM_ROWS, "DAM", date(2026, 9, 12))
    # 4 summary rows (Total/Max/Min/Avg) in the fixture must not become records
    assert all(r.block_start != None for r in records)  # noqa: E711 - sanity, no summary leaked through
    assert len(records) == 3


def test_parse_rows_last_block_wraps_to_midnight():
    rows = [["23:45 - 24:00", "1", "1", "1", "1", "100"]]
    records = parse_rows(rows, "DAM", date(2026, 9, 10))
    assert records[0].block_start == time(23, 45)
    assert records[0].block_end == time(0, 0)


def test_parse_rows_empty_raises():
    with pytest.raises(TableParseError):
        parse_rows([], "DAM", date(2026, 9, 10))


def test_parse_rows_all_summary_rows_raises():
    rows = [
        ["12-09-2026", "Total (MWh)", "1", "2", "3", "4", "-"],
        ["12-09-2026", "Max (MW)", "1", "2", "3", "4", "10000.00"],
    ]
    with pytest.raises(TableParseError):
        parse_rows(rows, "DAM", date(2026, 9, 10))


def test_parse_rows_malformed_mcp_raises():
    with pytest.raises(TableParseError):
        parse_rows([["00:00 - 00:15", "1", "1", "1", "1", "N/A"]], "DAM", date(2026, 9, 10))


def test_parse_rows_time_block_with_out_of_range_hour_raises():
    # Matches the digit-shape pattern (\d{1,2}:\d{2}-\d{1,2}:\d{2}) but "25"
    # isn't a valid hour, so time_type() rejects it after the regex passes.
    with pytest.raises(TableParseError):
        parse_rows([["25:00 - 25:15", "1", "1", "1", "1", "100"]], "DAM", date(2026, 9, 10))
