# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| latest (`main`) | ✅ |
| older releases | ❌ |

Security fixes are backported only to the latest stable release. Users are encouraged to keep their deployments up to date.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

If you discover a security vulnerability in OpenTransit, please disclose it responsibly by emailing the maintainer at the address listed in the GitHub profile. Include as much detail as possible:

- A description of the vulnerability and its potential impact.
- Steps to reproduce or proof-of-concept code.
- Affected component(s) and version(s).
- Any suggested mitigations, if known.

You will receive an acknowledgement within **48 hours** and a more detailed response within **7 days** outlining the remediation plan. We aim to release a fix within **30 days** of confirmed impact, depending on severity.

We ask that you:
- Give us reasonable time to address the issue before public disclosure.
- Avoid accessing or modifying data that does not belong to you.
- Act in good faith and not disrupt service availability.

## Security Design Principles

OpenTransit is built with the following security principles:

### Least Privilege
Each microservice runs with the minimum permissions required. Database users are scoped to the tables owned by their service. Container processes run as non-root users.

### Defense in Depth
Multiple layers of controls (API gateway, service-level auth, database-level constraints) are used so that no single failure exposes the system.

### Secure Defaults
Debug mode, verbose error responses, and default credentials are disabled out of the box. The `.env.example` file documents all required configuration but does not include real secrets.

### Supply Chain Security
- Python dependencies are pinned to exact versions and audited with `pip audit` in CI.
- Docker base images are pinned to specific digest hashes in production builds.
- Signed commits are encouraged for all maintainers.

## Known Security Considerations

| Area | Notes |
|---|---|
| Payment data | Raw card data is never stored; all payment processing is delegated to a PCI-DSS certified gateway. |
| Personal data | The system is designed for GDPR compliance. Users can request data export and deletion via the API. |
| Transit fare evasion | Each ticket carries a unique, cryptographically random `qr_code` token generated with `secrets.token_hex`. Ticket validation is idempotent and one-time: a ticket transitions to `used` on first validation and subsequent attempts are rejected. |

## Responsible Disclosure Hall of Fame

We thank the security researchers who have responsibly disclosed vulnerabilities to us. Contributors will be listed here with their permission.
