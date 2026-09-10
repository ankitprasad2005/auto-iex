from datetime import datetime, timezone

from .block import ChainBlock, GENESIS_PREV_HASH, compute_hash


class Chain:
    def __init__(self, blocks: list[ChainBlock] | None = None):
        self._blocks: list[ChainBlock] = list(blocks) if blocks else []

    @property
    def blocks(self) -> list[ChainBlock]:
        return list(self._blocks)

    def ensure_genesis(self, now: datetime | None = None) -> ChainBlock:
        if self._blocks:
            return self._blocks[0]
        timestamp = now or datetime.now(timezone.utc)
        genesis = ChainBlock.create(
            index=0, timestamp=timestamp, payload={"genesis": True}, prev_hash=GENESIS_PREV_HASH
        )
        self._blocks.append(genesis)
        return genesis

    def append(self, payload: dict, now: datetime | None = None) -> ChainBlock:
        if not self._blocks:
            self.ensure_genesis(now)
        prev = self._blocks[-1]
        timestamp = now or datetime.now(timezone.utc)
        block = ChainBlock.create(index=prev.index + 1, timestamp=timestamp, payload=payload, prev_hash=prev.hash)
        self._blocks.append(block)
        return block

    def verify(self) -> int | None:
        for i, block in enumerate(self._blocks):
            expected_prev_hash = GENESIS_PREV_HASH if i == 0 else self._blocks[i - 1].hash
            if block.prev_hash != expected_prev_hash:
                return block.index
            if compute_hash(block.index, block.timestamp, block.payload, block.prev_hash) != block.hash:
                return block.index
        return None
