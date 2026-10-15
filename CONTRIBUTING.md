# Contributing to Wallet Privacy Test Bench

Thank you for your interest in contributing to **Wallet Privacy Test Bench**!

---

## 1. Core Principles

- **Determinism First:** Test vectors, scenarios, and oracles must be 100% deterministic. Ephemeral timings, random ports, and packet latency must never cause test flakiness.
- **Strict Decoupling:** Wallet adapters must remain decoupled from the core Semantic Privacy Oracle and JSON Schema contracts.
- **Evidence-Based Metrics:** We measure empirical, verifiable network disclosures (script exposure ratios, session clustering, co-located broadcasts) rather than subjective privacy scores.

---

## 2. Local Development Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.10, 3.11, 3.12, 3.13)
- Git
- Docker Desktop (optional, required only for running the full `bitcoind` + `electrs` stack)

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/davide6600/wallet-privacy-test-bench.git
cd wallet-privacy-test-bench

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install in editable mode with development dependencies
pip install -e ".[dev]"

# 4. Run the automated test suite
pytest
```

---

## 3. Pull Request Guidelines

1. **Open an Issue First:** For non-trivial changes, open an issue to discuss the proposal, adapter, or rule logic.
2. **Feature Branches:** Use descriptive branch names (e.g., `feature/esplora-rest-observer` or `fix/scripthash-endianness`).
3. **Tests Required:** Every new feature, adapter, or rule must include automated pytest tests and adhere to existing JSON Schemas.
4. **Code Quality:** Ensure all tests pass (`pytest`) and code follows standard Python styling and type hints.
5. **Submit PR:** Submit your pull request against the `main` branch with a clear description of the problem solved.
