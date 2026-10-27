from typing import Any, Protocol

from eth_account import Account
from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from .. import config


class AnchorPublishError(RuntimeError):
    pass


class AnchorPublisher(Protocol):
    @property
    def address(self) -> str: ...

    def publish(self, data: bytes) -> tuple[str, int]: ...

    def fetch_tx_data(self, tx_hash: str) -> bytes: ...


class Web3AnchorPublisher:
    def __init__(
        self, rpc_url: str, chain_id: int, private_key: str, web3: Any = None, receipt_timeout: int = 120
    ):
        self.chain_id = chain_id
        self.receipt_timeout = receipt_timeout
        self._account = Account.from_key(private_key)
        if web3 is None:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self._web3 = web3

    @property
    def address(self) -> str:
        return self._account.address

    def publish(self, data: bytes) -> tuple[str, int]:
        eth = self._web3.eth
        call = {"from": self.address, "to": self.address, "value": 0, "data": HexBytes(data)}
        priority_fee = eth.max_priority_fee
        base_fee = eth.get_block("latest").get("baseFeePerGas") or 0
        tx = {
            "type": 2,
            "chainId": self.chain_id,
            "nonce": eth.get_transaction_count(self.address, "pending"),
            "to": self.address,
            "value": 0,
            "data": call["data"],
            "gas": eth.estimate_gas(call),
            "maxPriorityFeePerGas": priority_fee,
            "maxFeePerGas": 2 * base_fee + priority_fee,
        }
        signed = self._account.sign_transaction(tx)
        tx_hash = eth.send_raw_transaction(signed.raw_transaction)
        receipt = eth.wait_for_transaction_receipt(tx_hash, timeout=self.receipt_timeout)
        tx_hex = Web3.to_hex(tx_hash)
        if receipt["status"] != 1:
            raise AnchorPublishError(f"anchor transaction {tx_hex} reverted")
        return tx_hex, receipt["blockNumber"]

    def fetch_tx_data(self, tx_hash: str) -> bytes:
        return bytes(HexBytes(self._web3.eth.get_transaction(tx_hash)["input"]))


def get_publisher() -> Web3AnchorPublisher | None:
    key = config.ANCHOR_PRIVATE_KEY.strip()
    if not key:
        return None
    return Web3AnchorPublisher(config.ANCHOR_RPC_URL, config.ANCHOR_CHAIN_ID, key)
