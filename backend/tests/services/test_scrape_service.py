from datetime import date

from app.models.repository import load_chain_blocks
from app.services.scrape_service import scrape_and_record


def _generate_dam_rows(price: str) -> list[list[str]]:
    """Generate 96 rows for 15-minute intervals in a day."""
    rows = []
    for i in range(96):
        start_hour = i // 4
        start_minute = (i % 4) * 15
        end_hour = start_hour
        end_minute = start_minute + 15
        if end_minute == 60:
            end_hour += 1
            end_minute = 0
        time_block = f"{start_hour:02d}:{start_minute:02d} - {end_hour:02d}:{end_minute:02d}"
        rows.append([time_block, "1", "1", "1", "1", price])
    return rows


DAM_ROWS_A = _generate_dam_rows("3245.50")
DAM_ROWS_B = _generate_dam_rows("3300.00")


def test_scrape_and_record_first_scrape_appends_chain_block(db_session):
    result = scrape_and_record(db_session, "DAM", date(2026, 9, 10), fetch_fn=lambda: DAM_ROWS_A)
    assert result["written"] == 96
    assert result["skipped_duplicate"] is False
    assert result["chain_block"] is not None
    assert len(load_chain_blocks(db_session)) == 2  # genesis + 1


def test_scrape_and_record_identical_rescrape_is_idempotent(db_session):
    scrape_and_record(db_session, "DAM", date(2026, 9, 10), fetch_fn=lambda: DAM_ROWS_A)
    result = scrape_and_record(db_session, "DAM", date(2026, 9, 10), fetch_fn=lambda: DAM_ROWS_A)
    assert result["skipped_duplicate"] is True
    assert result["chain_block"] is None
    assert len(load_chain_blocks(db_session)) == 2  # unchanged


def test_scrape_and_record_changed_data_appends_new_chain_block(db_session):
    scrape_and_record(db_session, "DAM", date(2026, 9, 10), fetch_fn=lambda: DAM_ROWS_A)
    result = scrape_and_record(db_session, "DAM", date(2026, 9, 10), fetch_fn=lambda: DAM_ROWS_B)
    assert result["skipped_duplicate"] is False
    assert result["chain_block"] is not None
    assert len(load_chain_blocks(db_session)) == 3
