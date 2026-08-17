---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/STATIC_CONFORMANCE_AUDIT_2026-08-16.md
Title: Static Code-to-Standard Conformance Audit — Reconciled 2026-08-17
Version: 2.0.0-reconciliation
Status: Source Hardening Complete / Runtime Revalidation Pending
Last Material Revision: 2026-08-17
Branch: reconcile-2026-08-14
Baseline Commit: b13e51baa51c9e2bb0a5bff4f3911a6902b51206
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Static Code-to-Standard Conformance Audit

## 1. Scope

This audit compares the AI-IDP normative target, AegisTrace source, schemas, tests, and public documentation. It preserves the intended high-assurance destination rather than weakening the standard to match temporary implementation or deployment limits.

This is a **static/source reconciliation**. No fresh test suite, compiler, live PostgreSQL instance, HSM/KMS, OTLP endpoint, PQC runtime, credentialed remote publication, or release build was executed during this pass.

## 2. Executed baseline versus current branch

### Historical executed baseline — 2026-08-02

The recorded baseline reports:

- 113/113 tests passed;
- demo/ledger verification passed for that source state;
- Tectonic paper compilation passed;
- 25 specification documents and 14 JSON schemas were represented in the baseline corpus.

Those facts remain historical evidence for the 2026-08-02 source state.

### Current hardening branch — 2026-08-17

The reconciliation branch contains material post-baseline source changes. It now contains **15 JSON schemas**, including the explicit approval schema. These changes are not assigned a new passing-test count until the validation gate is actually executed.

## 3. Status vocabulary

| Status | Meaning |
|---|---|
| `VERIFIED-BASELINE` | Supported by the recorded 2026-08-02 executed validation. |
| `STATIC-CONFIRMED` | Directly visible in the current source, not newly executed. |
| `HARDENED-UNVALIDATED` | A source gap was closed or materially hardened; fresh runtime validation remains required. |
| `TARGET*` | High-assurance requirement/capability whose live activation depends on external infrastructure, runtime, credentials, hardware, institutional authority, or deployment topology. |
| `HISTORICAL` | Evidence about an older source/release state, retained without being presented as current execution evidence. |

## 4. Current conformance matrix

| Area | Current source assessment | Status |
|---|---|---|
| Persistent actor identity | Typed AI-IDP identifiers, lifecycle registry, permanent resolvability model | `STATIC-CONFIRMED` |
| Canonical state isolation | Ledger, registry, key, authorization, approval, and delegation getters return snapshots rather than mutable canonical aliases | `HARDENED-UNVALIDATED` |
| Event signing | Ed25519 event signing and historical public-key verification present | `VERIFIED-BASELINE` + `STATIC-CONFIRMED` |
| Hash-chained ledger | Ordered append, duplicate-ID rejection, hash verification, alias-resistant storage | `HARDENED-UNVALIDATED` |
| Independent verification | Missing public keys fail full verification; hash-only mode explicit; public-key import/export supported | `HARDENED-UNVALIDATED` |
| Parallel verification | Ordered chain/hash verification plus optional parallel signature checks with deterministic result ordering | `HARDENED-UNVALIDATED` |
| Authorization | Signed, issuer-bound, policy-versioned, actor/task/controller/principal-bound, fail-closed scope enforcement | `HARDENED-UNVALIDATED` |
| Scope dimensions | Action/task/resource/geography/tool/model/provider/time/depth evaluated; missing restricted context denies | `HARDENED-UNVALIDATED` |
| Approval | Signed, approver-bound, exact action-intent digest, single use | `HARDENED-UNVALIDATED` |
| Dual approval | Two distinct approvers required for designated actions and both must approve the same exact intent digest | `HARDENED-UNVALIDATED` |
| Delegation | Full-dimensional scope, nested subset enforcement, depth consumption, recursive signature/lineage verification, cycle protection | `HARDENED-UNVALIDATED` |
| Governed event boundary | Registry + authorization + scope + delegation + exact approval checks precede governed canonical append | `HARDENED-UNVALIDATED` |
| Denial evidence | Denied actions remain denied; best-effort signed `DENY` evidence records reason/request digest | `HARDENED-UNVALIDATED` |
| API request authentication | Agent proof-of-possession, timestamp freshness and nonce replay rejection before governance | `HARDENED-UNVALIDATED` |
| API public event disclosure | Strict allow-list projections; non-public event lookup non-enumerating | `HARDENED-UNVALIDATED` |
| Public verification keys | Export limited to keys used by PUBLIC evidence; private bindings omitted by default | `HARDENED-UNVALIDATED` |
| Public registry | Explicit public flag plus reviewed `public_attributes`; internal attributes not returned | `HARDENED-UNVALIDATED` |
| PostgreSQL* | Database-owned BIGSERIAL sequence, JSONB handling, production-oriented backend path | `HARDENED-UNVALIDATED` / `TARGET*` |
| Batched WAL | Validate-before-WAL, fsync option, caller-mutation isolation, corrupt WAL quarantine, background errors surfaced | `HARDENED-UNVALIDATED` |
| HSM/KMS* | Interfaces/provider paths present; live hardware/cloud enforcement requires external deployment | `TARGET*` |
| OpenTelemetry* | Exporter/runtime integration path present; collector endpoint required for live activation | `STATIC-CONFIRMED` / `TARGET*` |
| PQC* | Scheme abstraction/migration path present; live supported PQC runtime required | `TARGET*` |
| GitHub remote* | Remote integration path exists; credentialed live activation external | `STATIC-CONFIRMED` / `TARGET*` |
| Federation/regulator infrastructure* | Normative architecture retained; not represented as live institutional deployment | `TARGET*` |
| Test depth | New adversarial/privacy/governance/WAL/API/state-isolation/schema tests added in source | `HARDENED-UNVALIDATED` |

