---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
Secondary Contact: p.1o9.cognitive@outlook.com
Telephone:
Location: Saguenay, Québec, Canada
File: spec/APPROVAL_PROTOCOL.md
Title: Approval Protocol
Purpose: Define exact-action, signed, entitled, single-use approvals
Audience: Architects, implementers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready / reconciliation hardening
Last Material Revision: 2026-08-17
Dependencies: AUTHORIZATION_PROTOCOL.md; EVENT_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Approvals are exact-action, signed, bounded, entitled, and single-use
Failure Behaviour: Missing, mismatched, expired, replayed, unentitled, or unverifiable approvals are rejected
Trace Policy: Approval identity, intent, entitlement, and consumption evidence are traceable
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Approval Protocol

## 1. Purpose

Some authorized action classes require a separate approval before execution. An authorization grants bounded authority; an approval confirms a **specific proposed action intent** within that authority.

An approval is not a reusable permission for an action verb such as `PUBLISH` or `DESTROY_KEY`. It is a signed, single-use record bound to the canonical digest of the exact action proposed and issued only by an entitled approver.

## 2. Approval Record

A canonical approval record contains:

- `approval_id` — permanently unique approval identifier;
- `action` — canonical action class;
- `action_digest` — SHA-256 commitment to the exact canonical proposed-action intent;
- `approver_id` — approving principal;
- `authorization_id` — authorization under which approval is granted;
- `policy_version` — applicable policy version;
- `approved_at` — issuance timestamp;
- `expires_at` — optional expiry;
- `used` — single-use state;
- `used_at` — consumption timestamp where applicable;
- `signature` — Ed25519 signature over the canonical approval record;
- `signing_key_id` — key bound to the actual approver.

The normative JSON representation is defined by `schemas/approval.schema.json`.

## 3. Exact Action Intent

`action_digest` is computed from deterministic canonical JSON describing the proposed action. Bound facts include, where present:

- accountable controller;
- principal;
- persistent agent;
- runtime agent instance;
- provider, model, model version, and deployment;
- task;
- action class;
- **disclosure/visibility tier**;
- jurisdiction;
- delegation reference;
- resource target;
- before/after digests;
- relevant evaluated scope context.

The digest prevents retargeting. Approval to publish resource `A` does not authorize resource `B`; approval for `ORGANIZATION_PRIVATE` evidence does not authorize changing the same material action to `PUBLIC` visibility.

The reference implementation is `authorization/intent.py`.

## 4. Approver Entitlement

Cryptographic possession of a principal-bound key is necessary but is not sufficient to become an approver.

Before an approval can be issued or verified, policy must establish that `approver_id` is entitled to approve the action class under the applicable authorization context.

AegisTrace provides a pluggable `ApproverEntitlementProvider` contract:

- **fail-closed default:** only the authorization principal is entitled;
- **static explicit grants:** reference/test deployments can bind named approvers to action classes;
- **composite policy:** multiple approved entitlement sources can be combined;
- **external IAM/directory adapter:** production organizations may implement the same contract against their approved identity/role system.*

An unentitled approver is rejected even if its signature and signing key are otherwise cryptographically valid.

## 5. Operations

### 5.1 Request

When policy identifies an approval-gated action:

1. assemble the complete proposed action intent;
2. canonicalize it deterministically;
3. calculate `action_digest`;
4. present the action and material context to an entitled approver.

### 5.2 Issue

1. Verify the underlying authorization.
2. Verify approver entitlement for the action.
3. Verify that the signing key is active and bound to `approver_id`.
4. Create the approval with the exact `action_digest`.
5. Sign the canonical approval record.
6. Retain the approval as authority evidence.

A controller-bound key cannot masquerade as a different approver merely because the controller issued the authorization.

### 5.3 Verify

An approval is usable only if:

1. the record exists;
2. the underlying authorization remains valid;
3. the approval is unused and unexpired;
4. the shared consumption store reports it available;
5. policy version is current;
6. action class matches;
7. `action_digest` exactly matches the proposed action intent;
8. authorization ID matches;
9. the principal remains entitled to approve the action;
10. signing key is bound to the approver;
11. signature verifies.

Any mismatch or unavailable authoritative security state is a denial.

### 5.4 Consume

On successful governed acceptance:

1. the accepted event records approval identifier(s) and `action_intent_digest`;
2. all selected approvals are consumed atomically or none are consumed;
3. `used_at` is recorded;
4. reuse is rejected.

AegisTrace provides an `ApprovalConsumptionStore` contract with:

- process-local reference implementation;
- durable SQLite implementation;
- shared PostgreSQL implementation using database uniqueness/transactions for all-or-none consumption across clients.

The PostgreSQL path supplies the source mechanism required for shared single-use approval consumption in multi-process deployments. A complete distributed deployment must also use appropriately shared authoritative authorization/registry/delegation state and deployment-level transaction boundaries.*

### 5.5 Revoke

Explicit pre-use approval revocation remains a future lifecycle extension unless represented as an authorized signed state transition. Absence or local deletion must never be treated as evidence of revocation.

## 6. Dual Approval

Policy-designated actions require two valid approvals from **distinct entitled approvers**. Both approvals must:

- reference the same authorization;
- reference the same action class;
- carry the same exact `action_digest`;
- remain unused and valid;
- pass entitlement policy independently;
- have independently valid approver-bound signatures.

The current reference dual-approval set includes designated high-impact classes such as cryptographic-key destruction, production modification, and database-schema alteration. Normative policy may impose stricter requirements by context or conformance level.

## 7. Replay and Concurrency

Approval single-use is an authorization invariant, not a UI hint. High-assurance deployments must prevent two concurrent requests from consuming the same approval successfully.

The reference PostgreSQL consumption store uses a unique approval identifier and a single transaction so a conflicting second consumption fails rather than silently succeeding.

## 8. Invariants

- Approvals are bound to exact action intents.
- Visibility is part of the exact action intent.
- A change in a bound action fact requires a different digest and a new approval.
- Approvers must be entitled by policy.
- Approvals are single-use.
- Concurrent/replayed approval consumption is rejected.
- Expired approvals are rejected.
- Approver signatures are verified.
- Approval signing keys are bound to the actual approver.
- Dual approval requires two distinct entitled approvers of the same exact intent.
- Approval evidence remains reconstructable after use.

> `*` External organizational IAM, shared multi-service state deployment, institutional role governance, and target-environment validation remain deployment dependencies. The AegisTrace source provides the entitlement and atomic-consumption contracts without claiming a particular organization has configured those external systems.
