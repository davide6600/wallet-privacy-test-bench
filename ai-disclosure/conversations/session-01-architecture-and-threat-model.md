# AI Interaction Session 01: Architecture & Threat Model

- **Date:** October 2026
- **Tool / Platform:** Google Antigravity Agentic IDE
- **Underlying Model:** Gemini 3.8 Flash (High reasoning / Thinking agent)
- **User / Reviewer:** Davide De Carlo

---

### User Prompt
> I want to design an automated test harness to measure network privacy leakage in Bitcoin lightweight wallets (specifically starting with Electrum in regtest). Existing tools like mitmproxy or Wireshark capture generic network packets, but they don't understand Bitcoin descriptors or gap limits. BDK and Bitcoin Core test functional correctness, not privacy. I need:
> 1. A clear threat model distinguishing what an honest-but-curious backend learns versus what the wallet actually owns.
> 2. An architectural breakdown separating the test runner, the observer proxy, and the evaluation oracle.
> Keep the design modular, headless, and suitable for CI pipelines.

### Assistant Response Summary
- Proposed a 3-layer architecture:
  1. **Deterministic Ground Truth Generator:** Defines canary BIP84 derivation paths and pre-computes Electrum scripthashes.
  2. **Adversarial Observer Proxy:** Asynchronous TCP proxy listening on port 50001, intercepting newline-delimited JSON-RPC messages and forwarding to `electrs` on port 60401 while appending session-attributed events to `observed.jsonl`.
  3. **Semantic Privacy Oracle:** Reconciles observed queries against the known canary catalog to detect address clustering, gap probing, and broadcast co-location.
- Formalized three network observers:
  - Observer 1: Protocol backend indexer (sees scripthash subscriptions and transaction broadcasts).
  - Observer 2: Local on-path network/ISP observer (sees flow sizes, timing, and unencrypted SNI/DNS).
  - Observer 3: Auxiliary telemetry endpoints (fiat exchange rates, software updates).

### Human Review & Direction (Davide De Carlo)
- **Approved with modifications:**
  - Instructed the AI to strictly avoid machine-learning classifiers or universal privacy scores: findings must be based on explicit, rule-based policies.
  - Mandated that mobile wallets (Android/iOS) and Lightning Network be explicitly declared as non-goals for Milestone M0/M1 to avoid scope creep.
  - Specified Apache-2.0 as the open-source license.
