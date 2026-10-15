# Protocol Evidence & Technical Reference Register

This register documents primary protocol specifications and literature analyzed to establish the technical foundations of **Wallet Privacy Test Bench**.

---

## 1. Bitcoin Protocol & Wallet Architecture References

1. **Electrum Protocol Specification**
   - **Repository:** `spesmilo/electrum-protocol`
   - **Protocol Model:** Newline-delimited JSON-RPC over TCP/TLS sockets (`blockchain.scripthash.subscribe`, `blockchain.scripthash.get_history`).
   - **Cryptographic Ground Truth:** Scripthashes are computed as the little-endian SHA256 digest of the raw `scriptPubKey`. The server indexes and clusters subscriptions arriving over the same persistent TCP connection.
   - **Impact on Test Bench:** The oracle pre-computes scripthashes for all canary derivation paths to enable real-time query mapping.

2. **BIP 157 / BIP 158: Client Side Block Filtering**
   - **Reference:** Bitcoin Improvement Proposals (BIP 157, BIP 158).
   - **Mechanism:** Compact Golomb-coded block filters allow clients to scan blocks locally and query full blocks from peer nodes only upon matching, eliminating direct address exposure to a single indexer.
   - **Impact on Test Bench:** Provides the reference baseline for future compact-filter wallet adapters.

3. **Bitcoin Dev Kit (BDK) Integration Testing Box**
   - **Repository:** `bitcoindevkit/bitcoin-regtest-box`
   - **Design:** Containerized `bitcoind` and `electrs` for local regression tests.
   - **Impact on Test Bench:** Demonstrates the reliability of containerized `bitcoind + electrs` as standard headless testing infrastructure.

---

## 2. Scientific Literature on Network Privacy & Traffic Analysis

1. **"Mind Your Wallet's Privacy: Identifying Bitcoin Wallet Apps and User's Actions through Network Traffic Analysis" (ACM SAC 2019)**
   - **Authors:** S. Tikhomirov et al.
   - **Core Finding:** Even across encrypted transport channels (TLS), packet sizes, flow timings, and TCP round-trip frequencies allow passive network observers to differentiate between idle states, block synchronization, and payment broadcasts.
   - **Impact on Test Bench:** Justifies the inclusion of passive network metadata observers alongside application-level JSON-RPC loggers.

2. **Open Bitcoin Privacy Project (OBPP) Threat Models (2015–2016)**
   - **Core Analysis:** Categorized key wallet privacy threats: address clustering by indexers, transaction broadcast origin linkage, and temporal association between balance lookups and spends.
   - **Impact on Test Bench:** Provides the conceptual foundation for our oracle's privacy violation taxonomy.
