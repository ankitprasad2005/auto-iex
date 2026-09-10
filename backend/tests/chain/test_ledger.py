from dataclasses import replace

from app.chain.block import GENESIS_PREV_HASH
from app.chain.ledger import Chain


def test_verify_on_empty_chain_is_valid():
    chain = Chain()
    assert chain.verify() is None


def test_ensure_genesis_creates_block_with_zero_prev_hash():
    chain = Chain()
    genesis = chain.ensure_genesis()
    assert genesis.index == 0
    assert genesis.prev_hash == GENESIS_PREV_HASH
    assert chain.verify() is None


def test_append_on_empty_chain_creates_genesis_then_block():
    chain = Chain()
    block = chain.append({"market": "DAM"})
    assert len(chain.blocks) == 2
    assert block.index == 1
    assert block.prev_hash == chain.blocks[0].hash
    assert chain.verify() is None


def test_append_multiple_blocks_stays_valid():
    chain = Chain()
    for i in range(5):
        chain.append({"n": i})
    assert len(chain.blocks) == 6  # genesis + 5
    assert chain.verify() is None
    for i, block in enumerate(chain.blocks):
        assert block.index == i


def test_verify_detects_tampered_payload():
    chain = Chain()
    chain.append({"n": 1})
    chain.append({"n": 2})
    tampered = replace(chain.blocks[1], payload={"n": 999})
    blocks = chain.blocks
    blocks[1] = tampered
    tampered_chain = Chain(blocks=blocks)
    assert tampered_chain.verify() == 1


def test_verify_detects_broken_prev_hash_link():
    chain = Chain()
    chain.append({"n": 1})
    chain.append({"n": 2})
    tampered = replace(chain.blocks[2], prev_hash="f" * 64)
    blocks = chain.blocks
    blocks[2] = tampered
    tampered_chain = Chain(blocks=blocks)
    assert tampered_chain.verify() == 2


def test_verify_single_block_chain_is_valid():
    chain = Chain()
    chain.ensure_genesis()
    assert chain.verify() is None
