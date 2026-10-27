class FakePublisher:
    def __init__(self, error: Exception | None = None):
        self.error = error
        self.sent: list[bytes] = []
        self.on_chain: dict[str, bytes] = {}

    @property
    def address(self) -> str:
        return "0x" + "ab" * 20

    def publish(self, data: bytes) -> tuple[str, int]:
        if self.error is not None:
            raise self.error
        self.sent.append(data)
        tx_hash = f"0x{len(self.sent):064x}"
        self.on_chain[tx_hash] = data
        return tx_hash, 1000 + len(self.sent)

    def fetch_tx_data(self, tx_hash: str) -> bytes:
        return self.on_chain[tx_hash]
