"""
tests/test_canary.py
Test unitari per la generazione deterministica del canary wallet e dei contratti dati.
"""

import pytest
from harness.canary import (
    compute_electrum_scripthash,
    encode_segwit_address,
    generate_deterministic_canary,
)


def test_bech32_regtest_address_encoding():
    # 20 bytes dummy hash
    dummy_pubkey_hash = bytes.fromhex("751e76e8199196d454941c45d1b3a323f1433bd6")
    addr = encode_segwit_address("bcrt", 0, dummy_pubkey_hash)
    assert addr.startswith("bcrt1q")
    assert len(addr) == 44


def test_scripthash_computation():
    # P2WPKH: 0x00 0x14 + 20 bytes
    script_pubkey = bytes.fromhex("0014751e76e8199196d454941c45d1b3a323f1433bd6")
    scripthash = compute_electrum_scripthash(script_pubkey)
    assert len(scripthash) == 64
    assert scripthash.isalnum()


def test_deterministic_canary_reproducibility():
    canary1 = generate_deterministic_canary("test-canary-1", num_receive=10, num_change=5)
    canary2 = generate_deterministic_canary("test-canary-1", num_receive=10, num_change=5)

    assert len(canary1.addresses) == 15
    assert len(canary2.addresses) == 15

    # Verifica determinismo assoluto
    for a1, a2 in zip(canary1.addresses, canary2.addresses):
        assert a1.address == a2.address
        assert a1.electrum_scripthash == a2.electrum_scripthash
        assert a1.derivation_path == a2.derivation_path
