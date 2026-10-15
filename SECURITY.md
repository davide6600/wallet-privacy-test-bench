# Security Policy

## 1. Scope & Isolation Guarantees

**Wallet Privacy Test Bench** is strictly designed and intended for automated testing in isolated, controlled environments using Bitcoin `regtest` (local regression testing network).

- **No Real Funds or Keys:** Never use real mainnet seeds, extended private keys (`xprv`), or private keys holding economic value in tests or fixtures.
- **Strict Local Isolation:** Test components bind exclusively to loopback (`127.0.0.1`) or isolated container networks. No RPC service or proxy port should ever be exposed on public network interfaces.
- **Headless & Sandboxed:** Test scenarios run against local mock servers or dedicated regtest nodes (`bitcoind` + `electrs`).

---

## 2. Reporting a Vulnerability

We take the security of this testing harness and its data models seriously. If you discover a security vulnerability or potential data leak in the harness:

### Preferred Method: GitHub Private Vulnerability Reporting
Please do **NOT** open a public issue. Instead, submit a private report using GitHub's built-in Private Vulnerability Reporting:
1. Navigate to the [Security Advisories](https://github.com/davide6600/wallet-privacy-test-bench/security/advisories/new) tab on this repository.
2. Click **"Report a vulnerability"** to open a confidential disclosure report.
3. Provide a clear description of the vulnerability, reproduction steps, and any suggested patch.

### Alternative Contact
If you cannot use GitHub Security Advisories, you may reach the maintainer via the privacy-preserving GitHub contributor address:
- **Contact:** `39161933+davide6600@users.noreply.github.com`

We will acknowledge receipt within 48–72 hours and provide an estimated timeline for verification and remediation.
