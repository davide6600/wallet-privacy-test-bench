# Threat Model: Network Privacy for Bitcoin Wallets

This document formalizes the threat model used by the **Wallet Privacy Test Bench** to evaluate, quantify, and assert network-level privacy properties.

---

## 1. Security & Privacy Objective

The goal of this test bench is to measure the **confidentiality of key relationships, address clusters, and user transaction origins** relative to network actors encountered during normal wallet lifecycle operations (restoration, sync, balance lookup, payment generation, broadcast).

---

## 2. Observer Taxonomy

The test bench models three distinct network observers:

```
+-------------------------------------------------------------+
|              Bitcoin Wallet Under Test (Canary)             |
+-------------------------------------------------------------+
        |                               |                |
        | JSON-RPC / REST               | TCP/IP Flow    | Telemetry
        v                               v                v
+--------------------------+  +--------------------+  +--------------------+
| Observer 1:              |  | Observer 2:        |  | Observer 3:        |
| Protocol Backend Server  |  | Local Network / ISP|  | Auxiliary Services |
| (Electrum / Esplora)     |  | (Passive Sniffer)  |  | (Price / Versions) |
+--------------------------+  +--------------------+  +--------------------+
```

### Observer 1: Protocol Backend Server (Honest-but-Curious)
- **Definition:** The server contacted by the wallet to retrieve blockchain state (e.g., an ElectrumX server or Esplora node).
- **Capabilities:**
  - Logs all incoming JSON-RPC calls and arguments (`blockchain.scripthash.subscribe`, `blockchain.scripthash.get_history`, `blockchain.transaction.broadcast`).
  - Correlates all requests arriving over the same persistent TCP socket connection.
  - Records precise timestamps of balance lookups and payment broadcasts.
- **Oracle Assertion Question:**
  *Can the backend cluster the wallet's canary addresses together? Does it observe unused addresses beyond the gap limit?*

### Observer 2: Local Network / ISP Observer (Passive Sniffer)
- **Definition:** An on-path network observer on local Wi-Fi, malicious router, or upstream ISP.
- **Capabilities:**
  - Inspects destination IP addresses, ports, unencrypted DNS queries, and TLS SNI headers.
  - Performs traffic flow analysis (packet sizes, directionality, burst intervals).
- **Oracle Assertion Question:**
  *Can a passive observer infer synchronization activity or distinguish broadcast events from balance lookups despite transport encryption?*

### Observer 3: Auxiliary Services & External Telemetry
- **Definition:** Third-party servers contacted for ancillary features (fiat exchange rates, software update checks, mempool fee estimation).
- **Capabilities:**
  - Receives HTTP headers (User-Agent, language, operating system identifiers).
- **Oracle Assertion Question:**
  *Does the wallet leak persistent metadata or identifiers that could link its network activity to external identities?*

---

## 3. Privacy Policy Rules Evaluated by Oracle

The Semantic Privacy Oracle processes observed events and maps them to **standardized findings**:

| Rule Code | Description | Default Severity |
|---|---|---|
| `RULE-SCRIPT-CLUSTER` | Querying multiple distinct canary scripts over the same persistent TCP session. | Baseline / High |
| `RULE-UNUSED-SCRIPT-PROBE` | Querying unfunded canary addresses beyond the expected gap limit. | Medium |
| `RULE-BROADCAST-LINKAGE` | Broadcasting a transaction over the same connection/session used to query address balances. | High |
| `RULE-UNEXPECTED-DESTINATION` | Contacting network hosts or IP addresses not declared in the test scenario. | Critical |
| `RULE-CROSS-SESSION-REUSE` | Reusing connection identifiers, tokens, or cookies across distinct wallet sessions. | High |
