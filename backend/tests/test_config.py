import importlib

from app import config


def test_anchor_defaults(monkeypatch):
    for name in ("ANCHOR_RPC_URL", "ANCHOR_CHAIN_ID", "ANCHOR_PRIVATE_KEY", "ANCHOR_EXPLORER_TX_URL"):
        monkeypatch.delenv(name, raising=False)
    reloaded = importlib.reload(config)
    try:
        assert reloaded.ANCHOR_RPC_URL == "https://polygon-amoy-bor-rpc.publicnode.com"
        assert reloaded.ANCHOR_CHAIN_ID == 80002
        assert reloaded.ANCHOR_PRIVATE_KEY == ""
        assert reloaded.ANCHOR_EXPLORER_TX_URL == "https://amoy.polygonscan.com/tx/"
    finally:
        monkeypatch.undo()
        importlib.reload(config)


def test_anchor_env_overrides(monkeypatch):
    monkeypatch.setenv("ANCHOR_RPC_URL", "http://rpc.example")
    monkeypatch.setenv("ANCHOR_CHAIN_ID", "31337")
    monkeypatch.setenv("ANCHOR_PRIVATE_KEY", "0xkey")
    monkeypatch.setenv("ANCHOR_EXPLORER_TX_URL", "http://explorer/tx/")
    reloaded = importlib.reload(config)
    try:
        assert reloaded.ANCHOR_RPC_URL == "http://rpc.example"
        assert reloaded.ANCHOR_CHAIN_ID == 31337
        assert reloaded.ANCHOR_PRIVATE_KEY == "0xkey"
        assert reloaded.ANCHOR_EXPLORER_TX_URL == "http://explorer/tx/"
    finally:
        monkeypatch.undo()
        importlib.reload(config)
