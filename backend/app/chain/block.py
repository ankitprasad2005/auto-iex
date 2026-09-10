from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime

GENESIS_PREV_HASH = "0" * 64


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, default=str)


def compute_hash(index: int, timestamp: datetime, payload: dict, prev_hash: str) -> str:
    raw = f"{index}|{timestamp.isoformat()}|{_canonical_json(payload)}|{prev_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ChainBlock:
    index: int
    timestamp: datetime
    payload: dict
    prev_hash: str
    hash: str

    @staticmethod
    def create(index: int, timestamp: datetime, payload: dict, prev_hash: str) -> "ChainBlock":
        return ChainBlock(
            index=index,
            timestamp=timestamp,
            payload=payload,
            prev_hash=prev_hash,
            hash=compute_hash(index, timestamp, payload, prev_hash),
        )
