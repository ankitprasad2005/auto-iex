from datetime import time

import pytest

from app.pricing.blocks import (
    BLOCKS_PER_DAY,
    generate_blocks,
    block_index_for_minute,
    minutes_from_time,
)


def test_generate_blocks_count():
    blocks = generate_blocks()
    assert len(blocks) == BLOCKS_PER_DAY == 96


def test_generate_blocks_first_and_last():
    blocks = generate_blocks()
    assert blocks[0].index == 0
    assert blocks[0].start_minute == 0
    assert blocks[0].end_minute == 15
    assert blocks[-1].index == 95
    assert blocks[-1].start_minute == 1425
    assert blocks[-1].end_minute == 1440


def test_generate_blocks_sequential_no_gaps():
    blocks = generate_blocks()
    for prev, cur in zip(blocks, blocks[1:]):
        assert cur.start_minute == prev.end_minute


@pytest.mark.parametrize(
    "minute,expected_index",
    [(0, 0), (14, 0), (15, 1), (1425, 95), (1439, 95)],
)
def test_block_index_for_minute(minute, expected_index):
    assert block_index_for_minute(minute) == expected_index


@pytest.mark.parametrize("minute", [-1, 1440, 2000])
def test_block_index_for_minute_out_of_range(minute):
    with pytest.raises(ValueError):
        block_index_for_minute(minute)


def test_minutes_from_time():
    assert minutes_from_time(time(0, 0)) == 0
    assert minutes_from_time(time(9, 30)) == 570
    assert minutes_from_time(time(23, 45)) == 1425
