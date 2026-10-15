"""
harness/runner.py
Entrypoint CLI unificato per l'esecuzione del banco di prova Wallet Privacy Test Bench.
"""

from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import logging
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from adapters.electrum import ElectrumAdapter
from harness.canary import CanaryGroundTruth, generate_deterministic_canary
from harness.observer_proxy import ElectrumObserverProxy
from harness.oracle import SemanticPrivacyOracle
from harness.reporter import generate_html_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TestBenchRunner")


def get_git_commit(repo_dir: Path) -> tuple[str, bool]:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        commit = res.stdout.strip()
        status_res = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        )
        is_clean = len(status_res.stdout.strip()) == 0
        return commit, is_clean
    except Exception:
        return "unknown-commit", False


def file_sha256(path: Path) -> str:
    if not path.exists():
        return "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


async def run_bench_scenario(
    scenario_name: str = "restore-and-sync",
    output_dir: str = "artifacts",
    proxy_port: int = 50001,
    strict_policy: bool = False,
) -> int:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    run_id = f"run-{uuid.uuid4().hex[:8]}"
    logger.info(f"=== Avvio Test Bench [{run_id}] - Scenario: {scenario_name} ===")

    # 1. Preparazione Ground Truth
    gt_path = out_path / "ground-truth.json"
    gt = generate_deterministic_canary()
    gt.save_json(gt_path)
    logger.info(f"[1/4] Ground Truth canary generato: {len(gt.addresses)} indirizzi -> {gt_path}")

    # 2. Avvio Observer Proxy locale per il test
    log_file = out_path / "observed.jsonl"
    if log_file.exists():
        log_file.unlink()

    proxy = ElectrumObserverProxy(
        listen_host="127.0.0.1",
        listen_port=proxy_port,
        backend_host="127.0.0.1",
        backend_port=60401,
        log_file=str(log_file),
    )
    await proxy.start()
    logger.info(f"[2/4] Observer Proxy attivo su 127.0.0.1:{proxy_port}")

    # 3. Esecuzione scenario tramite Adapter
    adapter = ElectrumAdapter(proxy_host="127.0.0.1", proxy_port=proxy_port)
    scripthashes_to_probe = [a.electrum_scripthash for a in gt.addresses[:20]]

    logger.info("[3/4] Esecuzione scenario client in corso...")
    # Esegue la sessione di protocollo simulata o reale in modo asincrono
    await adapter.execute_protocol_client_session_async(
        canary_scripthashes=scripthashes_to_probe,
        do_broadcast=True,
    )
    # Breve pausa per flush
    await asyncio.sleep(0.5)
    await proxy.stop()

    # 4. Esecuzione Oracolo di Privacy
    logger.info("[4/4] Valutazione semantica con Privacy Oracle...")
    oracle = SemanticPrivacyOracle(gt_path)
    findings_report = oracle.evaluate(
        observed_jsonl_path=log_file,
        test_run_id=run_id,
        scenario_name=scenario_name,
        wallet_name="Electrum (Regtest Headless)",
        wallet_version="4.5.x-cli",
        strict_policy=strict_policy,
    )

    findings_path = out_path / "findings.json"
    oracle.save_report(findings_report, findings_path)

    # 5. Generazione Report HTML
    html_path = out_path / "report.html"
    generate_html_report(findings_report, html_path)

    # 6. Attestazione di esecuzione (Provenance Attestation)
    repo_root = Path(__file__).resolve().parent.parent
    commit, is_clean = get_git_commit(repo_root)

    attestation = {
        "schema_version": "1.0.0",
        "test_run_id": run_id,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "harness_git_commit": commit,
        "harness_clean_worktree": is_clean,
        "tested_artifact": {
            "name": "Electrum-Protocol-Client",
            "version": "4.5.x",
            "binary_path": "adapters/electrum.py",
            "binary_sha256": file_sha256(Path(__file__).parent.parent / "adapters" / "electrum.py"),
            "source_repository": "https://github.com/spesmilo/electrum",
        },
        "environment": {
            "os": platform.platform(),
            "python_version": sys.version.split()[0],
            "docker_version": "Docker Desktop WSL2 available",
        },
        "output_hashes": {
            "ground_truth_sha256": file_sha256(gt_path),
            "observed_events_sha256": file_sha256(log_file),
            "findings_sha256": file_sha256(findings_path),
        },
    }

    attestation_path = out_path / "run-attestation.json"
    with open(attestation_path, "w", encoding="utf-8") as f:
        json.dump(attestation, f, indent=2)

    logger.info("=== Test Bench completato con successo ===")
    logger.info(f"Verdetto: {findings_report['verdict']}")
    logger.info(f"Script Disclosure Ratio: {findings_report['metrics']['script_disclosure_ratio'] * 100:.1f}%")
    logger.info(f"Finding rilevati: {len(findings_report['findings'])}")
    logger.info(f"Report HTML: {html_path.resolve()}")
    logger.info(f"Attestation: {attestation_path.resolve()}")

    if findings_report["verdict"] == "FAIL":
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="Wallet Privacy Test Bench Runner")
    parser.add_argument("--scenario", default="restore-and-sync", help="Nome dello scenario da eseguire")
    parser.add_argument("--output", default="artifacts", help="Cartella per i report di output")
    parser.add_argument("--proxy-port", type=int, default=50002, help="Porta per l'Observer Proxy temporaneo")
    parser.add_argument("--strict", action="store_true", help="Se attivato, fallisce su qualsiasi finding MEDIUM o superiore")

    args = parser.parse_args()

    exit_code = asyncio.run(
        run_bench_scenario(
            scenario_name=args.scenario,
            output_dir=args.output,
            proxy_port=args.proxy_port,
            strict_policy=args.strict,
        )
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
