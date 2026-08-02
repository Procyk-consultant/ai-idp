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
File: spec/IDENTITY_PROTOCOL.md
Title: Identity Protocol
Purpose: Define how AI Actor identifiers are issued, resolved, and maintained
Audience: Architects, implementers, registry operators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: ACTOR_MODEL.md; IDENTITY_LIFECYCLE.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Identifiers are permanent and unique
Failure Behaviour: Identifier reuse or reassignment is a critical defect
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Identity Protocol

## 1. Identifier Format

AI-IDP identifiers are URIs of the form:

```
aitrace://<jurisdiction>/<entity-type>/<slug>[#<version-or-instance>]
```

- `jurisdiction` — `ca` for Canada. Provincial sub-authorities use `ca-qc`, `ca-on`, etc.
- `entity-type` — `provider`, `model`, `deployment`, `controller`, `principal`, `agent`, `agent-instance`, `task`, `delegation`, `authorization`, `approval`, `resource`, `event`, etc.
- `slug` — a unique, opaque, registry-assigned identifier (e.g., `org-001`, `agent-research-agent`, `run-0042`).
- `version-or-instance` — for versioned entities, the version (e.g., `v3`); for instance entities, the instance identifier.

Examples:

- `aitrace://ca/controller/org-001`
- `aitrace://ca/principal/user-012`
- `aitrace://ca/agent/research-agent#v3`
- `aitrace://ca/agent-instance/research-agent#run-0042`
- `aitrace://ca/task/task-00104`
- `aitrace://ca/event/evt_01JEXAMPLE`

## 2. Identifier Properties

AI-IDP identifiers are:

- **Permanently unique.** Once assigned, an identifier is never assigned to another entity.
- **Never reassigned.** Even after the entity is terminated or revoked, the identifier is not reassigned.
- **Never reused.** The identifier is not reused for any other entity.
- **Resolvable after termination.** The identifier resolves to a record indicating the entity's terminated state.
- **Resolvable after revocation.** The identifier resolves to a record indicating the entity's revoked state and the revocation reason.
- **Resolvable after provider closure.** The identifier resolves to a record maintained by the registry authority.
- **Resolvable after model retirement.** The identifier resolves to a record indicating the model's retired state.
- **Resolvable after repository transfer.** The identifier resolves to a record indicating the repository's new location or archived state.
- **Resolvable after organizational restructuring.** The identifier resolves to a record indicating the new controller or the entity's dissolved state.

## 3. Identifier Issuance

Identifiers are issued by an identity issuer operating under a registry authority. The issuance process:

1. The requesting entity submits an issuance request with required attributes.
2. The identity issuer validates the request against the schema.
3. The identity issuer verifies the requesting entity's authority (e.g., the controller's authority to register an agent).
4. The identity issuer mints a unique identifier.
5. The identity issuer records the issuance as a signed event in the ledger.
6. The identity issuer returns the identifier to the requesting entity.

## 4. Identifier Resolution

Identifiers are resolvable via:

- **Local resolution** — within an AegisTrace instance, identifiers resolve to local registry records.
- **Federated resolution** — across federated AegisTrace instances, identifiers resolve via the federation protocol.
- **Public resolution** — public identifiers resolve via the public verification repository (e.g., a public API or transparency log).

Resolution returns:

- The entity's current state (active, suspended, revoked, terminated).
- The entity's public attributes (for public tier).
- The entity's signed record (for controlled or organization-private tier, with authorization).
- The entity's sealed attributes (for sealed tier, with judicial or regulator authority).

## 5. Identifier Binding

Identifiers are bound to:

- A **signing key** (for entities that sign events).
- An **accountable controller** (for agents and agent instances).
- A **principal** (for actions; via the authorization chain).
- A **provider, model, version, deployment** (for agent instances).
- A **task** (for actions).
- A **delegation** (for child agents).

Bindings are recorded as events. Binding changes (e.g., key rotation) are new signed events; the prior binding is preserved.

## 6. Privacy and Pseudonymization

User and principal identifiers are pseudonymous by default (`aitrace://ca/principal/user-XXX`). The mapping from a pseudonymous identifier to a real identity is sealed and access-controlled. Public registry entries expose only the pseudonymous form.

## 7. Migration and Interoperability

AI-IDP identifiers may be mapped to:

- **W3C DIDs** — via a `did:aitrace` method (to be specified in a future version).
- **W3C Verifiable Credentials** — identifiers are used as subjects of verifiable credentials.
- **SPIFFE IDs** — for workload identity interop.
- **URLs** — public identifiers resolve to URLs in the public verification repository.

The mapping is documented but does not change the canonical AI-IDP identifier.

## 8. Identifier Verification

Identifiers are verified by:

- **Schema validation** — the identifier matches the URI format.
- **Registry lookup** — the identifier resolves to a registry record.
- **State check** — the entity is in an active state (not revoked or terminated).
- **Binding check** — the identifier's bindings are consistent with the using entity (e.g., a signing event uses a key bound to the signing entity).

Verification is performed by the `aegistrace.cli.verify` CLI and the `aegistrace.verify` Python API.
