from dataclasses import dataclass
from datetime import date as date_type, time as time_type
from decimal import Decimal, InvalidOperation
from typing import Literal

Market = Literal["DAM", "RTM"]

TIME_BLOCK_COLUMN: dict[str, int] = {"DAM": 0, "RTM": 3}


class TableParseError(Exception):
    pass


@dataclass(frozen=True)
class PriceBlockRecord:
    date: date_type
    market: Market
    block_start: time_type
    block_end: time_type
    mcp_rs_per_mwh: Decimal


def _parse_time_block(cell: str) -> tuple[time_type, time_type]:
    try:
        start_str, end_str = (part.strip() for part in cell.split("-"))
        start_h, start_m = (int(x) for x in start_str.split(":"))
        end_h, end_m = (int(x) for x in end_str.split(":"))
    except (ValueError, AttributeError) as exc:
        raise TableParseError(f"invalid time block cell: {cell!r}") from exc
    end_time = time_type(0, 0) if (end_h, end_m) == (24, 0) else time_type(end_h, end_m)
    return time_type(start_h, start_m), end_time


def _parse_mcp(cell: str) -> Decimal:
    cleaned = cell.replace(",", "").strip()
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise TableParseError(f"invalid MCP cell: {cell!r}") from exc


def parse_rows(rows: list[list[str]], market: Market, delivery_date: date_type) -> list[PriceBlockRecord]:
    if not rows:
        raise TableParseError("no rows to parse")
    time_col = TIME_BLOCK_COLUMN[market]
    records = []
    for row in rows:
        if len(row) <= time_col:
            raise TableParseError(f"row too short for market {market}: {row!r}")
        start, end = _parse_time_block(row[time_col])
        mcp = _parse_mcp(row[-1])
        records.append(
            PriceBlockRecord(date=delivery_date, market=market, block_start=start, block_end=end, mcp_rs_per_mwh=mcp)
        )
    return records
