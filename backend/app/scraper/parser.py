import re
from dataclasses import dataclass
from datetime import date as date_type, time as time_type
from decimal import Decimal, InvalidOperation
from typing import Literal

Market = Literal["DAM", "RTM"]

# Matches "00:00 - 00:15" and "00:00-00:15" (IEX renders the separator with
# or without surrounding spaces depending on market).
TIME_BLOCK_PATTERN = re.compile(r"^\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}$")


class TableParseError(Exception):
    pass


@dataclass(frozen=True)
class PriceBlockRecord:
    date: date_type
    market: Market
    block_start: time_type
    block_end: time_type
    mcp_rs_per_mwh: Decimal


def _find_time_block_cell(row: list[str]) -> str | None:
    # IEX renders the Date/Hour/Session leading columns with HTML rowspan,
    # so only the first row of each spanned group carries those cells —
    # every other row is missing them, shifting the time-block cell's index.
    # Searching by pattern instead of a fixed column index is what makes
    # this robust to that layout instead of breaking on ~75% of real rows.
    for cell in row:
        stripped = cell.strip()
        if TIME_BLOCK_PATTERN.match(stripped):
            return stripped
    return None


def _parse_time_block(cell: str) -> tuple[time_type, time_type]:
    try:
        start_str, end_str = (part.strip() for part in cell.split("-"))
        start_h, start_m = (int(x) for x in start_str.split(":"))
        end_h, end_m = (int(x) for x in end_str.split(":"))
        end_time = time_type(0, 0) if (end_h, end_m) == (24, 0) else time_type(end_h, end_m)
        start_time = time_type(start_h, start_m)
    except (ValueError, AttributeError) as exc:
        raise TableParseError(f"invalid time block cell: {cell!r}") from exc
    return start_time, end_time


def _parse_mcp(cell: str) -> Decimal:
    cleaned = cell.replace(",", "").strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise TableParseError(f"invalid MCP cell: {cell!r}") from exc


def parse_rows(rows: list[list[str]], market: Market, delivery_date: date_type) -> list[PriceBlockRecord]:
    if not rows:
        raise TableParseError("no rows to parse")

    records = []
    for row in rows:
        time_cell = _find_time_block_cell(row)
        if time_cell is None:
            # Trailing summary rows (Total/Max/Min/Avg) carry no time block
            # and aren't price data — skip them rather than failing the scrape.
            continue
        start, end = _parse_time_block(time_cell)
        mcp = _parse_mcp(row[-1])
        records.append(
            PriceBlockRecord(date=delivery_date, market=market, block_start=start, block_end=end, mcp_rs_per_mwh=mcp)
        )

    if not records:
        raise TableParseError(f"no time-block rows found for market {market}")
    return records
