"""
harness/canary.py
Generatore e gestore del Ground Truth del Wallet Canary deterministico per Bitcoin regtest.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- BIP 173 Bech32 Encoding per Native SegWit ---
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def _bech32_polymod(values: List[int]) -> int:
    generator = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk

def _bech32_hrp_expand(hrp: str) -> List[int]:
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def _bech32_create_checksum(hrp: str, data: List[int]) -> List[int]:
    values = _bech32_hrp_expand(hrp) + data
    polymod = _bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def _convertbits(data: bytes, frombits: int, tobits: int, pad: bool = True) -> Optional[List[int]]:
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret

def encode_segwit_address(hrp: str, witver: int, witprog: bytes) -> str:
    """Codifica un witness program in indirizzo bech32 Native SegWit (es. bcrt1q...)."""
    conv = _convertbits(witprog, 8, 5)
    if conv is None:
        raise ValueError("Errore durante la conversione bit per bech32")
    data = [witver] + conv
    checksum = _bech32_create_checksum(hrp, data)
    return hrp + "1" + "".join([CHARSET[d] for d in data + checksum])

def compute_electrum_scripthash(script_pubkey: bytes) -> str:
    """
    Calcola l'Electrum scripthash:
    SHA256(scriptPubKey) invertito in byte order (little-endian), esadecimale.
    """
    h = hashlib.sha256(script_pubkey).digest()
    return h[::-1].hex()

@dataclass
class CanaryAddress:
    index: int
    change: bool
    derivation_path: str
    address: str
    script_pubkey_hex: str
    electrum_scripthash: str
    expected_status: str = "unfunded"

@dataclass
class KnownUTXO:
    txid: str
    vout: int
    amount_sat: int
    address: str

@dataclass
class CanaryGroundTruth:
    schema_version: str
    canary_id: str
    network: str
    derivation_standard: str
    account_descriptor: str
    gap_limit: int
    addresses: List[CanaryAddress]
    known_utxos: List[KnownUTXO]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "canary_id": self.canary_id,
            "network": self.network,
            "derivation_standard": self.derivation_standard,
            "account_descriptor": self.account_descriptor,
            "gap_limit": self.gap_limit,
            "addresses": [asdict(a) for a in self.addresses],
            "known_utxos": [asdict(u) for u in self.known_utxos],
        }

    def save_json(self, path: Path | str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)


def generate_deterministic_canary(
    canary_id: str = "canary-bip84-regtest-001",
    num_receive: int = 20,
    num_change: int = 10,
    gap_limit: int = 20,
) -> CanaryGroundTruth:
    """
    Genera un set deterministico e ripetibile di indirizzi canary Native Segwit P2WPKH per regtest.
    Utilizza un generatore pseudocasuale con seed fisso per garantire riproducibilità esatta.
    """
    base_seed = b"WALLET_PRIVACY_TEST_BENCH_CANARY_SEED_V1"
    addresses: List[CanaryAddress] = []

    # Genera indirizzi di ricezione (change=0) e cambio (change=1)
    for change_flag, count, change_num in [(False, num_receive, 0), (True, num_change, 1)]:
        for idx in range(count):
            # Derivazione deterministica del pubkey hash (20 bytes)
            path_str = f"m/84'/1'/0'/{change_num}/{idx}"
            h_input = base_seed + f":{change_num}:{idx}".encode("utf-8")
            pubkey_hash = hashlib.sha256(h_input).digest()[:20]

            # P2WPKH scriptPubKey: OP_0 OP_PUSHBYTES_20 <hash160>
            script_pubkey = b"\x00\x14" + pubkey_hash
            address = encode_segwit_address("bcrt", 0, pubkey_hash)
            scripthash = compute_electrum_scripthash(script_pubkey)

            addresses.append(
                CanaryAddress(
                    index=idx,
                    change=change_flag,
                    derivation_path=path_str,
                    address=address,
                    script_pubkey_hex=script_pubkey.hex(),
                    electrum_scripthash=scripthash,
                    expected_status="funded" if (not change_flag and idx < 2) else "unfunded",
                )
            )

    # Definiamo due UTXO note per i primi 2 indirizzi
    known_utxos = [
        KnownUTXO(
            txid="a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0",
            vout=0,
            amount_sat=50_000_000,
            address=addresses[0].address,
        ),
        KnownUTXO(
            txid="f0e1d2c3b4a5968778695a4b3c2d1e0f0987654321fedcba0987654321fedcba",
            vout=1,
            amount_sat=25_000_000,
            address=addresses[1].address,
        ),
    ]

    return CanaryGroundTruth(
        schema_version="1.0.0",
        canary_id=canary_id,
        network="regtest",
        derivation_standard="BIP84",
        account_descriptor="wpkh([deadbeef/84'/1'/0']tpubDC5MmUKJHcW.../*)",
        gap_limit=gap_limit,
        addresses=addresses,
        known_utxos=known_utxos,
    )


if __name__ == "__main__":
    gt = generate_deterministic_canary()
    output_path = Path("fixtures/canary_wallet.json")
    gt.save_json(output_path)
    print(f"Canary Ground Truth generato con successo: {len(gt.addresses)} indirizzi -> {output_path}")
