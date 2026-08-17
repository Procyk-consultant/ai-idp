---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Location: Saguenay, Québec, Canada
File: project-control/VALIDATION_STATUS.md
Title: Validation Status
Purpose: Separate executed validation evidence from current source implementation state
Version: 2.0.0-reconciliation
Status: Source Implementation Complete / Runtime Revalidation Pending
Last Material Revision: 2026-08-17
Branch: reconcile-2026-08-14
Historical Baseline: b13e51baa51c9e2bb0a5bff4f3911a6902b51206
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Validation Status

## 1. Controlling rule

Validation language follows a strict evidence rule:

- **implemented** means functional source exists;
- **tested** means the relevant test was actually executed;
- **verified** means the relevant evidence was directly inspected/cross-checked;
- **validated** means the defined validation procedure was actually executed;
- **reproducible** requires a successful clean rerun;
- **certified** requires the applicable independent/accredited certification process.

A source change is not promoted to a passing validation claim merely because it appears correct under static inspection.

## 2. Historical executed baseline — 2026-08-02

The last fully executed project-wide validation remains the v2.0.0 baseline associated with the repository state later published at commit:

`b13e51baa51c9e2bb0a5bff4f3911a6902b51206`

Recorded evidence for that baseline includes:

- **113/113 tests passed**;
- clean demonstration scenario completed;
- four-event ledger verification completed;
- 25 specification documents represented in the corpus;
- **14 JSON schemas** represented in the validated corpus;
- schema validation recorded against JSON Schema Draft 2020-12;
- Tectonic 0.16.9 research-paper compilation recorded as successful;
- 13-page paper visual gate recorded as passed;
- release/archive/checksum records generated for that release state.

These are **historical executed facts about the 2026-08-02 baseline**. They are not automatically inherited by later source modifications.

## 3. Current reconciliation branch — 2026-08-17

Working branch:

`reconcile-2026-08-14`

The branch contains material post-baseline changes in runtime code, schemas, tests, specifications, security/privacy enforcement, cryptographic backends, federation, durable governance state, CI definition, and public documentation.

### Current source-implementation status

| Area | Source status | Fresh runtime/live validation |
|---|---|---|
| Independent signature verification / verify-only public keys | Implemented + hardened | Pending |
| Duplicate event detection | Implemented + hardened | Pending |
| Canonical event/registry/key/authority state isolation | Implemented + hardened | Pending |
| Fail-closed authorization scope | Implemented + hardened | Pending |
| Exact action-intent approval digest incl. visibility | Implemented + hardened | Pending |
| Approver entitlement policy contract | Implemented | Pending |
| Single-use / dual approval enforcement | Implemented + hardened | Pending |
| Durable SQLite approval-consumption state | Implemented | Pending |
| Shared PostgreSQL atomic approval consumption | Implemented | Pending live database validation* |
| Recursive bounded delegation lineage | Implemented + hardened | Pending |
| Governed operational-event boundary | Implemented + hardened | Pending |
| Denial evidence | Implemented + hardened | Pending |
| API agent proof-of-possession | Implemented + hardened | Pending |
| Process-local replay reservation | Implemented | Pending |
| Durable SQLite replay reservation | Implemented | Pending |
| Shared PostgreSQL replay reservation | Implemented | Pending live database validation* |
| Strict public event projection | Implemented + hardened | Pending |
| Scoped public verification-key export | Implemented + hardened | Pending |
| Public registry attribute projection | Implemented + hardened | Pending |
| Signed federation-agreement verification | Implemented | Pending |
| Cross-registry public resolution / TTL cache / break detection | Implemented | Pending |
| Disclosed federated event/chain verification | Implemented | Pending |
| WAL fail-closed recovery / corruption quarantine | Implemented + hardened | Pending |
| Parallel signature verification path | Implemented + hardened | Pending |
| PostgreSQL event sequence / JSONB / append-only handling | Implemented + hardened | Pending live integration* |
| PKCS#11 Ed25519 HSM generation/signing | Implemented | Pending token/device validation* |
| AWS KMS asymmetric signing | Implemented | Pending credentialed validation* |
| Azure Key Vault EC signing | Implemented | Pending credentialed validation* |
| Google Cloud KMS EC signing | Implemented | Pending credentialed validation* |
| ML-DSA-65 via liboqs | Implemented | Pending fresh runtime validation* |
| SLH-DSA SHA2-128s via liboqs | Implemented | Pending fresh runtime validation* |
| OpenTelemetry exporter | Implemented | Pending collector validation* |
| GitHub remote publication path | Implemented | Pending credentialed validation* |
| CI definition (Ruff/MyPy/tests as real gates) | Hardened | Not rerun |

