from decimal import Decimal

import pytest

from app.api.schemas import BlockComparisonOut, ComparisonOut


def _block(dam, rtm):
    return BlockComparisonOut(
        block_index=0, predicted_kwh=1.0, dam_cost_rs=dam, rtm_cost_rs=rtm, dam_pending=False, rtm_pending=rtm is None
    )


@pytest.mark.parametrize(
    "value, expected",
    [
        (Decimal("11250.000"), "11250.00"),  # normalize() would give 1.125E+4
        (Decimal("13000"), "13000.00"),
        (Decimal("0"), "0.00"),
        (Decimal("6187.5"), "6187.50"),
        (Decimal("4.005"), "4.01"),  # half-up to the paisa
        (Decimal("4.004"), "4.00"),
        (Decimal("0.0001"), "0.00"),
    ],
)
def test_block_costs_serialize_as_plain_rupees_with_two_decimals(value, expected):
    dumped = _block(value, value).model_dump()
    assert dumped["dam_cost_rs"] == expected
    assert dumped["rtm_cost_rs"] == expected


def test_pending_block_cost_stays_null():
    assert _block(Decimal("1"), None).model_dump()["rtm_cost_rs"] is None


def test_totals_serialize_as_plain_rupees_with_two_decimals():
    dumped = ComparisonOut(
        blocks=[],
        dam_total_rs=Decimal("217644.0885"),
        rtm_total_rs=Decimal("1.3E+4"),
        hybrid_total_rs=Decimal("171395.7305"),
        dam_pending_blocks=0,
        rtm_pending_blocks=12,
    ).model_dump()
    assert (dumped["dam_total_rs"], dumped["rtm_total_rs"], dumped["hybrid_total_rs"]) == (
        "217644.09",
        "13000.00",
        "171395.73",
    )
