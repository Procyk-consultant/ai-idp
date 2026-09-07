---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/VALIDATION_STATUS.md
Title: Validation Status
Purpose: Separate verified local 2.1.0 evidence from historical and external claims
Version: 2.1.0
Status: Local Engineering Gates Passed / External Activation Not Verified
Last Material Revision: 2026-09-07
Branch: local/2.1.0-reconciliation
Historical Public Baseline: b13e51baa51c9e2bb0a5bff4f3911a6902b51206
---

# Validation Status — 2.1.0

## Evidence vocabulary

- **Implemented:** functional source exists.
- **Tested:** the named test was executed.
- **Verified:** the cited evidence was directly inspected or reproduced.
- **Activated:** a real external service, credential, device, or target environment was exercised.
- **Published:** an external public action completed and its resulting identifier or URL was verified.

These terms are not interchangeable.

## Executed local gates

| Gate | Command/scope | Result |
|---|---|---|
| Windows operator path | `BUILD_WINDOWS.bat`; seven stages | PASS; exit 0 |
| Lint | Ruff over `src tests` | PASS |
| Type safety | MyPy over `src tests` | PASS; 80 files |
| Test collection | Pytest | 164 collected |
| Test execution | Full tracked suite | PASS: 162 passed, 2 opt-in native-PQC skips |
| Package install | Editable install without dependency mutation | PASS; package 2.1.0 |
| Wheel build | PEP 517 wheel | PASS; 115,507 bytes; SHA-256 `70f908c90b400f2a35358fc30ac297e2c71fcf31d9feb927fabe34017e3956a6` |
| Governed demo | AegisTrace admin demo | PASS; 4 events; `GOVERNED`; `verification: OK` |
| Ledger verification | Independent verify CLI with exported public keys | PASS; 4 event hashes, chain links, and signatures |
| Paper build | Tectonic 0.16.9 | PASS; exit 0; 13 pages |
| Container | Docker Desktop Linux engine | NOT EXECUTED; engine unavailable |

Warnings disclosed:

- FastAPI test-client dependency reports a Starlette deprecation warning about the current `httpx` integration.
- Starlette reports an AnyIO alias deprecation warning.
- Tectonic reports Fontconfig configuration and underfull-box warnings; compilation completes successfully.

## Explicitly unactivated or unverified targets

- live PostgreSQL service and operational durability/failover;
- real PKCS#11 token or hardware security module;
- credentialed AWS, Azure, or Google KMS;
- native ML-DSA/SLH-DSA round trips in an explicitly provisioned liboqs environment;
- live OpenTelemetry collector;
- credentialed GitHub publication adapter;
- independently operated federation registries;
- external certification, accreditation, legal adoption, or government acceptance;
- email delivery receipts and recipient responses;
- publication of the local 2.1.0 branch.

## Historical evidence retained

The 2026-08-02 v2.0.0 release recorded 113/113 tests, a successful demo/ledger verification, Tectonic compilation, release derivatives, checksums, and numbered archives. Those records remain evidence about v2.0.0 only. They are not relabelled as 2.1.0.

## Veritas contradiction check

Strongest alternative explanation: the version could be called 2.1.0 merely because one D-drive PDF uses that number while the runnable package remained 2.0.0. That explanation was initially supported by the fresh package build, which produced 2.0.0 before this pass. It is no longer the current runtime state: package metadata, runtime `__version__`, API health/version, container label, Compose image, README, changelog, and metadata tests now agree on 2.1.0, and the fresh local suite passes. The historical public state nevertheless remains 2.0.0 until a separately authorized external update occurs.
