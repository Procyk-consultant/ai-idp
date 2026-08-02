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
File: spec/FEDERATION_PROTOCOL.md
Title: Federation Protocol
Purpose: Define how multiple registry authorities interoperate
Audience: Architects, registry operators, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: REGISTRY_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Federated events are verifiable in any federated registry
Failure Behaviour: Federation breaks are detected
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Federation Protocol

## 1. Purpose

Federation allows multiple registry authorities to interoperate. A federated event is verifiable in any federated registry. A cross-jurisdiction delegation preserves the authority chain.

## 2. Federation Topology

AI-IDP supports:

- **National federation** — federal regulator + sectoral regulators + provincial regulators.
- **Bilateral federation** — pairwise federation between two registry authorities.
- **Multilateral federation** — federation via a federation hub.
- **International federation** — federation with foreign registry authorities (where authorized).

## 3. Federation Agreement

A federation agreement is a signed document specifying:

- The federating authorities.
- The trust model (e.g., mutual recognition, hierarchical).
- The data shared (which tiers, which fields).
- The verification procedures.
- The dispute resolution procedure.
- The termination procedure.
- The effective date and expiry.

## 4. Cross-Registry Resolution

A permanent identifier from one registry resolves in another registry via:

1. The receiving registry looks up the identifier in its local cache.
2. If not cached, the receiving registry queries the issuing registry via the federation API.
3. The issuing registry returns the public-tier record.
4. The receiving registry caches the record (with a TTL).
5. The receiving registry returns the record to the requester.

For controlled-tier or sealed-tier records, the requester must have authorization from the issuing registry.

## 5. Cross-Registry Verification

A federated event is verified by:

1. The receiving registry verifies the event's signature using the signing key from the issuing registry.
2. The receiving registry verifies the event's hash chain by querying the issuing registry's ledger.
3. The receiving registry verifies the event's authority chain by resolving the actor identifiers.
4. The receiving registry verifies the event's policy version against the issuing registry's policy.

## 6. Cross-Registry Delegation

A cross-registry delegation is a delegation where the parent and child are in different registries. The delegation record includes:

- The parent registry's identifier.
- The child registry's identifier.
- The federation agreement reference.
- The parent's signature.
- The child's signature (acknowledging the delegation).

## 7. Federation Gateway

A federation gateway is a service that mediates between federated registries. The gateway:

- Translates between federation protocols.
- Enforces federation agreement terms.
- Logs federation operations.
- Detects federation breaks (e.g., a registry that becomes unreachable).

## 8. Conflict Resolution

Conflicts may arise between federated registries (e.g., two registries claim the same identifier). Conflict resolution is per the federation agreement:

- The issuing registry's record is authoritative.
- The federation hub may arbitrate.
- Disputes are recorded as dispute events.

## 9. Invariants

- Federated events are verifiable in any federated registry.
- Cross-jurisdiction delegations preserve the authority chain.
- Federation breaks are detected and logged.
- Conflict resolution follows the federation agreement.
- Federation does not weaken the invariants.
