---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/STATIC_CONFORMANCE_PATCH_LOG_2026-08-17.md
Title: Static Conformance Patch Log — 2026-08-17
Version: 2.0.0-reconciliation
Status: Source Changes Complete / Unvalidated
Branch: reconcile-2026-08-14
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Static Conformance Patch Log — 2026-08-17

Every item below is a **source change**, not a fresh runtime-validation claim.

| ID | Area | Source change | Validation state |
|---|---|---|---|
| P-001 | Verification | Full signature verification fails on missing keys; hash-only mode explicit | UNVALIDATED SOURCE CHANGE |
| P-002 | Public keys | Verify-only public key import/export; public export can be scoped and omit bindings | UNVALIDATED SOURCE CHANGE |
| P-003 | Ledger | Duplicate event IDs rejected/reported | UNVALIDATED SOURCE CHANGE |
| P-004 | Ledger immutability | Deep-copy canonical events; reads return snapshots | UNVALIDATED SOURCE CHANGE |
| P-005 | Registry isolation | Registry reads/returns no longer expose mutable canonical aliases | UNVALIDATED SOURCE CHANGE |
| P-006 | Key isolation | Key lifecycle records returned as snapshots | UNVALIDATED SOURCE CHANGE |
| P-007 | Authority isolation | Authorization/approval/delegation records returned as snapshots | UNVALIDATED SOURCE CHANGE |
| P-008 | Authorization | Signature, issuer binding, policy version, state/expiry verification | UNVALIDATED SOURCE CHANGE |
| P-009 | Scope | Fail-closed action/task/resource/time/geography/tool/model/provider/depth evaluation | UNVALIDATED SOURCE CHANGE |
| P-010 | Approval | Approver-bound signatures and single-use consumption | UNVALIDATED SOURCE CHANGE |
| P-011 | Exact approval | SHA-256 action-intent digest binds material action facts including visibility | UNVALIDATED SOURCE CHANGE |
| P-012 | Dual approval | Two distinct approvers required for designated actions and same exact intent | UNVALIDATED SOURCE CHANGE |
| P-013 | Delegation | Parent-delegation link, child-scope subset, depth consumption, recursive lineage, cycle protection | UNVALIDATED SOURCE CHANGE |
| P-014 | Governance boundary | GovernedEventService enforces registry/authority/scope/delegation/approval before append | UNVALIDATED SOURCE CHANGE |
| P-015 | Denial evidence | Governance rejection remains deny; optional signed DENY evidence records intent/reason | UNVALIDATED SOURCE CHANGE |
| P-016 | API authentication | Agent proof-of-possession, request timestamp and nonce replay resistance | UNVALIDATED SOURCE CHANGE |
| P-017 | API public safety | Public event projection only; non-public event lookups non-enumerating | UNVALIDATED SOURCE CHANGE |
| P-018 | Public registry | Explicit public flag plus reviewed public_attributes projection | UNVALIDATED SOURCE CHANGE |
| P-019 | Public verification | Public key endpoint limited to keys used by public events, no private bindings by default | UNVALIDATED SOURCE CHANGE |
| P-020 | Verification endpoint | Public verify response reduced to aggregate status/count/mode | UNVALIDATED SOURCE CHANGE |
| P-021 | Parallel verification | Ordered chain/hash checks plus optional thread-pooled signature checks | UNVALIDATED SOURCE CHANGE |
| P-022 | Batched ledger | Candidate validation before WAL/buffer; buffered event alias isolation | UNVALIDATED SOURCE CHANGE |
| P-023 | WAL recovery | Corruption fails closed and quarantine evidence is preserved | UNVALIDATED SOURCE CHANGE |
| P-024 | Background flush | Persistent background errors surfaced instead of silently ignored | UNVALIDATED SOURCE CHANGE |
| P-025 | PostgreSQL* | Database-owned sequence semantics and JSONB decode handling hardened | UNVALIDATED SOURCE CHANGE |
| P-026 | CI | test-full dependencies, hard MyPy gate, timeout/concurrency/minimal permissions | DEFINITION UPDATED / NOT RERUN |
| P-027 | Schemas | Authorization scope and delegation/event governance schemas hardened | UNVALIDATED SOURCE CHANGE |
| P-028 | Approval schema | New exact-action `approval.schema.json`; current branch schema count 15 | UNVALIDATED SOURCE CHANGE |
| P-029 | Security tests | Replaced shallow mutation/tamper proxies with adversarial assertions | TEST SOURCE ADDED / NOT RUN |
| P-030 | Privacy tests | Real public projection, key scope, registry projection and non-enumeration assertions | TEST SOURCE ADDED / NOT RUN |
| P-031 | API tests | Proof-of-possession, replay, auth denial, disclosure boundary tests | TEST SOURCE ADDED / NOT RUN |
| P-032 | WAL tests | Real WAL creation, validate-before-write, corruption quarantine, replay, parallel verify | TEST SOURCE ADDED / NOT RUN |
| P-033 | State isolation tests | Key/registry/delegation alias-resistance assertions | TEST SOURCE ADDED / NOT RUN |
| P-034 | Conformance tests | Full schema event validation, missing-key failure, parallel verification, immutable snapshots | TEST SOURCE ADDED / NOT RUN |
| P-035 | Authority schema tests | Authorization/approval objects validated against normative schemas | TEST SOURCE ADDED / NOT RUN |
| P-036 | Specs | Authorization/approval/delegation/event/disclosure/core/conformance docs aligned to runtime model | STATIC RECONCILIATION |
| P-037 | README/dev docs | Governed vs evidence-only path, exact approvals, public projection, validation state documented | STATIC RECONCILIATION |
| P-038 | Privacy/limitations | Deployment dependencies and public/private boundaries explicitly reconciled | STATIC RECONCILIATION |

## High-assurance capabilities retained with `*`

The patch set does not delete the intended production/high-assurance destination. PostgreSQL production deployment, HSM/KMS, OTLP, live PQC, credentialed remote anchoring, shared durable anti-replay state, distributed transactional enforcement, federation/regulator infrastructure, and independent certification/adoption remain explicit `TARGET*` requirements/capabilities where applicable.

## Historical validation boundary

The recorded 113/113 result remains evidence for the 2026-08-02 baseline only. No current row in this patch log is promoted to `TESTED` or `VALIDATED` until the controlled validation gate is executed against the current branch.
