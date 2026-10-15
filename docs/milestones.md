# Development Milestones & Verifiable Deliverables

This roadmap establishes the technical milestones, timeline, and verifiable acceptance criteria for **Wallet Privacy Test Bench**.

---

## Roadmap Overview

- **Milestone M0 (Proof of Concept):** Completed. Fully functional headless restore-and-sync runner, canary generator, observer proxy, semantic oracle, and 100% passing tests.
- **Milestones M1–M6:** Planned phased implementation over 8–10 months (~18 hours/week).

---

## Detailed Milestone Breakdown

### Milestone M0: Working Proof of Concept (Completed)
- **Status:** Complete.
- **Deliverables:**
  - Automated runner executing headless restore-and-sync in regtest.
  - Pure-Python canary generator (BIP84 Native SegWit) with little-endian scripthash computation.
  - Asynchronous JSON-RPC observer proxy (`asyncio`) with mock server fallback.
  - Semantic privacy oracle evaluating clustering, gap limit probing, and broadcast linkage.
  - Schema-valid outputs (`ground-truth.json`, `observed.jsonl`, `findings.json`, `run-attestation.json`, `report.html`).
- **Acceptance Criterion:** `pytest` passes 100% on a clean environment with a single command. Verified stability across 3 consecutive clean runs (`test_reproducibility.py`).

---

### Milestone M1: Specification Formalization, Schemas & Multi-Descriptor Fixtures
- **Duration:** 4 weeks
- **Objective:** Extend data specifications to multi-descriptor standards (BIP44, BIP49, BIP84, BIP86 Taproot), formally validate JSON Schemas, and publish standardized test vectors.
- **Deliverables:**
  1. Draft 2020-12 JSON Schemas v1.1.0 with automated conformance test suites.
  2. Multi-descriptor test vectors covering Taproot (BIP86) and Native SegWit (BIP84) with pre-generated regtest transactions.
  3. Formal threat model and metric specification documentation.
- **Acceptance Criterion:** Automated test suite validating 20 positive and negative schema test cases without errors.

---

### Milestone M2: Headless Containerized Testbed & Multi-Protocol Collectors
- **Duration:** 6 weeks
- **Objective:** Consolidate containerized testbed with Bitcoin Core 26+ and electrs v0.10+, supporting dual stream logging of TCP JSON-RPC and socket metadata.
- **Deliverables:**
  1. Headless container environment with rapid block-generation scripts for Linux / WSL2 / GitHub Actions.
  2. Network telemetry collector with optional `pcapng` packet recording.
  3. Fast regtest state-reset mechanism without requiring bitcoind restart.
- **Acceptance Criterion:** Startup, block generation, test run, and clean shutdown on GitHub Actions runners within 60 seconds.

---

### Milestone M3: Electrum Adapter & Declarative Scenario Engine
- **Duration:** 6 weeks
- **Objective:** Complete automated adapter for Electrum CLI covering standard wallet lifecycle operations via declarative YAML scenarios.
- **Deliverables:**
  1. Full Electrum adapter with isolated configuration environments and daemon lifecycle management.
  2. Declarative YAML scenario engine supporting `restore-from-seed`, `initial-sync`, `receive-payment`, `open-tx-detail`, and `prepare-and-broadcast`.
  3. Route isolation assertion scenario verifying Tor / SOCKS5 proxy enforcement.
- **Acceptance Criterion:** 5 distinct scenarios executing headlessly in sequence, generating isolated logs with zero network leakage outside the configured proxy.

---

### Milestone M4: Advanced Semantic Privacy Oracle & Temporal Reconciliation
- **Duration:** 6 weeks
- **Objective:** Enhance the oracle engine with temporal correlation, cross-session linkage detection, and SARIF export for CI reporting.
- **Deliverables:**
  1. Temporal correlation engine linking address lookups with subsequent payment broadcasts.
  2. Cross-session linkage detection identifying shared connection fingerprints or cookie reuse.
  3. SARIF (Static Analysis Results Interchange Format) exporter for native GitHub code-scanning integration.
- **Acceptance Criterion:** Oracle correctly detects 100% of synthetic privacy leaks across 10 benchmark test vectors (zero false negatives).

---

### Milestone M5: CI/CD Regression Engine & Headless CLI
- **Duration:** 4 weeks
- **Objective:** Build a standalone CLI regression engine that diffs privacy findings between two wallet releases and exits with non-zero status upon detected regressions.
- **Deliverables:**
  1. CLI tool: `wallet-privacy-test diff --release-a <hash1> --release-b <hash2>`.
  2. Reusable GitHub Actions and GitLab CI workflow templates.
  3. Declarative policy file format (`.wallet-privacy-ci.yml`) to define acceptable leakage thresholds.
- **Acceptance Criterion:** CI pipeline programmatically fails (exit code 1) when testing a release with injected privacy leakage, and passes (exit code 0) on the clean reference release.

---

### Milestone M6: Packaging, Documentation & Independent Peer Review
- **Duration:** 4 weeks
- **Objective:** Package the tool for PyPI, publish comprehensive developer guides, and conduct independent peer review validation.
- **Deliverables:**
  1. Published PyPI package (`pip install wallet-privacy-test-bench`).
  2. Complete developer documentation, API reference, and adapter authoring guide.
  3. Independent audit and review report from external security researchers.
  4. End-to-end recorded demonstration runnable autonomously.
- **Acceptance Criterion:** Two independent external reviewers successfully reproduce test bench execution autonomously following public documentation.
