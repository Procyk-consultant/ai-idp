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
Purpose: Define exact-action, signed, single-use approvals
Audience: Architects, implementers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready / reconciliation hardening
Last Material Revision: 2026-08-17
Dependencies: AUTHORIZATION_PROTOCOL.md; EVENT_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Approvals are exact-action, signed, bounded, and single-use
Failure Behaviour: Missing, mismatched, expired, replayed, or unverifiable approvals are rejected
Trace Policy: Approval identity and consumption evidence are traceable
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Approval Protocol

## 1. Purpose

Some authorized action classes require a separate approval before execution. An authorization grants bounded authority; an approval confirms a **specific proposed action intent** within that authority.

An approval is therefore not a reusable permission for an action verb such as `PUBLISH` or `DESTROY_KEY`. It is a signed, single-use record bound to the canonical digest of the action actually proposed.

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
- disclosure/visibility tier;
- jurisdiction;
- delegation reference;
- resource target;
- before/after digests;
- relevant evaluated scope context.

The digest prevents retargeting. For example, approval to publish resource `A` does not authorize publishing resource `B`; approval for organization-private evidence does not silently authorize changing the same operation to `PUBLIC` visibility.

## 4. Operations

### 4.1 Request

When policy identifies an approval-gated action:

1. assemble the complete proposed action intent;
2. canonicalize it deterministically;
3. calculate `action_digest`;
4. present the proposed action and its material context to the approver.

### 4.2 Issue

1. The approver reviews the exact proposed intent.
2. The approval service verifies the underlying authorization.
3. The approval service verifies that the signing key is active and bound to `approver_id`.
4. The approval record is created with the exact `action_digest`.
5. The approver's signature is verified/stored.
6. The approval is retained as canonical authority evidence.

A controller-bound key cannot masquerade as a different human approver merely because the controller issued the underlying authorization.

### 4.3 Verify

An approval is usable only if:

1. the record exists;
2. the underlying authorization remains valid;
3. the approval is unused and unexpired;
4. policy version is current;
5. action class matches;
6. `action_digest` exactly matches the currently proposed action intent;
7. authorization ID matches;
8. signing key is bound to the approver;
9. signature verifies.

Any mismatch is a denial.

### 4.4 Consume

On successful governed acceptance:

1. the accepted event records the approval identifier(s) and action-intent digest;
2. selected approvals are marked `used=true`;
3. `used_at` is recorded;
4. reuse is rejected.

The AegisTrace reference boundary serializes selection, event append, and consumption in-process. A distributed high-assurance deployment must preserve equivalent transactional semantics across replicas/storage.*

### 4.5 Revoke

A future approval-lifecycle extension may model explicit pre-use revocation as signed append-only evidence. Until such a lifecycle is active in the reference implementation, revocation claims must not be inferred from absence or local deletion.

## 5. Dual Approval

Policy-designated actions require two valid approvals from **distinct approvers**. Both approvals must:

- reference the same authorization;
- reference the same action class;
- carry the same exact `action_digest`;
- remain unused and valid;
- have independently valid approver-bound signatures.

The current reference dual-approval set includes designated high-impact classes such as cryptographic-key destruction, production modification, and database-schema alteration. The normative policy may impose stricter requirements by context or conformance level.

## 6. Approver Authorization

Organizational policy determines which principals may approve which action classes. The reference implementation verifies cryptographic identity and exact-action binding; production deployments must additionally configure the organization's approver-role/entitlement source where required.*

## 7. Invariants

- Approvals are bound to exact action intents.
- A change in a bound action fact requires a different digest and a new approval.
- Approvals are single-use.
- Approval reuse is rejected.
- Expired approvals are rejected.
- Approver signatures are verified.
- Approval signing keys are bound to the actual approver.
- Dual approval requires two distinct approvers of the same exact intent.
- Approval evidence remains reconstructable after use.

> `*` Distributed transaction coordination and external organizational entitlement/identity systems are high-assurance deployment dependencies, not a reduction of the AI-IDP normative requirement.
