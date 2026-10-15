# Risk Matrix & Mitigation Strategies

This document analyzes technical and operational risks associated with the development and deployment of **Wallet Privacy Test Bench**, establishing preventive mitigations.

---

## 1. Technical Risks

| Risk | Probability | Impact | Mitigation Strategy |
|---|---|---|---|
| **Upstream protocol shifts (e.g., Electrum updates RPC formatting)** | Medium | Medium | The oracle and proxy decouple transport parsing from evaluation rules via JSON Schemas. Protocol updates require modifying only the wallet adapter, leaving the evaluation oracle intact. |
| **Network test flakiness & asynchronous socket timeouts** | Medium | High | All timeouts are explicit and configurable. Timing jitter and ephemeral port numbers are excluded from semantic equivalence assertions. The M0 PoC demonstrated 100% stability across multiple clean runs. |
| **Fragility of Desktop GUI Automation** | High | High | **Strict Architectural Rule:** The harness targets only CLI, headless, and RPC interfaces. Fragile graphical automation (e.g., Selenium/PyAutoGUI) is excluded from the core. |
| **Inadvertent leakage to public Bitcoin networks** | Low | Critical | Test adapters strictly enforce `--regtest`, `--oneserver`, and bind all listening and proxy ports strictly to `127.0.0.1` or isolated container bridge networks. |

---

## 2. Operational & Project Risks

| Risk | Probability | Impact | Mitigation Strategy |
|---|---|---|---|
| **Upstream maintainer indifference or adoption lag** | Medium | Low | The test harness operates completely standalone: researchers, auditors, and users can test public wallet releases independently of upstream integration. |
| **Availability of independent peer reviewers** | Medium | Medium | A dedicated external review pool is budgeted in Milestone M6 to compensate independent security researchers for formal test audits and issue verification. |
| **Scope Creep** | Low | Medium | Strict operational scope enforced by `docs/scope-and-non-goals.md` (no mobile emulators, no Lightning, no altcoins). |