## 5. Closed source findings

### C-001 — Silent missing-key verification

**Closed in source.** Full signature verification now reports missing verification keys as failure. Hash-only operation is an explicit separate mode.

### C-002 — Duplicate event IDs

**Closed in source.** Append and verification reject/report duplicate IDs.

### C-003 — Authorization/approval signatures not enforced at decision time

**Closed in source.** Signed records are reconstructed and verified with key bindings and current policy.

### C-004 — Declared but unenforced dual approval

**Closed in source.** Designated actions require two distinct valid approvers.

### C-005 — Operational API bypassed governance

**Closed in source.** API writes authenticate the acting agent and then cross the governed service before canonical append.

### C-006 — Partial delegation-scope enforcement

**Closed in source.** Task/resource/action/time/geography/tool/model/provider/depth are evaluated; nested child scopes cannot widen parents; complete lineage is verified.

### C-007 — PostgreSQL batch sequence ambiguity

**Closed in source.** Database BIGSERIAL is the sequence authority; batch appends do not restart client sequence values.

### C-008 — WAL corruption could be skipped/truncated

**Closed in source.** Corrupt replay fails closed and preserves a quarantine copy.

### C-009 — Parallel verification flag did not implement parallel verification

**Closed in source.** Signatures can be verified with a bounded thread pool while ordered chain/hash checks remain sequential.

### C-010 — Public-tier tests did not prove projection/redaction

**Closed in source.** Public projection is a reviewed allow-list; non-public event enumeration, public key scope, public registry attributes, and aggregate verification response have dedicated negative tests.

### C-011 — Weak mutation/attack assertions

**Closed in source.** New tests check signature-preserving tamper cases, duplicate IDs, deletion/reordering, governance bypass, state alias mutation, WAL corruption, replay, exact-approval retargeting, and missing verification keys.

### C-012 — Canonical history/state exposed through mutable aliases

**Found and closed during reconciliation.** Canonical ledger, registry, key, authorization, approval, and delegation service reads now return isolated snapshots.

### C-013 — Approval bound only to action class

**Found and closed during reconciliation.** Approval records now require `action_digest`, a SHA-256 commitment to the exact canonical action intent. Governed events carry the corresponding `action_intent_digest`. Resource or visibility changes invalidate the approval.

### C-014 — Remote identifier knowledge could reach server-held signing path

**Found and closed during reconciliation.** HTTP writes require agent proof-of-possession using a deterministic signed request plus timestamp/nonce checks before governance evaluation.

## 6. Remaining high-assurance deployment dependencies

These are retained as requirements/capabilities, not removed:

1. **Shared durable anti-replay state*** — process-local nonce state demonstrates the contract; replicas/restarts require a shared durable store.
2. **Distributed transaction semantics*** — in-process locking serializes approval selection/event append/consumption; multi-node production requires equivalent distributed transactional guarantees.
3. **External approver entitlement source*** — cryptographic approver identity is enforced; organization-specific roles/entitlements require the organization's IAM/governance source.
4. **Production bootstrap/root authority*** — deployment-specific initialization/administrative trust must be documented and controlled.
5. **HSM/KMS, PostgreSQL, OTLP, PQC, remote anchoring, federation, regulator vaults*** — require their actual external environments and validation.
6. **External review/certification/adoption*** — cannot be created by repository source changes.

## 7. Test-source additions in this reconciliation

Material source-level test additions/rewrites include:

- authorization exact-digest and dual-approval tests;
- full delegation-scope and nested-lineage tests;
- governed execution boundary tests;
- authenticated/replay-resistant API tests;
- strict public disclosure/privacy tests;
- adversarial security tests replacing shallow proxies;
- canonical state-isolation tests;
- WAL corruption/mutation/parallel-verification tests;
- authorization/approval schema conformance tests;
- strengthened general conformance tests.

No pass count is assigned to these additions until executed.

## 8. Schema reconciliation

Current branch schema changes include:

- explicit bounded authorization scope;
- `parent_delegation_id` and stricter delegation schema;
- governance/event fields including approval sets, delegation chain, scope context, governance mode, denial reason, and exact action-intent digest;
- new `approval.schema.json` with required exact-action digest and single-use state.

Current branch inventory: **15 schemas**. Historical validated baseline: **14 schemas**.

## 9. Validation gate required before new verified baseline

Before merge/release as a new validated state:

1. review complete branch diff;
2. run Ruff as a hard gate;
3. run MyPy as a hard gate;
4. run unit tests;
5. run integration tests;
6. run security tests;
7. run privacy tests;
8. run permanence tests;
9. run conformance tests;
10. run governed demo;
11. run full `verify --keys` against generated public keys;
12. run negative cases for missing keys, stale/replayed API request, wrong action digest, corrupted WAL, duplicate IDs, delegation widening, and public-data leakage;
13. exercise optional/live integrations only in appropriate configured environments;
14. compile paper/release derivatives when producing a new release artifact;
15. create a **new** validation report/checksum set rather than overwriting 2026-08-02 historical evidence.

None of those execution steps is claimed as completed by this static audit.

## 10. Decision

**Source-level hardening goals identified in the reconciliation pass are now closed in the branch. The branch is not yet a new validated release.**

`main` remains the historical public baseline until the user authorizes the next repository action and the required validation evidence exists.

> `*` TARGET/high-assurance dependency: required capability remains in the architecture but live completion or validation depends on external infrastructure, deployment topology, hardware/runtime, institutional authority, or independent assurance.