`Implemented`/`Hardened` means the source-level implementation/reconciliation is present. It does **not** mean the current branch has passed a fresh execution gate.

## 4. Current schema inventory

Historical executed baseline: **14 schemas**.

Current reconciliation branch: **15 schemas**.

The branch adds `schemas/approval.schema.json` and hardens authorization, delegation, and event schemas to reflect exact-action approvals, bounded scopes, governed execution and disclosure controls.

No new schema-validation pass count is claimed until the branch tests are executed.

## 5. Current test-source changes

The reconciliation branch adds or materially strengthens source tests covering:

- authorization scope dimensions and missing-context fail-closed behavior;
- exact action-digest approvals and anti-retargeting, including visibility changes;
- approver entitlement and dual approval by distinct entitled approvers;
- durable/atomic approval-consumption state;
- recursive delegation and child-scope narrowing;
- governed operational acceptance and denial evidence;
- API proof-of-possession and replay rejection;
- durable replay state across SQLite store instances;
- public projection/non-enumeration/key-scope/privacy controls;
- adversarial tampering/deletion/reordering/duplicate-ID cases;
- canonical object-alias isolation;
- WAL validation-before-write, corruption quarantine and recovery;
- parallel signature verification;
- authorization and approval JSON-schema conformance;
- signed federation agreements, remote-break handling and disclosed-chain verification;
- credential-free managed-KMS contract behavior;
- ML-DSA-65 and SLH-DSA live round-trip behavior when liboqs is present.

These tests are **present in source but unexecuted in the current reconciliation session**. Therefore there is no new total passing-test count.

## 6. Cryptographic backend completion

The former source-level placeholder gap for production cryptographic signing has been closed in the branch:

- PKCS#11 generates token-resident non-extractable Ed25519 private keys and signs through `CKM_EDDSA`;
- AWS KMS creates/uses asymmetric signing keys, retrieves public keys, signs, verifies and disables keys;
- Azure Key Vault creates EC signing keys and performs remote ES256 sign/verify;
- Google Cloud KMS creates asymmetric signing keys, retrieves public keys, signs and disables key versions;
- ML-DSA-65 and SLH-DSA SHA2-128s call liboqs for actual key generation, signing and verification rather than raising source placeholders.

See `project-control/CRYPTO_BACKEND_COMPLETION_2026-08-17.md`.

## 7. Durable governance-state completion

Source-level mechanisms now exist for security state that previously remained local-only or target-only:

- `ReplayReservationStore` abstraction;
- process-local in-memory replay reservation;
- durable SQLite replay reservation;
- shared PostgreSQL replay reservation;
- `ApprovalConsumptionStore` abstraction;
- durable SQLite single-use approval consumption;
- shared PostgreSQL atomic multi-approval consumption;
- fail-closed approver-entitlement contract with explicit grants/composition and external IAM adapter point;
- FastAPI wiring for the durable replay/approval/entitlement providers.

This does not claim that a particular production database/IAM deployment has been configured or validated.

## 8. Federation source completion

AegisTrace now includes a reference signed federation gateway with:

