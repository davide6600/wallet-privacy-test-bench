# Competitor Matrix & State-of-the-Art Analysis

This document catalogs adjacent tools and methodologies, detailing demonstrated capabilities, verified limitations relative to **Wallet Privacy Test Bench**, and our architectural differentiation.

---

## 1. Network Analyzers & General Traffic Interceptors

| Tool | License | Demonstrated Capabilities | Overlap with Project | Verified Limitations | Integration Assessment |
|---|---|---|---|---|---|
| **mitmproxy** ([repo](https://github.com/mitmproxy/mitmproxy)) | MIT | HTTP(S) and WebSocket interception, scripting, and TLS termination. | Intercepts HTTP/REST traffic for Esplora adapters. | Lacks Bitcoin domain knowledge: cannot parse descriptors, scripthashes, or derivation paths. No native support for raw TCP newline-delimited JSON-RPC (Electrum). | Useful auxiliary interceptor for REST endpoints; insufficient as a standalone Bitcoin test bench. |
| **Tweasel** ([docs](https://docs.tweasel.org/)) | MIT | Mobile automation (Android/iOS) and GDPR tracking detection. | Concept of automated network disclosure testing. | Exclusively targets mobile web/HTTP analytics. HAR exports cannot parse Bitcoin P2P or raw Electrum protocols. | Mobile emulator stack is excessively heavy for headless desktop/CLI CI pipelines. |
| **MobSF** ([repo](https://github.com/MobSF/Mobile-Security-Framework-MobSF)) | GPL-3.0 | Static and dynamic mobile security scanning (OWASP, CWE). | Identifies endpoints contacted by applications. | Generic mobile security analyzer; no semantic blockchain oracle or reconciliation against cryptographic ground truth. | Orthogonal focus (general vulnerability scanning for mobile binaries). |
| **Wireshark / tcpdump** | GPL-2.0 / BSD | Low-level packet capture and `pcapng` export. | Universal capture format for network evidence. | Low-level raw packet data; requires specialized dissectors and cannot reconcile queries with canary descriptors. | Retained as secondary cryptographic evidence, not as the primary evaluation oracle. |

---

## 2. Bitcoin Testbeds & Regression Suites

| Tool / Practice | License | Demonstrated Capabilities | Overlap with Project | Verified Limitations | Integration Assessment |
|---|---|---|---|---|---|
| **BDK Regtest Box** ([repo](https://github.com/bitcoindevkit/bitcoin-regtest-box)) | Apache-2.0 / MIT | Dockerized `bitcoind` + `electrs` containers for integration testing. | Deterministic regtest testbed. | Verifies only functional correctness (sync, balance, transaction creation); measures zero information leakage. | **Adopted as architectural foundation** for the containerized regtest testbed. |
| **Electrum Test Suite** ([repo](https://github.com/spesmilo/electrum)) | MIT | Unit and integration test suite running in `regtest`. | Functional test harness for Electrum. | Tests verify that the client functions correctly; they do not measure what an adversarial backend learns or clusters. | Test bench findings can be upstreamed as regression checks for Electrum CI. |
| **Electrum Personal Server** ([repo](https://github.com/chris-belcher/electrum-personal-server)) | MIT | Single-user Electrum backend connected to a local full node. | Mitigates privacy leakage to third-party servers. | Mitigation architecture for end users, not a comparative testing harness for wallet releases. | Useful baseline for a "trusted local node" test scenario. |
| **OBPP Wallet Ratings** ([repo](https://github.com/OpenBitcoinPrivacyProject/wallet-ratings)) | CC-BY-SA | Qualitative privacy rating framework for Bitcoin wallets (2015–2016). | Threat model concepts and leakage taxonomy. | Primarily manual evaluation spreadsheets; produced no automated software or CI regression harness. | OBPP taxonomy serves as theoretical foundation for our oracle's policy definitions. |

---

## 3. Binary & Release Verifiers

| Tool | License | Demonstrated Capabilities | Overlap with Project | Verified Limitations | Integration with Wallet Privacy Test Bench |
|---|---|---|---|---|---|
| **WalletScrutiny** ([site](https://walletscrutiny.com/)) | GPL-3.0 | Reproducible build verification for wallet binaries (APK, desktop) from public sources. | Identifies and tracks verified binary releases. | Limited to source-to-binary equivalence. Does not evaluate dynamic runtime network behavior of verified binaries. | **Complementary:** We ingest verified release hashes (SHA256) and assert runtime network privacy against that exact binary identity. |
| **F-Droid Verification Server** | AGPL-3.0 | Automated rebuilds and diffoscope comparison for Android packages. | Binary provenance attestations. | Focused strictly on Android compilation reproducibility. | Conceptual model for our cryptographic `run-attestation.json`. |
| **Bitcoin Core Guix** | MIT | Deterministic, multi-platform builds with cryptographic signatures. | Maximum binary integrity guarantee. | Dedicated to Bitcoin Core build verification; not a dynamic privacy test harness. | Gold standard reference for verifiable binary provenance. |

---

## 4. Competitive Differentiation

No existing tool answers this fundamental question:
> *"Given binary release $X$ of a Bitcoin wallet, and given a deterministic canary descriptor with 30 derivation paths, what exact percentage of wallet addresses and transaction linkages are revealed to each network participant during a standard restore and synchronization cycle?"*

**Wallet Privacy Test Bench** addresses this gap by unifying **deterministic ground truth**, **adversarial protocol observers**, and an **executable semantic oracle**.
