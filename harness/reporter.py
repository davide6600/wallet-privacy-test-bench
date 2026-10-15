"""
harness/reporter.py
Generatore di report statici HTML moderni e interattivi per Wallet Privacy Test Bench.
"""

from __future__ import annotations
import html
import json
from pathlib import Path
from typing import Any, Dict


def generate_html_report(findings_data: Dict[str, Any], output_path: Path | str) -> None:
    verdict = findings_data.get("verdict", "UNKNOWN")
    metrics = findings_data.get("metrics", {})
    findings = findings_data.get("findings", [])
    run_id = findings_data.get("test_run_id", "N/A")
    generated_at = findings_data.get("generated_at", "N/A")
    wallet_name = findings_data.get("wallet_name", "N/A")
    wallet_version = findings_data.get("wallet_version", "N/A")
    scenario_name = findings_data.get("scenario_name", "N/A")

    # Colore verdetto
    verdict_color = "#10b981" if verdict == "PASS" else ("#f59e0b" if verdict == "BASELINE_OBSERVATION" else "#ef4444")

    # Righe di findings
    finding_cards_html = []
    for f in findings:
        sev = f.get("severity", "INFO")
        sev_color = {
            "CRITICAL": "#ef4444",
            "HIGH": "#f97316",
            "MEDIUM": "#eab308",
            "LOW": "#3b82f6",
            "INFO": "#6b7280",
        }.get(sev, "#6b7280")

        evidence_str = json.dumps(f.get("evidence", {}), indent=2)
        reconciled_str = json.dumps(f.get("reconciled_ground_truth", {}), indent=2)

        card = f"""
        <div class="finding-card" style="border-left: 4px solid {sev_color};">
            <div class="finding-header">
                <span class="badge" style="background: {sev_color};">{html.escape(sev)}</span>
                <span class="rule-code">{html.escape(f.get('rule_code', ''))}</span>
                <span class="finding-id">{html.escape(f.get('finding_id', ''))}</span>
            </div>
            <h3 class="finding-title">{html.escape(f.get('title', ''))}</h3>
            <p class="finding-desc">{html.escape(f.get('description', ''))}</p>
            
            <div class="code-blocks">
                <details>
                    <summary>Observed Network Evidence</summary>
                    <pre><code>{html.escape(evidence_str)}</code></pre>
                </details>
                <details>
                    <summary>Canary Ground Truth Reconciliation</summary>
                    <pre><code>{html.escape(reconciled_str)}</code></pre>
                </details>
            </div>
        </div>
        """
        finding_cards_html.append(card)

    findings_body = "\n".join(finding_cards_html) if finding_cards_html else "<p>No findings detected.</p>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Finding Report - {html.escape(run_id)}</title>
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --border: #334155;
            --accent: #38bdf8;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        header {{
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .brand {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        h1 {{
            margin: 8px 0 4px 0;
            font-size: 2rem;
        }}
        .meta {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}
        .metric-box {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        .metric-label {{
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .metric-value {{
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 4px;
        }}
        .finding-card {{
            background: var(--surface);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid var(--border);
        }}
        .finding-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
        }}
        .badge {{
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 700;
            color: #ffffff;
        }}
        .rule-code {{
            font-family: monospace;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        .finding-id {{
            margin-left: auto;
            font-family: monospace;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}
        .finding-title {{
            margin: 4px 0 8px 0;
            font-size: 1.2rem;
        }}
        .finding-desc {{
            color: #cbd5e1;
            margin: 0 0 16px 0;
        }}
        .code-blocks details {{
            background: #0f172a;
            border: 1px solid var(--border);
            border-radius: 6px;
            margin-top: 8px;
            padding: 8px 12px;
        }}
        .code-blocks summary {{
            cursor: pointer;
            font-size: 0.85rem;
            color: var(--accent);
            font-weight: 600;
        }}
        pre {{
            margin: 8px 0 0 0;
            overflow-x: auto;
            font-size: 0.8rem;
            color: #e2e8f0;
        }}
        footer {{
            margin-top: 40px;
            border-top: 1px solid var(--border);
            padding-top: 16px;
            color: var(--text-muted);
            font-size: 0.8rem;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">Wallet Privacy Test Bench</div>
            <h1>Executive Privacy Disclosure Report</h1>
            <div class="meta">
                Run ID: <strong>{html.escape(run_id)}</strong> &bull; Scenario: <strong>{html.escape(scenario_name)}</strong> &bull; Wallet: <strong>{html.escape(wallet_name)} ({html.escape(wallet_version)})</strong> &bull; Date: {html.escape(generated_at)}
            </div>
        </header>

        <section class="dashboard">
            <div class="metric-box">
                <div class="metric-label">Executive Verdict</div>
                <div class="metric-value" style="color: {verdict_color};">{html.escape(verdict)}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Script Disclosure</div>
                <div class="metric-value">{metrics.get('script_disclosure_ratio', 0) * 100:.1f}%</div>
                <small style="color: var(--text-muted);">{metrics.get('observed_canary_scripts', 0)} / {metrics.get('total_canary_scripts', 0)} known scripts</small>
            </div>
            <div class="metric-box">
                <div class="metric-label">Max Cluster Size</div>
                <div class="metric-value">{metrics.get('cluster_size_max', 0)}</div>
                <small style="color: var(--text-muted);">addresses per single session</small>
            </div>
            <div class="metric-box">
                <div class="metric-label">Distinct TCP Sessions</div>
                <div class="metric-value">{metrics.get('distinct_sessions_count', 0)}</div>
                <small style="color: var(--text-muted);">communication channels</small>
            </div>
        </section>

        <section class="findings">
            <h2>Reconciled Findings ({len(findings)})</h2>
            {findings_body}
        </section>

        <footer>
            Generated by Wallet Privacy Test Bench &bull; Formal System Traceability and Data Integrity
        </footer>
    </div>
</body>
</html>
"""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    import sys
    inp = sys.argv[1] if len(sys.argv) > 1 else "artifacts/findings.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "artifacts/report.html"

    with open(inp, "r", encoding="utf-8") as f:
        data = json.load(f)
    generate_html_report(data, out)
    print(f"Report HTML generato con successo: {out}")
