# AegisTrace Federation Guide

Last Material Revision: 2026-08-01

## Federation Topology

- National federation: federal regulator + sectoral regulators + provincial regulators
- Bilateral federation: pairwise federation between two registry authorities
- Multilateral federation: federation via a federation hub
- International federation: federation with foreign registry authorities (where authorized)

## Federation Agreement

A federation agreement is a signed document specifying:

- The federating authorities
- The trust model (e.g., mutual recognition, hierarchical)
- The data shared (which tiers, which fields)
- The verification procedures
- The dispute resolution procedure
- The termination procedure
- The effective date and expiry

## Cross-Registry Resolution

A permanent identifier from one registry resolves in another registry via:

1. The receiving registry looks up the identifier in its local cache.
2. If not cached, the receiving registry queries the issuing registry via the federation API.
3. The issuing registry returns the public-tier record.
4. The receiving registry caches the record (with a TTL).
5. The receiving registry returns the record to the requester.

## Cross-Registry Verification

A federated event is verified by:

1. Signature verification using the signing key from the issuing registry.
2. Hash chain verification by querying the issuing registry's ledger.
3. Authority chain verification by resolving the actor identifiers.
4. Policy verification against the issuing registry's policy.

## Cross-Registry Delegation

A cross-registry delegation is a delegation where the parent and child are in different registries. The delegation record includes the parent registry's identifier, the child registry's identifier, the federation agreement reference, the parent's signature, and the child's signature.

## Federation Gateway

A federation gateway mediates between federated registries. The gateway translates between federation protocols, enforces federation agreement terms, logs federation operations, and detects federation breaks.

# AegisTrace Federation Guide
