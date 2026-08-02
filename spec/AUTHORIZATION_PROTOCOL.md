---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
Secondary Contact: p.1o9.cognitive@outlook.com
Telephone: +1 (581) 668-2372
Location: Saguenay, Québec, Canada
File: spec/AUTHORIZATION_PROTOCOL.md
Title: Authorization Protocol
Purpose: Define how authorizations are issued, verified, and enforced
Audience: Architects, implementers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: DELEGATION_PROTOCOL.md; APPROVAL_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Every action resolves to an authorization
Failure Behaviour: Unauthorized actions are rejected
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Authorization Protocol

## 1. Purpose

Authorization is the record that a principal has authorized a specific action or class of actions, subject to policy. Every action resolves to an authorization.

## 2. Authorization Record

An authorization record contains:

- `authorization_id` — unique identifier.
- `principal_id` — the principal authorizing the action.
- `controller_id` — the controller accountable for the action.
- `agent_id` — the agent authorized to perform the action.
- `task_id` — the task for which the authorization is granted.
- `delegation_id` — the delegation (if the action is delegated).
- `scope` — the bounded scope of the authorization (action classes, resource classes, time bounds).
- `policy_version` — the policy version under which the authorization is evaluated.
- `issued_at` — issuance timestamp.
- `expires_at` — optional expiry timestamp.
- `signature` — cryptographic signature by the principal (or the principal's authorized signer).

## 3. Authorization Operations

### 3.1 Issue

An authorization is issued by:

1. The principal (or their authorized signer) submits an authorization request.
2. The authorization service validates the request.
3. The authorization is recorded as a signed event in the ledger.

### 3.2 Verify

An authorization is verified by:

1. The authorization record exists in the ledger.
2. The authorization is in an active state (not revoked, not expired).
3. The authorization's scope encompasses the proposed action.
4. The principal is authorized.
5. The signature is valid.
6. The policy version is current.

### 3.3 Revoke

An authorization may be revoked by the principal (or their authorized signer). Revocation is a new signed event.

### 3.4 Expire

An authorization with `expires_at` automatically expires. Expiry is a new signed event.

## 4. Policy Engine

The policy engine evaluates authorization requests against the current policy. Policy includes:

- **Action policies** — which actions are permitted, denied, or require approval.
- **Resource policies** — which resources may be accessed, modified, or deleted.
- **Principal policies** — which principals may authorize which actions.
- **Controller policies** — which controllers are accountable for which agents.
- **Delegation policies** — delegation depth, scope, and revocation rules.
- **Approval policies** — which actions require human approval, dual approval, or regulator-visible evidence.
- **Visibility policies** — which events are public, controlled, organization-private, or sealed.
- **Retention policies** — how long events and evidence are retained.
- **Conformance policies** — conformance level requirements per context.

Policies have versions. The policy version is recorded in every authorization and event.

## 5. Approval

Some actions require approval before they can be executed. Approvals are single-use records. The approval protocol is defined in `APPROVAL_PROTOCOL.md`. Actions requiring approval include:

- High-impact automated decisions (per the AIA).
- Production deployments.
- Destructive actions (DELETE, DESTROY_RESOURCE, DESTROY_KEY).
- Privilege changes (CHANGE_PERMISSION, CHANGE_POLICY).
- Cross-organization delegations.
- External effects (TRIGGER_EXTERNAL_EFFECT, PUBLISH, DEPLOY, RELEASE).

## 6. Enforcement

The authorization engine enforces authorizations before any action:

1. The agent requests to perform an action.
2. The authorization engine retrieves the authorization record.
3. The engine verifies the authorization (per Section 3.2).
4. The engine verifies the delegation (if applicable).
5. The engine evaluates the policy.
6. The engine checks for required approvals.
7. If all checks pass, the action is permitted; otherwise, it is denied.

Denied actions are recorded as DENY events.

## 7. Fail-Closed

For high-risk actions (per policy), the engine fails closed: if any check fails or is inconclusive, the action is denied. Fail-closed actions include:

- Production deployments
- Destructive actions
- Privilege changes
- Cross-organization delegations
- External effects
- Database schema changes
- Infrastructure modifications

## 8. Invariants

- Every action resolves to an authorization.
- An authorization's scope is enforced.
- A revoked or expired authorization produces no new valid actions.
- Policy violations are denied and recorded.
- Fail-closed actions are denied if any check is inconclusive.
