"""
tests/test_oracle.py
Test per l'Oracolo di Privacy Semantica e la classificazione delle violazioni.
"""

import json
from pathlib import Path
import pytest
from harness.canary import generate_deterministic_canary
from harness.oracle import SemanticPrivacyOracle


@pytest.fixture
def canary_env(tmp_path):
    gt = generate_deterministic_canary("test-canary-fixture", num_receive=10, num_change=5)
    gt_file = tmp_path / "ground_truth.json"
    gt.save_json(gt_file)
    return gt, gt_file


def test_oracle_empty_observations(canary_env, tmp_path):
    gt, gt_file = canary_env
    empty_log = tmp_path / "empty_obs.jsonl"
    empty_log.write_text("")

    oracle = SemanticPrivacyOracle(gt_file)
    rep = oracle.evaluate(empty_log)

    assert rep["verdict"] == "PASS"
    assert rep["metrics"]["observed_canary_scripts"] == 0
    assert rep["metrics"]["script_disclosure_ratio"] == 0.0
    assert len(rep["findings"]) == 0


def test_oracle_detects_cluster_and_broadcast_linkage(canary_env, tmp_path):
    gt, gt_file = canary_env
    obs_log = tmp_path / "observed.jsonl"

    events = []
    # Interroga i primi 5 indirizzi nella sessione sess-01
    for a in gt.addresses[:5]:
        events.append({
            "timestamp_iso": "2026-10-05T12:00:00Z",
            "observer_id": "observer-test",
            "protocol": "electrum-jsonrpc",
            "session_id": "sess-01",
            "method": "blockchain.scripthash.subscribe",
            "params": [a.electrum_scripthash],
            "scripthash": a.electrum_scripthash,
        })

    # Broadcast nella stessa sessione
    events.append({
        "timestamp_iso": "2026-10-05T12:00:05Z",
        "observer_id": "observer-test",
        "protocol": "electrum-jsonrpc",
        "session_id": "sess-01",
        "method": "blockchain.transaction.broadcast",
        "params": ["rawtxhex"],
        "scripthash": None,
    })

    with open(obs_log, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    oracle = SemanticPrivacyOracle(gt_file)
    rep = oracle.evaluate(obs_log)

    assert rep["metrics"]["observed_canary_scripts"] == 5
    assert rep["metrics"]["script_disclosure_ratio"] == round(5 / 15, 4)
    assert rep["metrics"]["cluster_size_max"] == 5

    rule_codes = [f["rule_code"] for f in rep["findings"]]
    assert "RULE-SCRIPT-CLUSTER" in rule_codes
    assert "RULE-BROADCAST-LINKAGE" in rule_codes
