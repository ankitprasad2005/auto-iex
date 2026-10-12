from datetime import date, timedelta
from decimal import Decimal

from app.models.repository import get_demo_billing_records
from app.services.billing_service import DEMO_DAYS, generate_demo_billing_history

TODAY = date(2026, 9, 15)


def test_generates_records_spanning_the_trailing_month(db_session):
    records = generate_demo_billing_history(db_session, TODAY)
    assert len(records) > 0

    dates = {r.date for r in records}
    earliest_allowed = TODAY - timedelta(days=DEMO_DAYS)
    assert min(dates) >= earliest_allowed
    assert max(dates) < TODAY
    # every day in the window should have at least one entry
    assert len(dates) == DEMO_DAYS


def test_records_have_plausible_positive_values(db_session):
    records = generate_demo_billing_history(db_session, TODAY)
    for r in records:
        assert r.kwh > 0
        assert r.cost_rs > 0
        assert r.market in ("DAM", "RTM")
        assert r.time_label  # non-empty


def test_is_deterministic_across_calls_for_the_same_today(db_session):
    first = generate_demo_billing_history(db_session, TODAY)
    first_snapshot = [(r.date, r.time_label, r.market, r.kwh, r.cost_rs) for r in first]

    second = generate_demo_billing_history(db_session, TODAY)
    second_snapshot = [(r.date, r.time_label, r.market, r.kwh, r.cost_rs) for r in second]

    assert first_snapshot == second_snapshot


def test_regenerating_clears_previous_demo_data_instead_of_accumulating(db_session):
    generate_demo_billing_history(db_session, TODAY)
    first_count = len(get_demo_billing_records(db_session))

    generate_demo_billing_history(db_session, TODAY)
    second_count = len(get_demo_billing_records(db_session))

    assert first_count == second_count  # replaced, not doubled


def test_cost_is_consistent_with_kwh_and_an_implied_price(db_session):
    records = generate_demo_billing_history(db_session, TODAY)
    for r in records:
        # cost_rs = kwh * price_rs_per_mwh / 1000 for some plausible IEX-range
        # price; back-solve and sanity-check it lands in a believable band
        # rather than asserting an exact formula (the generator is free to
        # vary price per entry).
        implied_price_per_mwh = (r.cost_rs / r.kwh) * Decimal(1000)
        assert Decimal("500") <= implied_price_per_mwh <= Decimal("12000")
