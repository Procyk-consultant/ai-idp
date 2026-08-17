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
File: spec/AUTHORIZATION_PROTOCOL.md
Title: Authorization Protocol
Purpose: Define how authorizations are issued, verified, bounded, and enforced
Audience: Architects, implementers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready / reconciliation hardening
Last Material Revision: 2026-08-17
Dependencies: DELEGATION_PROTOCOL.md; APPROVAL_PROTOCOL.md; EVENT_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Every governed action resolves to a valid bounded authorization
Failure Behaviour: Missing, stale, malformed, out-of-scope, or unverifiable authority is denied
Trace Policy: Authorization and denial evidence are first-class trace records
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Authorization Protocol

## 1. Purpose

Authorization is the signed record that a principal, or an authorized signer acting for the principal/controller, grants an AI agent authority to perform a bounded class of actions for a specific task. Every **governed operational action** must resolve to an authorization before canonical acceptance.

AI-IDP distinguishes the operational governance boundary from evidence ingestion. A low-level evidence collector may be used to import or record evidence explicitly, but it is not itself an authorization decision point. A runtime that executes or accepts operational actions as governed actions must cross the authorization boundary first.

## 2. Authorization Record

An authorization contains at least:

- `authorization_id` — permanently unique authorization identifier;
- `principal_id` — principal granting authority;
- `controller_id` — accountable controller;
- `agent_id` — authorized persistent agent;
- `task_id` — task for which authority is granted;
- `delegation_id` — parent delegation where the actor is delegated;
- `scope` — bounded authority dimensions;
- `policy_version` — policy version used for evaluation;
- `state` — active, revoked, or expired;
- `issued_at` and optional `expires_at`;
- `signature` and `signing_key_id`.

The signing key must resolve to the principal or accountable controller authorized to issue the record. A signed record whose key binding, signature, policy version, state, or expiry cannot be verified is invalid.

## 3. Scope Model

Authorization scope may constrain:

- action classes;
- task classes;
- resource classes;
- geographic scope;
- tool classes;
- model classes;
- provider classes;
- time bounds;
- delegation depth.

Scope evaluation is **fail-closed**. If a scope restricts a dimension and the runtime cannot establish the corresponding value, the action is denied rather than treated as unrestricted. Unknown scope fields are non-conformant.

For example, an authorization restricted to provider class `approved-provider` cannot authorize an action if the runtime does not know the provider class or if the actual provider class differs.

## 4. Authorization Operations

### 4.1 Issue

1. Resolve the principal, controller, agent, task, and any parent delegation.
2. Validate the proposed scope and expiry.
3. Verify that the signing key is active and bound to an authorized issuer.
4. Create the authorization identifier.
5. Canonicalize and sign the authorization record.
6. Store the canonical record without exposing mutable aliases to callers.
7. Record issuance in the applicable trace/ledger workflow.

### 4.2 Verify

Verification requires all of the following:

1. the authorization exists;
2. the record is active and unexpired;
3. the record uses the current required policy version;
4. the signing key resolves to an authorized issuer;
5. the cryptographic signature verifies;
6. the controller, principal, agent, task, and delegation bindings match the proposed action;
7. the bounded scope encompasses the proposed action and its runtime context.

A missing or inconclusive check is a denial for fail-closed actions.

### 4.3 Revoke

Revocation changes the authority state for future actions. Historical records remain resolvable. The revocation itself is recorded as new signed evidence rather than rewriting the prior authorization.

### 4.4 Expire

An authorization with `expires_at` cannot authorize a new action after expiry. Expiry does not erase historical evidence.

## 5. Policy Engine

The policy engine evaluates:

- action policies;
- resource policies;
- principal/controller bindings;
- delegation policies;
- approval requirements;
- visibility/disclosure rules;
- retention and conformance policies.

The policy version is carried into authorization and event evidence so later reconstruction can establish which policy governed the decision.

## 6. Approval-Gated Actions

Some action classes require a separate approval. The authorization permits the class of work; the approval authorizes **one exact proposed action intent**. The approval protocol therefore uses a canonical `action_digest` rather than treating the action verb alone as sufficient.

The exact action intent may bind, as applicable:

- controller, principal, agent, and runtime instance;
- provider/model/deployment execution context;
- task;
- action class;
- visibility/disclosure tier;
- jurisdiction;
- delegation reference;
- resource target;
- before/after digests;
- evaluated scope context.

Changing a bound fact changes the digest and invalidates the approval for that changed action.

## 7. Governed Enforcement Sequence

For a governed action, the reference enforcement sequence is:

1. authenticate the submitting actor/request where the action enters through a remote API or similar boundary;
2. resolve active identity and runtime relationships;
3. retrieve and cryptographically verify the authorization;
4. verify exact controller/principal/agent/task/delegation bindings;
5. evaluate all restricted scope dimensions fail-closed;
6. verify the complete delegation chain when applicable;
7. compute the exact canonical action-intent digest;
8. verify the required approval set against that exact digest;
9. append the governed event with the authority/delegation/approval evidence;
10. consume single-use approvals;
11. if denied, record a `DENY` event where denial evidence can itself be safely produced.

## 8. Remote/API Authentication

Authorization IDs and key IDs are not bearer credentials. A remote requester must prove possession of the acting agent's signing key before a server uses server-held signing capability or accepts the operation as authenticated.

The AegisTrace reference API binds a deterministic request payload to an Ed25519 request signature plus a timestamp and nonce. Replayed nonces and stale timestamps are rejected.

A single-process nonce cache demonstrates the contract. **Shared durable anti-replay state across restarts and replicas is a high-assurance deployment requirement*** for distributed production operation.

## 9. Fail-Closed Classes

High-impact classes include production deployment/release, destructive resource or key operations, permission/policy changes, infrastructure/database-schema modification, external effects, publication, and other policy-designated actions. If required evidence, context, approval, or cryptographic verification is unavailable, the decision is deny.

## 10. Invariants

- Every governed action resolves to an authorization.
- Authorization identity/task/controller/principal bindings are exact.
- Restricted scope dimensions are fail-closed.
- A revoked, expired, stale, or unverifiable authorization produces no new valid governed action.
- Approval-gated actions require approval of the exact canonical action intent.
- Denied actions do not become permitted because denial evidence could not be recorded.
- Historical authority evidence remains resolvable after revocation/expiry.
- Remote possession of an identifier alone is not authentication.

> `*` Distributed nonce persistence, external HSM/KMS enforcement, regulator infrastructure, and other production integrations retain the AI-IDP target requirement while depending on deployment-specific infrastructure and validation.
