from datetime import datetime, timezone

import pytest

from app.anchoring.payload import (
    EMPTY_HEAD_HASH,
    PAYLOAD_LENGTH,
    PREFIX,
    chain_head,
    decode_anchor_payload,
    encode_anchor_payload,
)
from app.models.tables import ChainBlockModel

A, B, C = "a" * 64, "b" * 64, "c" * 64


def test_prefix_and_length_constants():
    assert PREFIX == b"AUTOIEX1"
    assert PAYLOAD_LENGTH == 104
    assert EMPTY_HEAD_HASH == "0" * 64


def test_encode_lays_out_prefix_then_three_hashes_in_order():
    data = encode_anchor_payload(A, B, C)
    assert len(data) == 104
    assert data[:8] == b"AUTOIEX1"
    assert data[8:40] == bytes.fromhex(A)
    assert data[40:72] == bytes.fromhex(B)
    assert data[72:] == bytes.fromhex(C)


def test_roundtrip():
    h1 = "0123456789abcdef" * 4
    assert decode_anchor_payload(encode_anchor_payload(h1, B, EMPTY_HEAD_HASH)) == (h1, B, EMPTY_HEAD_HASH)


def test_encode_accepts_uppercase_hex_and_decodes_lowercase():
    assert decode_anchor_payload(encode_anchor_payload("A" * 64, B, C)) == (A, B, C)


@pytest.mark.parametrize(
    "bad",
    ["a" * 63, "a" * 65, "", "g" * 64, "0x" + "a" * 62, " " + "a" * 63, None, 123, b"a" * 64],
)
def test_encode_rejects_non_64_hex(bad):
    with pytest.raises(ValueError):
        encode_anchor_payload(A, bad, C)


def test_decode_rejects_bad_prefix():
    data = b"AUTOIEX2" + encode_anchor_payload(A, B, C)[8:]
    with pytest.raises(ValueError, match="prefix"):
        decode_anchor_payload(data)


@pytest.mark.parametrize("length", [0, 8, 103, 105, 1000])
def test_decode_rejects_wrong_length(length):
    data = (encode_anchor_payload(A, B, C) * 10)[:length]
    with pytest.raises(ValueError, match="length"):
        decode_anchor_payload(data)


def test_decode_accepts_bytearray_and_memoryview():
    data = encode_anchor_payload(A, B, C)
    assert decode_anchor_payload(bytearray(data)) == (A, B, C)
    assert decode_anchor_payload(memoryview(data)) == (A, B, C)


def test_chain_head_of_empty_chain():
    assert chain_head([]) == (-1, EMPTY_HEAD_HASH)


def test_chain_head_is_last_block():
    now = datetime.now(timezone.utc)
    blocks = [
        ChainBlockModel(index=i, timestamp=now, payload_json={}, prev_hash="0" * 64, hash=h)
        for i, h in enumerate([A, B, C])
    ]
    assert chain_head(blocks) == (2, C)
