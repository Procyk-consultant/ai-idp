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
File: spec/FEDERATION_PROTOCOL.md
Title: Federation Protocol
Purpose: Define cryptographically recognized interoperability between registry authorities
Audience: Architects, registry operators, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready / reconciliation hardening
Last Material Revision: 2026-08-17
Dependencies: REGISTRY_PROTOCOL.md; EVENT_PROTOCOL.md; DISCLOSURE_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Federation never weakens identity, authority, disclosure, or verification requirements
Failure Behaviour: Unrecognized, expired, unverifiable, or unavailable federation fails closed and is detectable
Trace Policy: Federation operations and breaks are accountable records
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Federation Protocol

## 1. Purpose

Federation allows independently operated AI-IDP registry authorities to recognize and verify one another without collapsing into a single global trust domain. Federation must preserve the issuing authority, persistent identity, cryptographic evidence, disclosure tier, delegation lineage, and applicable policy context.

The normative target supports bilateral, multilateral, national, sectoral, provincial/territorial, and authorized international federation. **No government, regulator, standards body, or foreign registry is represented as already operating an AI-IDP federation.**

AegisTrace includes a reference federation gateway in `src/aegistrace/federation/` so the protocol can be implemented and tested before institutional adoption.

## 2. Federation Topologies

AI-IDP permits:

- **Bilateral federation** — two registry authorities recognize one another under a signed agreement.
- **Multilateral federation** — multiple authorities recognize one another directly or through an authorized hub.
- **National federation** — a proposed future topology across Canadian authorities where legally/administratively adopted.
- **Sector federation** — authorities scoped to a regulated industry or trust community.
- **International federation** — cross-border recognition where legally and contractually authorized.

Topology does not change the core invariants. Recognition is explicit, bounded, revocable, and attributable.

## 3. Signed Federation Agreement

A federation agreement is a bilateral or multilateral trust instrument specifying at minimum:

- agreement identifier;
- local and remote registry-authority identifiers;
- effective date and optional expiry;
- allowed disclosure tiers;
- verification procedures;
- dispute/incident handling;
- termination/revocation procedure;
- any additional policy metadata;
- signing-key identifiers for the participating authorities;
- cryptographic signatures by the participating authorities.

The AegisTrace reference implementation canonicalizes the agreement and verifies both authority signatures using keys bound to the corresponding authority identifiers before a remote authority can be registered with the gateway.

Missing, invalid, expired, revoked, or incorrectly bound agreement signatures cause federation registration/resolution to fail closed.

## 4. Cross-Registry Public Resolution

A public identifier from a recognized remote registry resolves through this sequence:

1. Verify that an active signed federation agreement exists for the remote authority.
2. Check the bounded local cache.
3. If absent or expired, query the issuing registry's public federation/API surface.
4. Require the returned identifier to match the requested identifier.
5. Reject unreviewed response fields rather than automatically exposing newly added remote fields.
6. Cache only the validated public projection for a bounded TTL.
7. Return the isolated public record.

The current AegisTrace HTTP federation client consumes only public endpoints. Controlled or sealed federation requires an authenticated/authorized organization-specific client and remains subject to `DISCLOSURE_PROTOCOL.md`.

## 5. Cross-Registry Event Verification

For a **fully disclosed** event record, a receiving registry verifies:

1. identifier and signing-key resolution;
2. canonical event hash recomputation;
3. Ed25519 signature using the issuing registry's verification key;
4. `previous_event_hash` continuity for a disclosed chain segment;
5. duplicate event-ID absence;
6. authority/delegation/policy evidence at the disclosure tier available to the receiving party.

`FederationGateway.verify_disclosed_event()` and `verify_disclosed_chain()` implement the cryptographic event/hash-chain portion for disclosed records.

A redacted `PUBLIC` event projection is intentionally treated as an integrity/reference surface and does not reveal enough private canonical fields to reconstruct the full underlying event. Full event signature verification therefore requires the disclosure tier authorized for the verifier, or a separately defined public anchoring/proof mechanism such as signed/Merkle roots.

## 6. Public Verification Keys

The gateway may retrieve an issuing registry's public verification-key registry only under an active federation agreement. Returned key registries must use the supported AegisTrace public-key schema and contain explicit key identifiers and public material.

Key retrieval does not itself grant authority to act; it provides verification material only.

## 7. Cross-Registry Delegation

A cross-registry delegation must preserve:

- parent registry/authority reference;
- child registry/authority reference;
- signed federation agreement reference;
- parent persistent-agent identity;
- child persistent-agent identity;
- principal and accountable controller;
- bounded delegation scope;
- expiry/revocation state;
- signatures required by the applicable cross-organization policy;
- any dual-authorization requirement imposed by AI-IDP conformance/policy.

No federation relationship may widen a delegation beyond the authority possessed by the delegating actor.

## 8. Federation Gateway

The reference `FederationGateway` provides:

- explicit remote-authority registration;
- bilateral signature verification;
- key-to-authority binding verification;
- agreement effective/expiry/revocation enforcement;
- allow-listed public-entity resolution;
- bounded TTL caching;
- public-event projection retrieval;
- public verification-key retrieval;
- remote health checking;
- federation-break records;
- cryptographic verification of fully disclosed events and contiguous chain segments.

The reference `HTTPFederatedRegistryClient` deliberately does not invent government endpoints or credentials. Operators configure the actual approved registry URL and authentication/disclosure mechanism for their deployment.*

## 9. Federation Breaks

A federation break includes conditions such as:

- remote authority becomes unreachable;
- active agreement can no longer be verified;
- agreement expires or is revoked;
- remote response violates the expected public contract;
- remote verification material is malformed or unavailable.

Federation breaks are not silently converted into trust. The reference gateway records break details and surfaces failure to the caller. High-assurance deployments should additionally persist/emit these records into the canonical evidence and incident-management paths.*

## 10. Conflict Resolution

When registries disagree:

- the issuing authority remains authoritative for its issued identifier unless a superseding governance/legal process establishes otherwise;
- cached records must not silently override fresher authoritative records;
- disputes and corrections should be represented as accountable records;
- any hub/regulator arbitration process is governed by the applicable federation agreement and external authority.

## 11. Invariants

- Federation recognition is explicit and cryptographically attributable.
- Federation agreements are bounded, expirable, and revocable.
- Unrecognized or unverifiable authorities fail closed.
- Public federation discloses only explicitly reviewed public fields.
- Full disclosed event chains can be independently hash/signature verified.
- Cross-registry delegation cannot widen authority.
- Federation breaks are detectable.
- Federation does not weaken AI-IDP identity, authorization, privacy, permanence, or accountability invariants.

> `*` Institutional registry operation, authenticated controlled/sealed disclosure, regulator-operated infrastructure, production URLs/credentials, independent federation governance, and external adoption/certification are deployment/institutional dependencies. The reference implementation provides the protocol and gateway mechanics without claiming those institutions already operate AI-IDP infrastructure.
