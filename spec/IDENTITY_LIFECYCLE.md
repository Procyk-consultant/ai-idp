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
File: spec/IDENTITY_LIFECYCLE.md
Title: Identity Lifecycle
Purpose: Define lifecycle operations on AI Actor identifiers
Audience: Architects, implementers, registry operators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: IDENTITY_PROTOCOL.md; REVOCATION_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Lifecycle operations preserve history
Failure Behaviour: History-erasing lifecycle operations are forbidden
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Identity Lifecycle

## 1. States

An AI Actor identifier transitions through the following states:

- **Proposed** — the entity has been proposed but not yet registered.
- **Active** — the entity is registered and operational.
- **Suspended** — the entity is temporarily inactive (e.g., under investigation).
- **Revoked** — the entity is permanently inactive (e.g., for cause).
- **Terminated** — the entity has been terminated by the controller.
- **Archived** — the entity is no longer active but the identifier remains resolvable.

State transitions are signed events. Historical states are preserved.

## 2. Lifecycle Operations

### 2.1 Creation

- A new identifier is minted by the identity issuer.
- The initial state is `Active`.
- The creation event records the entity's initial attributes and bindings.

### 2.2 Update

- Attributes may be updated by appending update events.
- Prior attributes are preserved in the ledger.
- Critical attributes (controller, signing key) require dual authorization for updates.

### 2.3 Suspension

- An entity may be suspended by an authorized principal (e.g., a regulator, an incident coordinator, or the controller).
- Suspension is reversible.
- Suspended entities cannot perform new actions.

### 2.4 Revocation

- An entity may be revoked by an authorized principal.
- Revocation is permanent.
- Revoked entities cannot perform new actions.
- Historical records are preserved.
- The revocation event records the reason, the revoking principal, and the timestamp.

### 2.5 Termination

- An entity may be terminated by its controller.
- Termination is permanent.
- Terminated entities cannot perform new actions.
- Historical records are preserved.
- The permanent identifier remains resolvable.

### 2.6 Reactivation

- Suspended entities may be reactivated by an authorized principal.
- Revoked or terminated entities cannot be reactivated.
- Reactivation is a new signed event.

### 2.7 Archival

- Terminated entities may be archived after a defined retention period.
- Archived entities remain resolvable but with reduced attributes (e.g., no signing key, no current controller).
- The permanent identifier remains resolvable indefinitely.

## 3. Key Lifecycle

Keys have a parallel lifecycle:

- **Created** — a new key is created and bound to an entity.
- **Active** — the key is used to sign events.
- **Rotated** — a new key is created; the old key is rotated out (but not destroyed).
- **Suspended** — the key may be suspended (temporary).
- **Revoked** — the key is revoked (permanent). Revoked keys cannot produce valid new events.
- **Terminated** — the key is terminated. Historical signatures remain verifiable.

Key rotation produces a new key-binding event. The old key remains in the registry, marked as rotated, with its end-of-active date recorded.

## 4. Permanent Identifier Preservation

Permanent identifiers are preserved across:

- **Provider switches** — the persistent agent's identifier is unchanged; the execution context is updated.
- **Model switches** — the persistent agent's identifier is unchanged; the execution context is updated.
- **Deployment switches** — the persistent agent's identifier is unchanged; the execution context is updated.
- **Tool switches** — the persistent agent's identifier is unchanged; the tool binding is updated.
- **Environment switches** — the persistent agent's identifier is unchanged; the environment is updated.
- **Organizational restructuring** — the controller is updated via a controller-change event; the persistent agent's identifier is unchanged.
- **Repository transfer** — the repository reference is updated; the persistent agent's identifier is unchanged.

## 5. Event Recording

Every lifecycle operation is recorded as a signed event in the ledger. The event includes:

- The entity identifier.
- The operation (CREATE, UPDATE, SUSPEND, REVOKE, TERMINATE, REACTIVATE, ARCHIVE, ROTATE_KEY, etc.).
- The principal authorizing the operation.
- The controller accountable for the entity.
- The timestamp.
- The reason (for revocation, termination, suspension).
- The previous-event hash and event hash.
- The signature.

## 6. Invariants

- An identifier is never reassigned to a different entity.
- An identifier is never reused.
- A revoked or terminated identifier remains resolvable.
- A historical event remains verifiable after the entity is revoked or terminated.
- A key rotation does not invalidate prior signatures.
- A controller change does not invalidate prior events.
