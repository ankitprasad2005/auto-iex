from types import SimpleNamespace

import pytest
from eth_account import Account
from hexbytes import HexBytes

from app import config
from app.anchoring import publisher as publisher_module
from app.anchoring.publisher import AnchorPublishError, Web3AnchorPublisher, get_publisher

KEY = "0x" + "11" * 32
ADDRESS = Account.from_key(KEY).address


class FakeEth:
    def __init__(self, receipt_status=1, base_fee=30, priority_fee=25, tx_input=None):
        self.receipt_status = receipt_status
        self.base_fee = base_fee
        self.priority_fee = priority_fee
        self.tx_input = tx_input
        self.calls = []
        self.raw = None

    def get_transaction_count(self, address, block_identifier):
        self.calls.append(("nonce", address, block_identifier))
        return 7

    def estimate_gas(self, tx):
        self.calls.append(("estimate", tx))
        return 22_000

    def get_block(self, ident):
        self.calls.append(("block", ident))
        return {"baseFeePerGas": self.base_fee}

    @property
    def max_priority_fee(self):
        return self.priority_fee

    def send_raw_transaction(self, raw):
        self.raw = raw
        return HexBytes("0x" + "cd" * 32)

    def wait_for_transaction_receipt(self, tx_hash, timeout):
        self.calls.append(("receipt", tx_hash, timeout))
        return {"status": self.receipt_status, "blockNumber": 4242}

    def get_transaction(self, tx_hash):
        self.calls.append(("get_tx", tx_hash))
        return {"input": self.tx_input}


def _publisher(eth, **kwargs):
    return Web3AnchorPublisher("http://rpc.invalid", 80002, KEY, web3=SimpleNamespace(eth=eth), **kwargs)


def test_address_is_derived_from_private_key():
    assert _publisher(FakeEth()).address == ADDRESS


def test_publish_sends_signed_zero_value_self_transfer():
    eth = FakeEth()
    tx_hash, block_number = _publisher(eth, receipt_timeout=45).publish(b"payload")

    assert tx_hash == "0x" + "cd" * 32
    assert block_number == 4242
    assert ("nonce", ADDRESS, "pending") in eth.calls
    estimate = next(c[1] for c in eth.calls if c[0] == "estimate")
    assert estimate["from"] == ADDRESS and estimate["to"] == ADDRESS
    assert estimate["value"] == 0 and HexBytes(estimate["data"]) == HexBytes(b"payload")
    assert ("receipt", HexBytes("0x" + "cd" * 32), 45) in eth.calls

    assert Account.recover_transaction(eth.raw) == ADDRESS
    from eth_account.typed_transactions import TypedTransaction

    decoded = TypedTransaction.from_bytes(HexBytes(eth.raw)).as_dict()
    assert decoded["chainId"] == 80002
    assert decoded["nonce"] == 7
    assert decoded["gas"] == 22_000
    assert decoded["value"] == 0
    assert HexBytes(decoded["to"]) == HexBytes(ADDRESS)
    assert HexBytes(decoded["data"]) == HexBytes(b"payload")
    assert decoded["maxPriorityFeePerGas"] == 25
    assert decoded["maxFeePerGas"] == 2 * 30 + 25


def test_publish_handles_missing_base_fee():
    eth = FakeEth(base_fee=None)
    eth.get_block = lambda ident: {}
    _publisher(eth).publish(b"x")
    from eth_account.typed_transactions import TypedTransaction

    decoded = TypedTransaction.from_bytes(HexBytes(eth.raw)).as_dict()
    assert decoded["maxFeePerGas"] == 25


def test_publish_raises_when_receipt_status_is_zero():
    with pytest.raises(AnchorPublishError, match="reverted"):
        _publisher(FakeEth(receipt_status=0)).publish(b"x")


def test_publish_propagates_rpc_errors():
    eth = FakeEth()

    def boom(raw):
        raise ConnectionError("rpc down")

    eth.send_raw_transaction = boom
    with pytest.raises(ConnectionError):
        _publisher(eth).publish(b"x")


def test_fetch_tx_data_returns_input_bytes_from_hexbytes():
    eth = FakeEth(tx_input=HexBytes(b"hello"))
    assert _publisher(eth).fetch_tx_data("0x" + "cd" * 32) == b"hello"
    assert ("get_tx", "0x" + "cd" * 32) in eth.calls


def test_fetch_tx_data_accepts_hex_string_input():
    assert _publisher(FakeEth(tx_input="0x68656c6c6f")).fetch_tx_data("0x01") == b"hello"


def test_builds_real_web3_when_none_injected():
    pub = Web3AnchorPublisher("http://127.0.0.1:1", 80002, KEY)
    assert pub.address == ADDRESS
    assert pub._web3.provider.endpoint_uri == "http://127.0.0.1:1"


def test_invalid_private_key_raises():
    with pytest.raises(ValueError):
        Web3AnchorPublisher("http://rpc.invalid", 80002, "0x1234", web3=SimpleNamespace(eth=FakeEth()))


def test_get_publisher_returns_none_when_key_empty(monkeypatch):
    monkeypatch.setattr(config, "ANCHOR_PRIVATE_KEY", "")
    assert get_publisher() is None


def test_get_publisher_returns_none_when_key_is_whitespace(monkeypatch):
    monkeypatch.setattr(config, "ANCHOR_PRIVATE_KEY", "   ")
    assert get_publisher() is None


def test_get_publisher_builds_from_config(monkeypatch):
    monkeypatch.setattr(config, "ANCHOR_PRIVATE_KEY", KEY)
    monkeypatch.setattr(config, "ANCHOR_RPC_URL", "http://127.0.0.1:2")
    monkeypatch.setattr(config, "ANCHOR_CHAIN_ID", 1234)
    pub = get_publisher()
    assert isinstance(pub, publisher_module.Web3AnchorPublisher)
    assert pub.address == ADDRESS
    assert pub.chain_id == 1234
    assert pub._web3.provider.endpoint_uri == "http://127.0.0.1:2"


def test_default_web3_client_reads_proof_of_authority_blocks(monkeypatch):
    # Polygon is a POA chain: its block extraData is longer than the 32 bytes
    # plain web3.py accepts, so reading the base fee fails without the POA middleware.
    pub = Web3AnchorPublisher("http://127.0.0.1:1", 80002, KEY)
    extra = "0x" + "ab" * 104
    block = {"number": "0x1", "baseFeePerGas": "0x1e", "extraData": extra}
    monkeypatch.setattr(
        pub._web3.provider, "make_request", lambda method, params: {"jsonrpc": "2.0", "id": 1, "result": block}
    )

    latest = pub._web3.eth.get_block("latest")

    assert latest["baseFeePerGas"] == 30
    assert latest["proofOfAuthorityData"] == HexBytes(extra)
