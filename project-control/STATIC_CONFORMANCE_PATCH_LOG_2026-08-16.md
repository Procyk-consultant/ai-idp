---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/STATIC_CONFORMANCE_PATCH_LOG_2026-08-16.md
Title: Static Conformance Patch Log — 2026-08-16
Version: 2.0.0-reconciliation
Status: Applied to reconciliation branch / Not Runtime-Revalidated
Branch: reconcile-2026-08-14
Baseline Commit: b13e51baa51c9e2bb0a5bff4f3911a6902b51206
---

# Static Conformance Patch Log — 2026-08-16

This log records code/document changes applied after the initial static audit in `STATIC_CONFORMANCE_AUDIT_2026-08-16.md`. It supersedes an audit finding only where explicitly stated below. No test or compilation result is implied by an applied static patch.

## Applied hardening

### P-001 — Verify-only public key registry

**Files:** `src/aegistrace/identity/keys.py`, `src/aegistrace/cli/admin.py`, `src/aegistrace/cli/verify.py`

- Added verify-only public-key registration without private material.
- Added public verification-key registry export.
- Demo now emits `public_keys.json` alongside `ledger.jsonl`.
- Full CLI verification now has an actual public-key input path.

**Supersedes audit finding:** C-001 implementation gap -> `HARDENED-UNVALIDATED`.

### P-002 — Strict ledger verification and event-ID uniqueness

**File:** `src/aegistrace/ledger/append_only.py`

- Unknown signing keys are verification failures when signature verification is requested.
- Hash-only verification is an explicit mode rather than a silent fallback.
- Duplicate event identifiers are rejected on append and reported by the verifier.
- Verification report records verification mode and verified-signature count.

**Supersedes audit findings:** C-001, C-002 -> `HARDENED-UNVALIDATED`.

### P-003 — Signed authorization and approval enforcement

**File:** `src/aegistrace/authorization/engine.py`

- Authorization signatures are revalidated before policy decisions.
- Approval signatures are revalidated before use/evaluation.
- Signer binding to principal/controller or approver/controller is enforced.
- Stale policy versions are rejected.
- Designated dual-approval actions require two valid approvals from distinct approvers.
- Existing single-approval call shape remains accepted for non-dual actions.

**Supersedes audit findings:** C-003, C-004 -> `HARDENED-UNVALIDATED`.

### P-004 — Fail-closed WAL recovery

**File:** `src/aegistrace/ledger/batched.py`

- Corrupt/malformed/chain-invalid WAL replay no longer silently skips entries.
- Corrupt WAL is copied to a timestamped quarantine artifact.
- Recovery raises `WALRecoveryError` rather than discarding evidence.
- Successful recovery retains the WAL rather than truncating the only durable recovery log.
- Flush callback failures are no longer silently swallowed in foreground `flush()`.

**Supersedes audit finding:** C-008 -> `HARDENED-UNVALIDATED`.

**Remaining target:** `parallel_verify` remains a declared optimization target; correctness still uses the canonical strict verifier.

### P-005 — PostgreSQL-owned event sequencing and JSONB normalization

**File:** `src/aegistrace/storage/postgres.py`

- PostgreSQL `BIGSERIAL` is now the authoritative sequence source.
- Batch inserts no longer restart process-local sequence numbering.
- A unique sequence index makes ambiguous ordering fail visibly.
- Single-event append returns the database-assigned sequence.
- JSONB reads accept psycopg2-decoded dictionary payloads as well as textual JSON.

**Supersedes audit finding:** C-007 -> `HARDENED-UNVALIDATED`.

### P-006 — Stronger future CI gate

**File:** `.github/workflows/ci.yml`

- Future CI installs `[test-full]` rather than only `[dev]`.
- MyPy is no longer bypassed with `|| true`.
- Workflow receives read-only contents permission, concurrency control and timeout.

**Important:** the workflow has not been run after this edit. The existing GitHub billing-blocked result remains unrelated to these branch changes.

### P-007 — Public documentation reconciliation

**Files include:** `README.md`, `PRIVACY.md`, `LIMITATIONS.md`, `spec/AI-IDP-CANADA.md`, `release/VALIDATION_REPORT.md`, `project-control/VALIDATION_STATUS.md`, `project-control/SOURCE_GAP_REGISTER.md`, `research/synthesis/INDIGENOUS_DATA_GOVERNANCE_ANALYSIS.md`.

- Preserved AI-IDP as the proposed high-assurance Canadian standard and AegisTrace as its reference implementation.
- Preserved strong L1-L4 intent and target capabilities.
- Added `*` notation for advanced capabilities where external activation/runtime/hardware/credentials are still required.
- Preserved 113/113 as the last executed validation result from 2026-08-02, not as a claim for the changed branch.
- Separated GitHub billing-blocked CI from code/compile status.
- Replaced universal Indigenous consultation gating with context-specific rights-holder engagement where Indigenous rights/data/governance are materially implicated.
- Corrected stale statements that OpenTelemetry/PQC did not exist and that the project was local-only despite GitHub/Zenodo publication.

## Remaining high-priority gaps

The following are not closed by this patch log:

1. **Governance enforcement boundary:** `EventCollector` and FastAPI ingestion still need explicit resolution/enforcement of authorization, delegation and approval objects before governed actions are accepted as authorized canonical operations.
2. **Delegation depth/full scope:** geography/tool/model/provider/depth constraints need full runtime enforcement.
3. **Public-tier projection:** visibility labels exist, but a concrete redacted public projection plus negative leakage tests should be added.
4. **HSM/KMS live signing*:** interfaces exist; real PKCS#11/cloud signing completion and target-environment validation remain.
5. **PQC live signing*:** migration architecture exists; external PQC runtime and completed sign/verify path remain.
6. **Parallel verification*:** optimization flag exists; parallel signature verification is not yet the active implementation.
7. **Test depth:** several historical tests need stronger assertions to map every normative invariant to executable adversarial evidence.
8. **Affected tests:** source tests must be updated to reflect strict `verify --keys`, dual-approval and fail-closed recovery contracts before the next run.

## Validation status

**No tests or compilation were executed while applying these patches.**

The branch must pass a fresh controlled validation before any of the above patches are labelled `VERIFIED`. Until then they remain `HARDENED-UNVALIDATED` or `TARGET*` as applicable.
