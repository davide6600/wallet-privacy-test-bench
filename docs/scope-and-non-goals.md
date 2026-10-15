# Scope & Non-Goals

This document establishes operational boundaries for **Wallet Privacy Test Bench** to prevent scope creep and maintain strict focus on verifiable engineering deliverables.

---

## 1. In Scope

- **Target Blockchain:** Bitcoin exclusively.
- **Execution Network:** Strictly and exclusively Bitcoin `regtest` (local regression testing network).
- **Host Runner Environment:** Headless Linux and Docker on WSL2 / GitHub Actions runners.
- **Initial Supported Wallet:** Electrum CLI / Daemon (desktop headless mode).
- **Supported Network Protocols:**
  - Electrum Protocol (newline-delimited JSON-RPC over TCP sockets).
  - Esplora / Blockstream REST API architecture (HTTP/JSON).
- **Core Privacy Metrics:**
  - Script disclosure ratio (observed addresses / total canary derivation paths).
  - Cluster linkage (addresses grouped within the same persistent TCP socket session).
  - Transaction origin linkage (balance queries and transaction broadcasts occurring over the same connection).
- **Standardized Outputs:**
  - Machine-readable, schema-validated JSON findings for CI pipelines.
  - Standalone static HTML reports with complete audit trails.
  - Provenance attestations (`run-attestation.json`) recording SHA256 hashes of tested binaries.

---

## 2. Non-Goals (Explicitly Out of Scope)

- **Real Funds & Mainnet:** No tests are ever executed on mainnet, public testnets, or using private keys with real economic value.
- **Mobile Wallets (Android / iOS):** Excluded from the initial roadmap. Mobile automation requires heavy emulators, WireGuard VPN tunneling, and dynamic instrumentation (Frida) to bypass certificate pinning, deflecting effort from core protocol oracles.
- **Hardware Wallets & Physical Interfaces:** Excluded (no USB, NFC, or secure element emulation).
- **Lightning Network & Layer 2:** Excluded. Lightning features routing, onion gossip, and channel announcement threat models that require distinct analytical frameworks.
- **Altcoins:** No support for networks other than Bitcoin.
- **Adversarial Scanning of Public Nodes:** The test bench only interacts with controlled local laboratory containers; active scanning or attacking of third-party public infrastructure is prohibited.
- **Black-Box Machine Learning Classifiers:** ML-based traffic classification is a non-goal for the core engine. Privacy properties must be asserted via deterministic, auditable logical rules, not probabilistic models prone to false positives.
- **Abstract Universal Scores:** We avoid opaque metrics (e.g., "7/10 privacy rating"). The oracle outputs objective, actionable findings mapped directly to violated rules and protocol evidence.
- **Source-to-Binary Compiler Verification:** The project does not duplicate WalletScrutiny or Guix; it takes verified binary hashes and assesses their runtime network disclosure.
