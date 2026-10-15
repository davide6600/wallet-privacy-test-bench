# System Architecture: Wallet Privacy Test Bench

This document outlines the software components, data flows, and interactions between modules of the **Wallet Privacy Test Bench**.

---

## 1. Architectural Diagram

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

## 2. Core Modules

### A. Canary Wallet Generator (`harness/canary.py`)
- Deterministically generates a suite of canary keys and descriptors for Bitcoin `regtest` (BIP84 Native SegWit `m/84'/1'/0'`).
- For each derived receive and change address, pre-computes:
  - Derivation path and derivation index.
  - Hexadecimal `scriptPubKey`.
  - **Electrum Scripthash**: SHA256 hash of the `scriptPubKey` reversed to little-endian byte order.
- Outputs the complete ground truth definition to `ground-truth.json`.

### B. Observer Proxy (`harness/observer_proxy.py`)
- An asynchronous TCP proxy (`asyncio`) positioned between the Electrum client (port 50001) and the indexing daemon (`electrs` on port 60401).
- Intercepts newline-delimited (`\n`) JSON-RPC messages, parses methods and parameters (`method`, `params`, `id`), forwards them transparently to the backend, and returns replies without measurable latency.
- Appends each network event to the streaming `observed.jsonl` log enriched with:
  - `session_id`: Unique identifier of the persistent TCP connection.
  - `timestamp_iso`: High-resolution ISO timestamp.
  - Method name and decoded RPC parameters.
- Features a mock server fallback mode to enable lightweight CI test runs without launching full containerized Bitcoin nodes.

### C. Wallet Adapter (`adapters/electrum.py`)
- Controls the client lifecycle headlessly:
  - Initializes an isolated temporary workspace directory.
  - Restores wallet state from canary seed descriptor.
  - Enforces RPC server flags pointing strictly to the local observer proxy.
  - Starts daemon (`daemon start`), monitors synchronization with explicit timeouts, queries balance (`getbalance`), and initiates transaction broadcasts.
  - Gracefully stops daemon (`daemon stop`) and collects runtime metrics.

### D. Semantic Privacy Oracle (`harness/oracle.py`)
- Consumes `ground-truth.json` and `observed.jsonl`.
- Indexes expected canary scripthashes and reconciles them with queries observed during the session:
  - **Script Disclosure Ratio**: Proportion of active, unused, or change scripts revealed to the backend.
  - **Cluster Leakage**: Groups of distinct addresses queried over the same TCP session connection (`session_id`).
  - **Broadcast Linkage**: Whether transaction broadcast occurred across the same persistent session that queried address balances.
- Generates standardized outputs: `findings.json`, `run-attestation.json`, and `report.html`.
