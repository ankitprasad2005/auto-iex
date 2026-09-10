import pytest

from app.pricing.allocation import ConsumptionRange, allocate_to_blocks
from app.pricing.blocks import generate_blocks, BLOCKS_PER_DAY


@pytest.mark.parametrize(
    "start,end,kw",
    [
        (0, 0, 5),      # zero-length
        (100, 50, 5),   # end before start
        (1430, 10, 5),  # midnight-spanning (end < start in same-day encoding)
        (0, 15, 0),     # zero power
        (0, 15, -5),    # negative power
        (-1, 15, 5),    # start below range
        (0, 1441, 5),   # end beyond day
    ],
)
def test_consumption_range_rejects_invalid(start, end, kw):
    with pytest.raises(ValueError):
        ConsumptionRange(start_minute=start, end_minute=end, predicted_kw=kw)


def test_allocate_empty_ranges_returns_all_zero_for_96_blocks():
    result = allocate_to_blocks([])
    assert len(result) == BLOCKS_PER_DAY
    assert all(v == 0.0 for v in result.values())


def test_allocate_range_exactly_one_block():
    r = ConsumptionRange(start_minute=0, end_minute=15, predicted_kw=4.0)
    result = allocate_to_blocks([r])
    assert result[0] == pytest.approx(1.0)  # 4kW * 0.25h
    assert result[1] == 0.0


def test_allocate_range_shorter_than_one_block():
    r = ConsumptionRange(start_minute=0, end_minute=5, predicted_kw=12.0)
    result = allocate_to_blocks([r])
    assert result[0] == pytest.approx(1.0)  # 12kW * (5/60)h


def test_allocate_range_unaligned_to_block_boundaries():
    r = ConsumptionRange(start_minute=10, end_minute=40, predicted_kw=4.0)
    result = allocate_to_blocks([r])
    assert result[0] == pytest.approx(4.0 * 5 / 60)
    assert result[1] == pytest.approx(4.0 * 15 / 60)
    assert result[2] == pytest.approx(4.0 * 10 / 60)


def test_allocate_overlapping_ranges_are_additive():
    r1 = ConsumptionRange(start_minute=0, end_minute=15, predicted_kw=2.0)
    r2 = ConsumptionRange(start_minute=0, end_minute=15, predicted_kw=3.0)
    result = allocate_to_blocks([r1, r2])
    assert result[0] == pytest.approx(1.25)  # (2+3)kW * 0.25h


def test_allocate_full_day_range():
    r = ConsumptionRange(start_minute=0, end_minute=1440, predicted_kw=4.0)
    result = allocate_to_blocks([r], generate_blocks())
    assert all(v == pytest.approx(1.0) for v in result.values())