- bilateral federation agreements;
- signatures by keys bound to both registry authorities;
- effective/expiry/revocation checks;
- public-safe remote entity resolution;
- bounded TTL cache;
- scoped public verification-key retrieval;
- federation-break detection;
- fully disclosed event and contiguous hash-chain/signature verification.

Institutional registry operators, authenticated controlled/sealed federation, regulator-operated infrastructure, actual production endpoints, and legal recognition remain external deployment/adoption boundaries.

## 9. Validation gates

| Gate | Historical 2026-08-02 evidence | Current branch state |
|---|---|---|
| Initial comprehension / project inventory | Passed historically | No new execution required for source reconciliation |
| Research protocol / evidence registers | Passed/partial as documented historically | Historical evidence retained; time-sensitive claims require refresh before consequential use |
| Formal architecture / specification corpus | Passed historically | Materially updated; source reconciliation complete, runtime/schema gate pending |
| Functional implementation | Passed for baseline | Source implementation/hardening complete; fresh execution pending |
| Engineering verification | **113/113 passed historically** | **Not rerun** |
| Security/privacy/permanence/conformance suites | Passed as part of historical corpus | Strengthened source tests added; not rerun |
| Scientific evaluation | Partial historically | No new empirical deployment evidence created |
| Paper compilation | Passed historically | Not recompiled in this reconciliation |
| External/independent validation | Partial/pending historically | Still pending |
| Release/archive/checksum generation | Passed for historical release | Regenerate only after a new successful validation/release gate |

## 10. GitHub Actions state

The previously observed GitHub Actions failure for the baseline commit was reported by GitHub as a job that **did not start because the account was locked due to a billing issue**. The recorded job had no executed workflow steps.

Classification:

**CI BLOCKED BEFORE EXECUTION / NOT EVIDENCE OF A CODE OR COMPILATION FAILURE.**

No CI rerun was initiated during the current reconciliation.

## 11. Remaining external/live boundaries

The following are **not unfinished core source implementations**. They require the corresponding external environment, credentials, hardware, operators, independent evidence, or institutional authority:

- live PostgreSQL production deployment and operational evidence*;
- live PKCS#11/HSM device validation*;
- AWS/Azure/GCP credentialed KMS validation*;
- OpenTelemetry collector deployment/validation*;
- liboqs runtime/deployment assurance and fresh PQC execution evidence*;
- credentialed GitHub remote anchoring/publication*;
- organization-specific IAM/directory adapter configuration*;
- authenticated controlled/sealed federation with real remote registry operators*;
- independent archival infrastructure / regulator-operated vault / transparency infrastructure*;
- external peer review, accreditation, certification, government/standards adoption*.

The asterisk denotes **external activation, target-environment evidence, or institutional assurance**, not an omitted source implementation.

## 12. Required validation before a new verified baseline

Before this branch can be described as a new validated release/baseline, execute and record at minimum:

1. complete branch-diff review;
2. Ruff;
3. MyPy as a hard gate;
4. unit tests;
5. integration tests;
6. security tests;
7. privacy tests;
8. permanence tests;
9. conformance/schema tests;
10. governed demo;
11. full `verify --keys` using generated public verification material;
12. negative verification with missing/invalid keys;
13. stale/replayed/tampered API-request tests;
14. wrong exact-action digest / approval-retargeting tests;
15. durable replay and atomic approval-consumption tests;
16. corrupted WAL / duplicate-event / delegation-widening / public-leakage tests;
17. signed federation / federation-break / disclosed-chain tests;
18. ML-DSA-65 and SLH-DSA live round trips with the pinned liboqs validation profile;
19. configured HSM/KMS/PostgreSQL/OTel/GitHub-remote integration tests where appropriate target infrastructure/credentials exist;
20. paper/release build only when producing the next release artifact;
21. new validation report and new checksums without overwriting historical evidence.

## 13. Current conclusion

**Source implementation and hardening are complete on `reconcile-2026-08-14`. Runtime and target-environment revalidation are pending.**

`main` remains the historical public baseline. No merge, release, certification, or new passing-test claim is implied by this status file.
