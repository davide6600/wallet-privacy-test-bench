"""
harness/oracle.py
Oracolo semantico di privacy per la riconciliazione tra Ground Truth e Osservazioni di rete.
"""

from __future__ import annotations
import datetime
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class Finding:
    finding_id: str
    rule_code: str
    severity: str
    title: str
    description: str
    evidence: Dict[str, Any]
    reconciled_ground_truth: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "rule_code": self.rule_code,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "evidence": self.evidence,
            "reconciled_ground_truth": self.reconciled_ground_truth,
        }


class SemanticPrivacyOracle:
    def __init__(self, ground_truth_path: Path | str):
        self.ground_truth_path = Path(ground_truth_path)
        with open(self.ground_truth_path, "r", encoding="utf-8") as f:
            self.ground_truth = json.load(f)

        # Mappe di lookup indicizzate
        self.scripthash_to_addr: Dict[str, Dict[str, Any]] = {}
        for addr_info in self.ground_truth.get("addresses", []):
            sh = addr_info["electrum_scripthash"].lower()
            self.scripthash_to_addr[sh] = addr_info

        self.total_canary_scripts = len(self.scripthash_to_addr)

    def evaluate(
        self,
        observed_jsonl_path: Path | str,
        test_run_id: str = "run-001",
        scenario_name: str = "restore-and-sync",
        wallet_name: str = "Electrum",
        wallet_version: str = "4.5.x-cli",
        strict_policy: bool = False,
    ) -> Dict[str, Any]:
        obs_path = Path(observed_jsonl_path)
        events: List[Dict[str, Any]] = []

        if obs_path.exists():
            with open(obs_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

        # Aggregazione per sessione
        sessions: Dict[str, List[Dict[str, Any]]] = {}
        queried_scripthashes: Set[str] = set()
        broadcast_sessions: Set[str] = set()

        for ev in events:
            sess_id = ev.get("session_id", "default")
            sessions.setdefault(sess_id, []).append(ev)

            sh = ev.get("scripthash")
            if sh:
                queried_scripthashes.add(sh.lower())

            method = ev.get("method", "")
            if "broadcast" in method:
                broadcast_sessions.add(sess_id)

        # Calcolo metriche
        observed_canary_count = sum(
            1 for sh in queried_scripthashes if sh in self.scripthash_to_addr
        )
        disclosure_ratio = (
            observed_canary_count / self.total_canary_scripts
            if self.total_canary_scripts > 0
            else 0.0
        )

        max_cluster_size = 0
        session_clusters: Dict[str, List[Dict[str, Any]]] = {}

        for sess_id, s_events in sessions.items():
            session_shs = {
                ev.get("scripthash").lower()
                for ev in s_events
                if ev.get("scripthash") and ev.get("scripthash").lower() in self.scripthash_to_addr
            }
            if len(session_shs) > max_cluster_size:
                max_cluster_size = len(session_shs)
            session_clusters[sess_id] = [self.scripthash_to_addr[s] for s in session_shs]

        findings: List[Finding] = []
        finding_counter = 1

        # REGOLA 1: Cluster Disclosure (Più script nella stessa sessione TCP)
        for sess_id, clustered_addrs in session_clusters.items():
            if len(clustered_addrs) > 1:
                findings.append(
                    Finding(
                        finding_id=f"FIND-{finding_counter:03d}",
                        rule_code="RULE-SCRIPT-CLUSTER",
                        severity="MEDIUM" if not strict_policy else "HIGH",
                        title="Canary Address Clustering via Shared TCP Session",
                        description=(
                            f"The backend observed {len(clustered_addrs)} distinct canary scripts "
                            f"within the same persistent TCP session [{sess_id}], "
                            f"enabling the server to cluster all queried addresses to the same wallet entity."
                        ),
                        evidence={
                            "session_id": sess_id,
                            "cluster_size": len(clustered_addrs),
                            "queried_scripthashes": [a["electrum_scripthash"] for a in clustered_addrs],
                        },
                        reconciled_ground_truth={
                            "derivation_paths": [a["derivation_path"] for a in clustered_addrs],
                            "addresses": [a["address"] for a in clustered_addrs],
                        },
                    )
                )
                finding_counter += 1

        # REGOLA 2: Unused Script Probing (Interrogazione script vergini/oltre gap)
        unused_probed = [
            self.scripthash_to_addr[sh]
            for sh in queried_scripthashes
            if sh in self.scripthash_to_addr and self.scripthash_to_addr[sh].get("expected_status") == "unfunded"
        ]
        if unused_probed:
            findings.append(
                Finding(
                    finding_id=f"FIND-{finding_counter:03d}",
                    rule_code="RULE-UNUSED-SCRIPT-PROBE",
                    severity="LOW",
                    title="Unused Canary Script Probing (Gap Limit Exposure)",
                    description=(
                        f"The wallet queried {len(unused_probed)} canary addresses that never recorded transactions on-chain, "
                        f"exposing its gap-limit lookahead window to the backend indexer."
                    ),
                    evidence={
                        "count_unused_probed": len(unused_probed),
                        "sample_scripthashes": [a["electrum_scripthash"] for a in unused_probed[:5]],
                    },
                    reconciled_ground_truth={
                        "sample_addresses": [a["address"] for a in unused_probed[:5]],
                        "derivation_paths": [a["derivation_path"] for a in unused_probed[:5]],
                    },
                )
            )
            finding_counter += 1

        # REGOLA 3: Broadcast Linkage (Spesa inviata dalla stessa sessione di sync)
        for b_sess in broadcast_sessions:
            if b_sess in session_clusters and len(session_clusters[b_sess]) > 0:
                findings.append(
                    Finding(
                        finding_id=f"FIND-{finding_counter:03d}",
                        rule_code="RULE-BROADCAST-LINKAGE",
                        severity="HIGH",
                        title="Transaction Broadcast Co-located with Address Sync Session",
                        description=(
                            f"The transaction was broadcast over TCP session [{b_sess}], which was also used to query "
                            f"balance and history for {len(session_clusters[b_sess])} canary addresses, "
                            f"linking the payment originator directly to the wallet cluster."
                        ),
                        evidence={
                            "session_id": b_sess,
                            "associated_cluster_size": len(session_clusters[b_sess]),
                        },
                        reconciled_ground_truth={
                            "linked_addresses_sample": [a["address"] for a in session_clusters[b_sess][:5]]
                        },
                    )
                )
                finding_counter += 1

        # Verdetto complessivo
        verdict = "PASS"
        if strict_policy and any(f.severity in ["HIGH", "CRITICAL"] for f in findings):
            verdict = "FAIL"
        elif any(f.severity == "CRITICAL" for f in findings):
            verdict = "FAIL"
        elif findings:
            verdict = "BASELINE_OBSERVATION"

        metrics = {
            "total_canary_scripts": self.total_canary_scripts,
            "observed_canary_scripts": observed_canary_count,
            "script_disclosure_ratio": round(disclosure_ratio, 4),
            "distinct_sessions_count": len(sessions),
            "cluster_size_max": max_cluster_size,
        }

        report = {
            "schema_version": "1.0.0",
            "test_run_id": test_run_id,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "scenario_name": scenario_name,
            "wallet_name": wallet_name,
            "wallet_version": wallet_version,
            "verdict": verdict,
            "metrics": metrics,
            "findings": [f.to_dict() for f in findings],
        }

        return report

    def save_report(self, report: Dict[str, Any], output_path: Path | str) -> None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


if __name__ == "__main__":
    import sys
    gt_file = sys.argv[1] if len(sys.argv) > 1 else "fixtures/canary_wallet.json"
    obs_file = sys.argv[2] if len(sys.argv) > 2 else "fixtures/sample_observed.jsonl"
    out_file = sys.argv[3] if len(sys.argv) > 3 else "artifacts/findings.json"

    oracle = SemanticPrivacyOracle(gt_file)
    rep = oracle.evaluate(obs_file)
    oracle.save_report(rep, out_file)
    print(f"Report oracolo generato: {rep['verdict']} ({len(rep['findings'])} findings) -> {out_file}")
