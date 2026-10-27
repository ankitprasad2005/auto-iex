import re
from typing import Protocol, Sequence

PREFIX = b"AUTOIEX1"
HASH_BYTES = 32
PAYLOAD_LENGTH = len(PREFIX) + 3 * HASH_BYTES
EMPTY_HEAD_INDEX = -1
EMPTY_HEAD_HASH = "0" * 64

_HEX64 = re.compile(r"[0-9a-fA-F]{64}")


class _HashedBlock(Protocol):
    index: int
    hash: str


def _hash_bytes(value: str) -> bytes:
    if not isinstance(value, str) or not _HEX64.fullmatch(value):
        raise ValueError(f"head hash must be 64 hex characters, got {value!r}")
    return bytes.fromhex(value)


def encode_anchor_payload(scrape_hash: str, settlement_hash: str, price_hash: str) -> bytes:
    return PREFIX + b"".join(_hash_bytes(h) for h in (scrape_hash, settlement_hash, price_hash))


def decode_anchor_payload(data: bytes) -> tuple[str, str, str]:
    data = bytes(data)
    if len(data) != PAYLOAD_LENGTH:
        raise ValueError(f"anchor payload length must be {PAYLOAD_LENGTH} bytes, got {len(data)}")
    if not data.startswith(PREFIX):
        raise ValueError("anchor payload has an unexpected prefix")
    body = data[len(PREFIX):]
    scrape, settlement, price = (body[i:i + HASH_BYTES].hex() for i in range(0, 3 * HASH_BYTES, HASH_BYTES))
    return scrape, settlement, price


def chain_head(blocks: Sequence[_HashedBlock]) -> tuple[int, str]:
    if not blocks:
        return EMPTY_HEAD_INDEX, EMPTY_HEAD_HASH
    return blocks[-1].index, blocks[-1].hash
