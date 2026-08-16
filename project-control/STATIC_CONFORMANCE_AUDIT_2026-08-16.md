---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/STATIC_CONFORMANCE_AUDIT_2026-08-16.md
Title: Static Code-to-Standard Conformance Audit — 2026-08-16
Version: 2.0.0-reconciliation
Status: Working Audit / Not Runtime-Revalidated
Last Material Revision: 2026-08-16
Branch: reconcile-2026-08-14
Baseline Commit: b13e51baa51c9e2bb0a5bff4f3911a6902b51206
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Static Code-to-Standard Conformance Audit — 2026-08-16

## 1. Purpose

This audit compares the AI-IDP normative target, the AegisTrace v2.0.0 reference implementation, the executable tests, and the public-facing project documentation. It preserves the project's intended high-assurance destination rather than weakening requirements to match incomplete integrations.

This is a **static reconciliation pass**. No test suite, compilation, live HSM/KMS operation, live PostgreSQL deployment, live OTLP export, live PQC signing, or release build was executed during this pass.

## 2. Authoritative Validation Baseline

The last fully executed validation remains the 2026-08-02 v2.0.0 baseline documented in `release/VALIDATION_REPORT.md` and `project-control/VALIDATION_STATUS.md`:

- 113/113 tests passed;
- clean AegisTrace demo completed;
- four-event ledger verification passed;
- 23 normative invariants were represented in the validation corpus;
- JSON schemas validated against Draft 2020-12;
- Tectonic paper compilation passed;
- production-hardening modules were represented in the validated test corpus.

The current reconciliation branch contains post-baseline code changes. Therefore, **113/113 is historical evidence, not a validation claim for the current branch** until a fresh authorized run is completed.

The latest observed GitHub-hosted CI failure is classified separately: GitHub reported that the job did not start because the account was locked due to a billing issue. No workflow step executed; this is not evidence of a compilation or test failure.

## 3. Status Vocabulary

| Status | Meaning |
|---|---|
| `VERIFIED-BASELINE` | Directly supported by the recorded 2026-08-02 executed validation. |
| `STATIC-CONFIRMED` | Implementation is directly visible in source during this audit, but not newly executed. |
| `HARDENED-UNVALIDATED` | Static defect/gap was patched on the reconciliation branch; fresh execution still required. |
| `TARGET*` | Required/intended high-assurance capability with implementation/interface work present, but live activation or completion depends on external runtime/service/hardware or remaining implementation work. |
| `GAP` | Static inspection found a mismatch between normative intent and implementation/test depth. |
| `HISTORICAL` | Preserved evidence from an older project state; not a current-state assertion. |

## 4. Core Conformance Matrix

