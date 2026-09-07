---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/PROJECT_STATUS.md
Title: Project Status
Purpose: Controlling local project status and evidence boundaries
Version: 2.1.0
Status: Authoritative Locally / Not Published Online
Last Material Revision: 2026-09-07
Branch: local/2.1.0-reconciliation
Source Branch: reconcile-2026-08-14
Historical Public Baseline: b13e51baa51c9e2bb0a5bff4f3911a6902b51206
Licence Status: All Rights Reserved; no public licence granted
---

# Project Status — AI-IDP / AegisTrace 2.1.0

## Controlling state

The authoritative current project state is **local version 2.1.0**. It is based on the 124-commit `reconcile-2026-08-14` line plus the 2026-09-07 evidence repair and verification pass on `local/2.1.0-reconciliation`.

Version 2.1.0 has **not** been merged to public `main`, tagged, released, deployed, or published online. Public GitHub `main` and the Zenodo DOI remain the historical v2.0.0 baseline. Historical v2.0.0 release records remain intact and must not be relabelled as 2.1.0 evidence.

## Current verified implementation

The local 2.1.0 source includes:

- persistent identity and key lifecycle;
- fail-closed multidimensional authorization and exact action-intent approvals;
- approver entitlements, single/dual approval, and atomic consumption;
- bounded recursive delegation;
- authenticated governed API writes with nonce replay resistance;
- denial evidence and strict public disclosure projections;
- append-only/hash-chained ledgers, WAL recovery, and parallel verification;
- SQLite and PostgreSQL durability paths;
- PKCS#11 and managed KMS signing paths;
- crypto-agility paths for Ed25519, ML-DSA-65, and SLH-DSA-128s;
- OpenTelemetry and GitHub adapter paths;
- signed federation agreements and disclosed-chain verification;
- 25 specification documents, 15 JSON schemas, 58 Python source files, and 22 Python test/support files.

External services, hardware, credentials, independent operators, and target-environment activation remain separate from implemented source.

## Fresh local verification — 2026-09-07

| Gate | Result |
|---|---|
| Python | 3.12.10 |
| Windows one-click build | PASS: `BUILD_WINDOWS.bat` completed all seven stages and returned exit 0 |
| Ruff | PASS on `src` and `tests` |
| MyPy | PASS; no issues in 80 source/test files |
| Pytest | PASS: 162 passed, 2 skipped, 164 collected |
| Native PQC | 2 live liboqs tests intentionally skipped unless `AEGISTRACE_RUN_LIBOQS_TESTS=1` |
| Package metadata | PASS: installed package and runtime both report 2.1.0 |
| Wheel | PASS: `aegistrace-2.1.0-py3-none-any.whl`, 115,507 bytes, SHA-256 `70f908c90b400f2a35358fc30ac297e2c71fcf31d9feb927fabe34017e3956a6` |
| Governed demo | PASS: 4 events, governance mode `GOVERNED`, verification `OK` |
| Independent ledger verification | PASS: event hashes, hash chain, and 4 signatures verified |
| Paper | PASS: Tectonic 0.16.9 exit 0; 13-page PDF; disclosed underfull-box/fontconfig warnings |
| Container | BLOCKED BY ENVIRONMENT: Docker CLI present, Docker Desktop Linux engine unavailable |

Two dependency deprecation warnings were emitted by the FastAPI/Starlette test client. They did not fail the suite and remain dependency-maintenance items.

## Defects found and repaired in this pass

1. The API replaced a caller-supplied empty ledger because `ledger or AppendOnlyLedger()` treated an empty ledger as false. The boundary now distinguishes `None` explicitly.
2. Event collection was typed to one concrete ledger even though the runtime supports both append-only and batched ledgers. A minimal `EventLedger` protocol now defines the required contract.
3. GCP KMS verification accepted a broad public-key union at the type boundary. It now fails closed unless the loaded public key is elliptic-curve.
4. A leaf delegation returned a scope-widening reason before enforcing the leaf boundary. Delegation depth is now validated first.
5. The standard `test-full` extra installed `liboqs-python`; importing it can download and compile a native liboqs tree when the library is absent. Native PQC tests are now explicit opt-in and the dependency remains available through the separate `pqc` extra.
6. Current package/API/container metadata still identified the reconciled code as 2.0.0. Current-facing runtime metadata now identifies version 2.1.0 while historical 2.0.0 records remain historical.

## Indigenous data-governance decision

The controlling rule is context-specific:

- meaningful, distinctions-based rights-holder engagement is required before a deployment that materially affects Indigenous rights, community data, governance authority, or services;
- this is **not a universal implementation gate** for unrelated deployments without that material nexus;
- AI-IDP does not remove or override legal duties, agreements, or community governance requirements where they apply.

This rule is corroborated by the 2.1.0 French synthesis PDF, the current README/privacy/specification text, and the relevant source-branch commits. Stale universal-precondition wording was corrected in current active documents. Historical release snapshots retain their historical wording.

## Communications and content evidence

- **Emails/contacts:** Pierre-Edward Procyk states that emails were sent and contacts completed. The inspected local archive contains drafts and a reviewed Gmail-draft transcript, but no sent-mail receipt, message header, or communications log proving the completed sends. Classification: **user-confirmed; independent receipt evidence unavailable in the inspected files**. The project must not revert this to “not sent,” but it also must not invent dates, recipients, or message identifiers.
- **Content work:** verified local evidence includes a structured five-series/15-post LinkedIn package, two scheduler-ready text exports, a 15-image prompt set, at least 18 named AI-IDP/AegisTrace visual assets in `Visual_components`, a visually sound three-page French 2.1.0 synthesis PDF, and the repository's paper, government, technical, impact, research, specification, and presentation-support corpus. These files prove substantial drafting/production work; they do not by themselves prove publication.

## GitHub and CI state

- Public `main`: `b13e51baa51c9e2bb0a5bff4f3911a6902b51206`.
- Public reconciliation branch: `e148cf484b782872416121704a7887935a21bc71`, 124 commits ahead of public `main` and 0 behind at the inspected merge base.
- Public update branch: `54c8367bb62b68a1a7b36ecd54428183365367ee`.
- Current authoritative 2.1.0 branch: local only; no remote push performed in this pass.
- Latest public CI run inspected: run `31344416895`, job `93323578720`, 0 workflow steps, runner ID 0. GitHub's annotation says the job was not started because the account is locked due to a billing issue.

The CI evidence proves a pre-execution GitHub account/billing lock, not a code failure. Because GitHub documents standard hosted runners as free for public repositories, an erroneous or stale account/subscription billing state is plausible. Proving that it is specifically a GitHub subscription bug requires authenticated billing/support evidence that was not available to this local inspection.

## External action boundary

No public merge, push, tag, release, deployment, publication, post, email, account change, billing change, or licence change was performed by the 2026-09-07 local reconciliation. Any later GitHub update must name the exact branch/commit and receive explicit action-time authorization.
