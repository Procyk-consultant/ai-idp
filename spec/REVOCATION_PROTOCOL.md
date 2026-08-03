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
File: spec/REVOCATION_PROTOCOL.md
Title: Revocation Protocol
Purpose: Define how identifiers, keys, agents, and authorizations are revoked
Audience: Architects, implementers, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: IDENTITY_LIFECYCLE.md; PERMANENT_RECORD_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Revocation preserves history
Failure Behaviour: History-erasing revocation is forbidden
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Revocation Protocol

## 1. Revocable Entities

The following may be revoked:

- Identifiers (permanent; revocation marks the entity as revoked but the identifier remains resolvable)
- Signing keys
- Persistent agents
- Agent instances
- Delegations
- Authorizations
- Approvals
- Certifications

## 2. Revocation Record

A revocation record contains:

- `revocation_id` — unique identifier.
- `revoked_record_id` — the revoked record's identifier.
- `revocation_reason` — the reason for the revocation.
- `revoking_principal_id` — the principal revoking.
- `revoked_at` — revocation timestamp.
- `effective_at` — effective timestamp (may be retroactive in rare cases).
- `signature` — cryptographic signature by the revoking principal.

## 3. Revocation Authority

Revocation authority is defined by policy:

- **Controller** — may revoke their own agents, keys, delegations, authorizations, approvals.
- **Regulator** — may revoke any entity for cause (e.g., non-compliance, fraud).
- **Court** — may revoke any entity under judicial authority.
- **Certification body** — may revoke certifications.
- **Principal** — may revoke their own authorizations and approvals.

## 4. Revocation Operations

### 4.1 Issue

A revocation is issued by an authorized principal. The revocation is recorded as a signed event in the ledger.

### 4.2 Verify

A revocation is verified by:

1. The revocation record exists.
2. The revoking principal is authorized.
3. The signature is valid.
4. The revocation is in effect (the effective timestamp has passed).

### 4.3 Propagate

Revocation is propagated to dependent entities:

- Revoking a signing key invalidates new signatures by that key.
- Revoking a delegation invalidates new actions by the child agent under that delegation.
- Revoking an authorization invalidates new actions under that authorization.
- Revoking an approval invalidates the use of that approval.
- Revoking a persistent agent invalidates new actions by any instance of that agent.
- Revoking a certification invalidates the conformity claim.

## 5. Historical Preservation

Revocation preserves historical records. Events signed by a now-revoked key remain verifiable (the key was valid at the time of signing). Actions taken under a now-revoked delegation remain verifiable. The historical ledger is unchanged.

## 6. Invariants

- Revocation is a new signed event.
- Revocation preserves historical records.
- Revocation propagates to dependent entities.
- Revoked entities cannot produce new valid events.
- Historical signatures remain verifiable.