| Area | Normative intent | Current static assessment | Status |
|---|---|---|---|
| Persistent actor identity | Permanent unique actor and instance identifiers | URI/identifier model and lifecycle registry implemented | `STATIC-CONFIRMED` |
| Identifier resolvability | Revoked/terminated identities remain resolvable | Lifecycle registry preserves records and resolution | `VERIFIED-BASELINE` / `STATIC-CONFIRMED` |
| Ed25519 event signatures | Material events cryptographically signed | Signing and verification implementation present | `VERIFIED-BASELINE` |
| Hash-chained ledger | Append-only sequence with detectable tampering/reordering | Core ledger present; branch now also rejects duplicate event IDs | `HARDENED-UNVALIDATED` |
| Independent verification | Verification must fail when cryptographic evidence is unavailable/invalid | Branch changed unknown-key behavior from silent skip to explicit failure; hash-only mode must be explicit | `HARDENED-UNVALIDATED` |
| Public verification keys | Verifier can operate without private signing material | Branch adds verify-only public-key registry import/export | `HARDENED-UNVALIDATED` |
| Authorization | Every governed action resolves to valid signed authority | Signatures existed; branch adds signature, policy-version and signer-binding verification | `HARDENED-UNVALIDATED` |
| Approval | Required approvals are signed, valid and single-use | Existing single-use model retained; branch adds signature/binding validation | `HARDENED-UNVALIDATED` |
| Dual approval | High-impact designated actions require two distinct approvers | Constant existed but was not enforced; branch now enforces two distinct valid approvals for designated actions | `HARDENED-UNVALIDATED` |
| Delegation | Child authority is bounded, signed and revocable | Signed delegation and basic action/resource/task/time scope exist | `STATIC-CONFIRMED` / `GAP` |
| Governance enforcement at event boundary | Event acceptance should resolve authorization/delegation/approval before governed action | `EventCollector` validates signature-key binding and event integrity but is not yet directly coupled to `PolicyEngine`/`DelegationBroker` | `GAP` |
| API governance enforcement | HTTP event ingestion should not bypass authority checks | API currently wires registry/keys/ledger/collector but not policy/delegation services | `GAP` |
| Public-tier redaction | PUBLIC projection excludes sensitive fields | Visibility tier is recorded; current tests do not demonstrate a complete projection/redaction enforcement path | `GAP` |
| PostgreSQL* | Production persistence with sequence integrity, access logs, anchors and legal holds | Substantial backend exists; explicit batch-sequence semantics require hardening review | `TARGET*` / `GAP` |
| HSM/KMS* | Private keys remain within HSM/KMS; signing occurs there | Abstractions and provider paths exist; live PKCS#11/cloud signing methods are not yet fully implemented/activated | `TARGET*` |
| OpenTelemetry* | Runtime observability export without replacing canonical ledger | Exporter implementation present; external collector activation required | `TARGET*` / `STATIC-CONFIRMED` |
| PQC migration* | Cryptographic agility toward ML-DSA/SLH-DSA | Scheme abstraction and migration orchestration exist; live PQC operations require external runtime and completion | `TARGET*` |
| GitHub remote* | Publish anchors/status/evidence through remote integration | REST/git paths implemented; live credentialed deployment is external | `TARGET*` / `STATIC-CONFIRMED` |
| Batched WAL ledger | High-throughput durable append path | Implementation exists; corrupted WAL handling currently requires fail-closed hardening | `GAP` |
| Conformance tests | Executable evidence for normative invariants | Historical suite passed; static review found some tests verify only shallow proxies for broader invariants | `VERIFIED-BASELINE` / `GAP` |

## 5. Static Findings Requiring Hardening

### C-001 — Independent verification could previously pass without verification keys

**Original behavior:** `LedgerVerifier` silently skipped unknown signing keys. The CLI also exposed `--keys` without actually loading them.

**Risk:** A command labelled verification could return success after checking only hashes/chain while a reader might infer signatures were verified.

**Branch action:**
- unknown verification key is now a failure when signature verification is requested;
- hash-only verification is explicit;
- verify-only public-key registries can be imported/exported;
- demo output is being aligned to produce public verification material.

**Status:** `HARDENED-UNVALIDATED`.

### C-002 — Event-ID uniqueness was implicit rather than enforced

**Original behavior:** `AppendOnlyLedger` checked chain/hash integrity but had no explicit duplicate `event_id` guard.

**Branch action:** ledger maintains an event-ID set and rejects duplicate identifiers; verifier also reports duplicates.

**Status:** `HARDENED-UNVALIDATED`.

### C-003 — Authorization signatures existed but were not revalidated during policy evaluation

**Original behavior:** authorization and approval records were signed at issuance, but `PolicyEngine.evaluate()` did not verify those signatures or signer bindings.

**Branch action:** signed records are reconstructed and verified; current policy version and signer binding are required.

**Status:** `HARDENED-UNVALIDATED`.

### C-004 — Dual-approval requirement declared but not enforced

**Original behavior:** `DUAL_APPROVAL_REQUIRED` existed as policy data but evaluation accepted a single approval.

**Branch action:** designated actions require two valid approvals from distinct approvers. Existing single-approval calls remain compatible for non-dual actions.

**Status:** `HARDENED-UNVALIDATED`.

### C-005 — Governance services are not yet coupled to every event-ingestion path

`EventCollector` proves event integrity and signing-key/actor binding. It does not itself resolve the supplied `authorization_id`, `delegation_id`, or `approval_id` against `PolicyEngine` / `DelegationBroker`. The FastAPI server currently uses this collector directly.

**Required end-state:** governed material actions must pass authority/delegation/approval enforcement before canonical acceptance, while evidence-only or imported-event verification paths remain explicitly distinguished.

**Status:** `GAP` — design/implementation work required before claiming the API itself is a complete enforcement boundary.

### C-006 — Delegation scope model is broader than current enforcement depth

`DelegationScope` contains task, resource, action, time, geography, tool, model, provider and depth fields. Current `encompasses()` actively evaluates action/resource/task/time; the additional dimensions and delegation-depth chain require stronger enforcement at orchestration time.

