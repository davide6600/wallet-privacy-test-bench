# Wallet Privacy Test Bench

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![Tests](https://github.com/davide6600/wallet-privacy-test-bench/actions/workflows/test.yml/badge.svg)](https://github.com/davide6600/wallet-privacy-test-bench/actions/workflows/test.yml)
[![Determinism](https://img.shields.io/badge/Determinism-100%25%20Verified-brightgreen)](tests/test_reproducibility.py)

> **Reproducible network-privacy regression testing harness for Bitcoin wallets.**

---

## 1. Problem & Technical Gap

Lightweight and desktop Bitcoin wallets regularly communicate with remote backend infrastructure (Electrum servers, Bitcoin Core nodes, Esplora REST instances) to synchronize transaction histories, verify balances, and broadcast transactions.

In doing so, existing tools address only fragments of the security and privacy landscape:
- **Generic Traffic Analyzers (`mitmproxy`, `Wireshark`, `Tweasel`):** Capture raw HTTP/TLS packets and socket flows, but are domain-agnostic. They have no knowledge of Bitcoin descriptors, derivation paths (BIP32/44/84/86), scriptPubKeys, Electrum scripthashes, or gap limits.
- **Functional Testing Frameworks (`BDK`, Bitcoin Core `regtest`):** Verify whether balance calculations and transaction broadcasts succeed, but completely ignore runtime metadata leakage or backend clustering.
- **Reproducible Build Verifiers (`WalletScrutiny`, `F-Droid`, `Guix`):** Certify that published binaries match public source repositories, but do not inspect or evaluate dynamic network behavior at runtime.
- **Historical Evaluations (`Open Bitcoin Privacy Project`):** Established pioneering qualitative threat models in 2015–2016, but left no automated, executable regression harness for modern CI/CD pipelines.

**Wallet Privacy Test Bench** bridges this gap by combining:
1. **Deterministic Canary Ground Truth:** Generating known derivation paths, canary descriptors, and pre-computed scripthashes.
2. **Adversarial Protocol Observers:** Transparently proxying and logging raw JSON-RPC (Electrum) and REST queries with socket session attribution.
3. **Semantic Privacy Oracle:** Reconciling observed network traffic against deterministic ground truth to quantify exact information disclosure.
4. **CI-Ready Regression Engine:** Producing schema-validated JSON findings, machine-readable SARIF data, static HTML reports, and exit codes to halt privacy regressions before release.

---

## 2. System Architecture

```
+--------------------------------------------------------------------------+
|                        TEST BENCH RUNNER (Python CLI)                     |
|                                                                          |
|   1. Setup Lab State         2. Run Scenario       3. Collect & Evaluate |
|   (Docker / Regtest)         (Wallet Adapter)      (Semantic Oracle)     |
+-------------------+------------------+---------------------+-------------+
                    |                  |                     |
                    v                  v                     v
         +--------------------+  +------------+    +-------------------+
         | Docker Environment |  | Electrum   |    | Semantic Privacy  |
         |                    |  | CLI Client |    | Oracle            |
         | +----------------+ |  | (Canary)   |    +---------+---------+
         | | bitcoind       | |  +-----+------+              ^
         | | (regtest node) | |        |                     |
         | +-------+--------+ |        | JSON-RPC            |
         |         |          |        |                     |
         | +-------v--------+ |  +-----v--------------+      |
         | | electrs daemon | |  | Observer Proxy     |      |
         | +-------+--------+ |  | (Port 50001)       |      |
         |         ^          |  |                    |      |
         |         |          |  | - Logs RPC calls   |      |
         |         +----------+  | - Forwards to      |------+
         |                       |   electrs (60401)  | observed.jsonl
         +-----------------------+ - Captures timing  |
                                 +--------------------+
```

---

## 3. Quickstart (One-Command Execution)

### Prerequisites
- Python 3.10+ (tested on 3.10, 3.11, 3.12, and 3.13)
- Docker Desktop (optional: only required when running with full containerized `bitcoind` + `electrs` daemons; mock observer proxy runs standalone without containers)

### Local Execution

```bash
# 1. Clone the repository
git clone https://github.com/davide6600/wallet-privacy-test-bench.git
cd wallet-privacy-test-bench

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Run the automated test suite (100% deterministic, 0 flakiness)
pytest

# 4. Run the end-to-end restore & sync scenario
python -m harness.runner --output artifacts
```

The runner automatically generates verifiable artifacts in `artifacts/`:
- `ground-truth.json`: Canary descriptor, derivation paths, and expected scripthashes.
- `observed.jsonl`: Stream of intercepted JSON-RPC protocol requests with session attribution.
- `findings.json`: Structured privacy findings, violated policy rules, and metrics.
- `report.html`: Modern, navigable static executive report.
- `run-attestation.json`: Cryptographic SHA256 hashes of tested binaries and provenance metadata.

---

## 4. Schemas & Data Contracts

All inputs, intermediary streams, and outputs are strictly validated against JSON Schema specifications (Draft 2020-12):
- [`schemas/ground-truth.schema.json`](schemas/ground-truth.schema.json): Specification for canary wallet descriptors and expected derivation paths.
- [`schemas/observed.schema.json`](schemas/observed.schema.json): Specification for intercepted network protocol events.
- [`schemas/findings.schema.json`](schemas/findings.schema.json): Specification for privacy rule violations, severity, and disclosure metrics.
- [`schemas/run-attestation.schema.json`](schemas/run-attestation.schema.json): Tamper-evident cryptographic attestation of test runs and binary hashes.

---

## 5. Technical Documentation

Comprehensive architectural and protocol documentation is available in the [`docs/`](docs/) directory:
- [System Architecture](docs/architecture.md): Deep-dive into runner modules, async proxy design, and data flows.
- [Threat Model](docs/threat-model.md): Detailed taxonomy of network observers (protocol backend, local network/ISP, auxiliary telemetry) and privacy violation rules.
- [Competitor Matrix & State of the Art](docs/competitor-matrix.md): In-depth comparison with `mitmproxy`, `Tweasel`, `MobSF`, `BDK Regtest Box`, `Electrum Test Suite`, and `WalletScrutiny`.
- [Scope & Non-Goals](docs/scope-and-non-goals.md): Explicit operational boundaries (regtest-only, headless desktop/CLI, non-goals).
- [Technical Feasibility & PoC Validation](docs/feasibility.md): Empirical verification of determinism, asyncio socket decoupling, and canary mapping.
- [Protocol Evidence Register](docs/evidence-register.md): Citations and specifications (Electrum protocol, BIP157/158, BDK regtest).
- [Risk Matrix](docs/risks.md): Technical and operational risk assessment and mitigations.
- [Sustainability & Maintenance](docs/sustainability.md): Long-term governance, zero-cost cloud infrastructure, and community extension guide.
- [Development Milestones](docs/milestones.md): Technical roadmap and verifiable deliverables across M1–M6.

---

## 6. Generative AI Transparency

In accordance with strict open-source governance and grant evaluation standards, this project maintains full transparency regarding the use of generative AI assistance:
- See [`ai-disclosure/`](ai-disclosure/) for our complete AI Disclosure Register, Human Code Review Sign-off, and chronological development session logs.

---

## 7. License & Security

- **License:** Released under the [Apache-2.0 License](LICENSE).
- **Security Policy:** Refer to [SECURITY.md](SECURITY.md) for responsible disclosure via GitHub Private Vulnerability Reporting.
- Copyright (c) 2026 Davide De Carlo.
