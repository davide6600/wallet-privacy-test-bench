# Human Review & Code Audit Sign-Off

This document formalizes the human code review, validation, and quality verification conducted by **Davide De Carlo** across all components produced during the technical preparation of **Wallet Privacy Test Bench**.

---

## 1. Scope of Review & Verified Modules

### Component 1: JSON Schema Specifications (`schemas/*.json`)
- **Review Conducted:** Verified adherence to JSON Schema Draft 2020-12, verified regex patterns for 32-byte hexadecimal strings (`^[0-9a-f]{64}$`), and ensured strict constraint of required properties.
- **Outcome:** Approved.

### Component 2: Canary Wallet Generator (`harness/canary.py`)
- **Review Conducted:** Audited pure-Python Bech32 polymod constants against BIP173 specification for `regtest` HRP (`bcrt`). Verified that Electrum scripthash calculation correctly implements little-endian byte reversal of the SHA256 digest of `scriptPubKey`.
- **Outcome:** Approved.

### Component 3: Observer Proxy (`harness/observer_proxy.py`)
- **Review Conducted:** Verified transparent TCP socket forwarding, newline-delimited JSON-RPC stream handling, and session ID attribution.
- **Outcome:** Approved with critical modification: Identified a blocking socket call in the client helper during early testing; refactored to native `asyncio.open_connection` reader/writer streams to prevent event loop stalls.

### Component 4: Semantic Privacy Oracle (`harness/oracle.py`)
- **Review Conducted:** Audited clustering algorithm across persistent TCP session IDs, validated detection logic for unfunded canary address probing, and verified broadcast origin linkage checks.
- **Outcome:** Approved.

### Component 5: Test Suite & Reproducibility (`tests/*.py`)
- **Review Conducted:** Executed all 6 automated pytest tests locally on Python 3.13. Verified 100% passing status across 3 clean, independent sequential runs in temporary directories (`test_three_clean_runs_stability`).
- **Outcome:** Approved.

---

## 2. Attestation of Responsibility

I, the undersigned **Davide De Carlo**, hereby certify that I have personally reviewed, tested, and audited all source code, schemas, and technical specifications in this repository, and assume full operational and intellectual responsibility for the deliverables.