**Status:** `GAP`.

### C-007 — PostgreSQL batch sequencing semantics require correction

The PostgreSQL schema defines `seq BIGSERIAL`, while `append_events_batch()` supplies enumerated sequence values beginning at zero for each provided batch. This can conflict with the intended globally monotonic event order when multiple batches are appended.

**Required end-state:** one unambiguous globally ordered sequence source, transactionally consistent with canonical event order.

**Status:** `GAP`.

### C-008 — WAL replay is not fail-closed on corrupted entries

`BatchedLedger._replay_wal()` currently catches malformed/corrupt entries and continues, then truncates the WAL after replay.

**Risk:** a high-assurance recovery path should preserve/quarantine evidence and surface corruption rather than silently discard it.

**Required end-state:** fail-closed recovery, preserved corrupt WAL evidence, explicit recovery report, no silent truncation after partial/corrupt replay.

**Status:** `GAP`.

### C-009 — Parallel verification target is declared but not yet implemented in the batched verifier path

`BatchConfig.parallel_verify` and module documentation describe parallel signature verification; current `verify()` delegates to the standard sequential verifier.

**Status:** `TARGET*` / `GAP`.

### C-010 — Public-tier privacy tests do not yet prove full redaction/projection

The current tests confirm the PUBLIC visibility tier, but the visible test path does not assert a concrete projection removes all sensitive fields. Similar comments in the conformance suite describe downstream filtering rather than exercising it.

**Required end-state:** explicit projection API + negative leakage tests covering sensitive fields, identity resolution, approvals/delegations and evidence payloads.

**Status:** `GAP`.

### C-011 — Some security/conformance tests are weaker than their names imply

Static inspection identified examples where a test contains no final security assertion or checks for the absence of mutation methods rather than proving immutability against all supported paths.

**Required end-state:** each normative invariant maps to an executable adversarial assertion with clear pass/fail evidence.

**Status:** `GAP` in test depth; the historical 113/113 execution result remains valid for the test corpus that existed at that time.

## 6. Advanced Capability Notation

The project may continue to present the intended high-assurance capabilities prominently. Where live activation/completion depends on an external environment, use an asterisk and a compact note rather than removing the capability:

- PostgreSQL storage*
- HSM / cloud-KMS signing*
- OpenTelemetry export*
- post-quantum migration/signing*
- GitHub remote anchoring/publication*
- regulator-controlled or external federation infrastructure*

Recommended note:

> `*` Target/high-assurance capability represented in the AegisTrace architecture and implementation path. Live production activation and/or final validation depends on the required external service, hardware, credential, runtime library, regulator/institutional infrastructure, or deployment environment. The asterisk describes activation status; it does not reduce the AI-IDP normative target.

## 7. Indigenous Data Governance Reconciliation

The project retains Indigenous data sovereignty and distinctions-based governance as a serious design objective. The former blanket statement that rights-holder consultation is a prerequisite for **every** implementation is being replaced with a context-sensitive requirement:

- meaningful rights-holder engagement is required where Indigenous rights, community data, governance authority or services are materially implicated;
- public-framework analysis is not a substitute for engagement in those cases;
- Indigenous committee/rights-holder participation is not a universal gate for unrelated implementations with no material Indigenous nexus.

This change preserves the governance objective while removing an unnecessary universal dependency from unrelated deployments.

## 8. Validation Gate Before Merge

Before this reconciliation branch can be described as validated or merged into the public baseline as a new verified release, the following controlled gate is required:

1. review the complete branch diff;
2. update affected tests to the new verification/authorization contracts;
3. run Ruff;
4. run MyPy as an actual gate, not `|| true`;
5. run unit, integration, security, privacy, permanence and conformance suites;
6. run the demo and full `verify --keys` path;
7. test corrupted/missing key evidence and fail-closed behavior;
8. if available, exercise optional integration suites separately from core validation;
9. compile the paper only if material paper sources changed or a new release artifact is being produced;
10. record results in a new validation report rather than overwriting the 2026-08-02 historical evidence.

No step in this section was executed during this static audit.

## 9. Current Decision

**Keep the standard ambitious. Fix the implementation toward the standard. Do not lower the standard to match temporary implementation gaps.**

The current branch is a controlled hardening/reconciliation branch. `main` remains the last public repository baseline until review and authorization of the final diff.
