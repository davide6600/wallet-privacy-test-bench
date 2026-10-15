# Security Policy

## 1. Scope & Isolation Guarantees

**Wallet Privacy Test Bench** is strictly designed and intended for automated testing in isolated, controlled environments using Bitcoin `regtest` (local regression testing network).

- **No Real Funds or Keys:** Never use real mainnet seeds, extended private keys (`xprv`), or private keys holding economic value in tests or fixtures.
- **Strict Local Isolation:** Test components bind exclusively to loopback (`127.0.0.1`) or isolated container networks. No RPC service or proxy port should ever be exposed on public network interfaces.
- **Headless & Sandboxed:** Test scenarios run against local mock servers or dedicated regtest nodes (`bitcoind` + `electrs`).

---

## 2. Reporting a Vulnerability

We take the security of this testing harness and its data models seriously. If you discover a security vulnerability or potential data leak:

1. Please do **NOT** open a public issue.
2. Submit a confidential report using GitHub's built-in **[Private Vulnerability Reporting](https://github.com/davide6600/wallet-privacy-test-bench/security/advisories/new)** under the Security tab of this repository.
3. Provide a clear description of the vulnerability, steps to reproduce, and any suggested remediation.

All private security advisories are reviewed promptly, and an initial response will be provided within 48–72 hours.
