# Generative AI Usage Register

In compliance with the **NLnet Generative AI Policy**, this register documents the tools, platforms, scope of assistance, and human verification performed by the applicant (Davide De Carlo) during the technical preparation of this project.

---

## 1. Tools & Underlying Models Used

- **Platform:** Google Antigravity Agentic IDE
- **Underlying Model:** Gemini 3.8 Flash (High reasoning / Thinking agent)
- **Period of Interaction:** October 2026
- **Interaction Repository:** [`ai-disclosure/conversations/`](conversations/)

---

## 2. Allocation of Responsibilities (Human vs. AI)

| Domain | AI Assistance Role | Human Review & Control (Davide De Carlo) |
|---|---|---|
| **Research & State of the Art** | Aggregating open-source specifications (Electrum protocol, BIP157/158, BDK regtest-box, mitmproxy, WalletScrutiny), cataloging technical differences. | Validated accuracy of protocol mechanisms, confirmed research gap, and directed analytical scope. |
| **Data Contracts & Schemas** | Drafting initial JSON Schema definitions (Draft 2020-12) for `ground-truth`, `observed`, `findings`, and `run-attestation`. | Verified hex regex patterns, required property rules, and adherence to formal CSV audit trail principles. |
| **Proof of Concept Code** | Scaffolding Python implementations for Bech32 encoding, JSON-RPC proxying, and the semantic privacy oracle. | Line-by-line code audit; identified and fixed asyncio socket blocking bug; verified deterministic execution. |
| **Testing & CI Infrastructure** | Drafting automated pytest cases and GitHub Actions CI workflow templates. | Executed test suites locally (100% passing across 3-run clean tests); verified zero timing flakiness. |
| **Documentation & Narrative** | Drafting technical documentation structures, threat model taxonomies, and comparison matrices. | Authored, revised, and personally approved all project documentation and grant narratives. |

---

## 3. Strict Verification & Authorship Attestation

1. **Authorship:** All project narratives, problem definitions, architectural decisions, and grant proposal responses were formulated and approved by the applicant.
2. **Execution Auditing:** Every line of code, test case, and schema was executed and validated locally on the applicant's workstation before publication.
3. **Session Audit Trail:** Detailed chronological session transcripts are maintained in [`ai-disclosure/conversations/`](conversations/) for complete transparency.
