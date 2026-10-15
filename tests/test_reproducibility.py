"""
tests/test_reproducibility.py
Test di riproducibilità (3 run pulite) per verificare l'assenza di flakiness o indeterminismo.
"""

import asyncio
from pathlib import Path
import pytest
from harness.runner import run_bench_scenario


@pytest.mark.asyncio
async def test_three_clean_runs_stability(tmp_path):
    """
    Esegue 3 run complete sequenziali in sottodirectory pulite e verifica che:
    1. Lo script disclosure ratio sia identico
    2. Il numero e tipo di findings sia identico
    3. Il verdetto semantico sia identico
    """
    results = []

    for i in range(1, 4):
        run_dir = tmp_path / f"run_{i}"
        # Usa porte diverse per evitare collisioni immediate di socket
        port = 51000 + i

        exit_code = await run_bench_scenario(
            scenario_name=f"reproducibility-test-run-{i}",
            output_dir=str(run_dir),
            proxy_port=port,
            strict_policy=False,
        )
        assert exit_code == 0

        findings_file = run_dir / "findings.json"
        assert findings_file.exists()

        import json
        with open(findings_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        results.append(data)

    # Confronto tra le 3 run
    first = results[0]
    for idx, other in enumerate(results[1:], start=2):
        assert other["verdict"] == first["verdict"], f"Discrepanza verdetto nella run {idx}"
        assert other["metrics"]["script_disclosure_ratio"] == first["metrics"]["script_disclosure_ratio"]
        assert other["metrics"]["cluster_size_max"] == first["metrics"]["cluster_size_max"]
        assert len(other["findings"]) == len(first["findings"])

        rules_first = [f["rule_code"] for f in first["findings"]]
        rules_other = [f["rule_code"] for f in other["findings"]]
        assert rules_first == rules_other, f"Discrepanza regole trovate nella run {idx}"
