# AegisTrace Architecture Guide

Last Material Revision: 2026-08-01

## Layered Architecture

AegisTrace is organized into six layers. See `technical/AEGISTRACE_TECHNICAL_ARCHITECTURE.md` for the full architecture.

### Identity Layer
The identity layer manages AI Actor identifiers and signing keys. It comprises `identity/ids.py` (Identifier, URI parsing, ULID generation), `identity/keys.py` (KeyService, KeyRecord), and `identity/lifecycle.py` (Registry, EntityRecord).

### Ledger Layer
The ledger layer is the heart of the traceability system. It comprises `ledger/append_only.py` (AppendOnlyLedger, LedgerVerifier), `ledger/merkle.py` (merkle_root, merkle_proof), `signing/ed25519.py` (SigningKey, sha256_hex), and `signing/canonical.py` (canonicalize).

### Governance Layer
The governance layer manages authority chains. It comprises `delegation/broker.py` (DelegationBroker, Delegation, DelegationScope) and `authorization/engine.py` (PolicyEngine, Authorization, Approval).

### Event Layer
The event layer builds, signs, and records events. It comprises `events/models.py` (Event, Actor, ExecutionContext, ACTIONS, VISIBILITY_TIERS) and `events/collector.py` (EventCollector).

### Adapter Layer
The adapter layer bridges AegisTrace to external systems. It comprises `adapters/filesystem.py`, `adapters/git.py`, `adapters/github.py`, `adapters/database.py`, and `adapters/mcp.py`.

### Storage Layer
The storage layer persists the ledger, registry, and keys. It comprises `storage/sqlite.py` (SQLiteStorage) and JSONL files (canonical, human-readable, externally-verifiable).

## Key Invariants

The architecture enforces 23 invariants (see `spec/AI-IDP-CORE.md` Section 5). The most important invariants:

1. Every agent instance resolves to one persistent agent.
2. Every persistent agent resolves to an accountable controller.
3. Every action resolves to an agent instance, a task, and an authority chain.
4. Every child agent resolves to a parent delegation.
5. Model/provider switches preserve agent identity.
6. Revocation and termination preserve historical records.
7. Corrections append; they do not overwrite.
8. Every event is cryptographically linked (hash chain + signature).
9. An agent cannot silently alter its canonical history.
10. An administrator cannot silently erase canonical history.

## Data Flow

1. A controller registers an agent (identity layer).
2. A principal issues an authorization (governance layer).
3. The agent instance requests to perform an action.
4. The policy engine evaluates the request (governance layer).
5. The event collector builds, signs, and appends the event (event layer).
6. The ledger verifies the hash chain and event hash (ledger layer).
7. Periodically, a Merkle root is anchored to a public verification surface (ledger layer).
8. External verifiers can verify the ledger at any time.

## Security Properties

- Forgery resistance
- Revocation enforcement
- Hash-chain integrity
- Event-hash correctness
- Signature verification
- Approval single-use
- Scope enforcement
- Fail-closed operation
- Path-traversal protection
- Public/private separation

## Privacy Properties

- Pseudonymous identifiers
- No contact data in events
- Visibility tiers (PUBLIC, CONTROLLED, ORGANIZATION_PRIVATE, SEALED)
- Sealed records
- User-enumeration prevention

## Permanence Properties

- Permanent resolvability
- Historical signature validity
- Key rotation preservation
- Identity preservation across model/provider switches
- Archive preservation
- Ledger permanence after agent termination

## Conformance Properties

- Schema conformance
- Canonical action vocabulary
- Canonical visibility tiers
- Required invariants
- Append-only
- Public-tier field separation
- Ledger integrity after many appends

# AegisTrace Architecture Guide
