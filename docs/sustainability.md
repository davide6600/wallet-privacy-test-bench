# Long-Term Sustainability & Maintenance

This document outlines the governance, extensibility, and maintenance model for **Wallet Privacy Test Bench** beyond initial development milestones.

---

## 1. Modular Architecture for Community Contributions

The decoupled architecture minimizes the friction required to add support for new wallets or indexing protocols:
- **Stable Core Oracle:** The evaluation engine and findings schemas are completely decoupled from individual client implementation details.
- **Standardized Adapter Interface:** Supporting a new wallet (e.g., Sparrow, BDK CLI, headless Bitcoin Core) requires implementing a single Python adapter class conforming to the base lifecycle interface (`init`, `restore`, `sync`, `broadcast`).
- **Drop-in CI Templates:** Ready-to-use GitHub Actions and GitLab CI workflows allow wallet maintainers to integrate regression gates with fewer than ten lines of CI configuration.

---

## 2. Maintenance Model & Governance

- **Permissive Open Source Licensing:** Released under **Apache-2.0**, enabling frictionless integration by open-source wallets, commercial auditing firms, and academic security researchers.
- **Zero-Cost Infrastructure Footprint:** The harness runs locally and on standard free CI runners (such as GitHub Actions). Having no proprietary cloud databases, central servers, or recurring SaaS subscriptions guarantees that structural hosting costs remain at zero.
- **Future Roadmap:** Following core desktop/CLI consolidation, future development may extend adapters to compact block filter protocols (BIP 157/158) and CoinJoin / collaborative transaction protocols.
