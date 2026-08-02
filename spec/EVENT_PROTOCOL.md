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
File: spec/EVENT_PROTOCOL.md
Title: Event Protocol
Purpose: Define the structure, signing, and verification of events
Audience: Architects, implementers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: ACTOR_MODEL.md; signing/
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Events are append-only, hash-chained, signed
Failure Behaviour: Event tampering is detectable
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Event Protocol

## 1. Event Structure

An event is a JSON object with the following fields:

```json
{
  "schema_version": "1.0.0",
  "event_id": "evt_01JEXAMPLE",
  "timestamp": "2026-08-01T00:00:00Z",
  "jurisdiction_id": "ca",
  "actor": {
    "controller_id": "aitrace://ca/controller/org-001",
    "principal_id": "aitrace://ca/principal/user-012",
    "agent_id": "aitrace://ca/agent/research-agent#v3",
    "agent_instance_id": "aitrace://ca/agent-instance/research-agent#run-0042"
  },
  "execution_context": {
    "provider_id": "aitrace://ca/provider/provider-001",
    "model_id": "aitrace://ca/model/example-llm",
    "model_version_id": "aitrace://ca/model/example-llm#v1.2",
    "deployment_id": "aitrace://ca/deployment/deployment-001"
  },
  "task_id": "aitrace://ca/task/task-00104",
  "delegation_id": "aitrace://ca/delegation/dlg-00104",
  "authorization_id": "aitrace://ca/authorization/auth-00104",
  "approval_id": "aitrace://ca/approval/apr-00104",
  "action": "MODIFY",
  "resource_id": "urn:sha256:RESOURCE_DIGEST",
  "before_digest": "sha256:BEFORE_DIGEST",
  "after_digest": "sha256:AFTER_DIGEST",
  "visibility": "ORGANIZATION_PRIVATE",
  "policy_version": "1.4.2",
  "previous_event_hash": "sha256:PREVIOUS_EVENT_HASH",
  "event_hash": "sha256:CURRENT_EVENT_HASH",
  "signature": "Ed25519:SIGNATURE_VALUE",
  "signing_key_id": "aitrace://ca/key/key-001"
}
```

This example is illustrative test data only. It is not a real event.

## 2. Schema Version

`schema_version` follows semantic versioning. The current version is `1.0.0`. Schema changes are governed by `VERSIONING_POLICY.md`.

## 3. Timestamp

`timestamp` is an ISO 8601 UTC timestamp. Timestamps are monotonic within a ledger but not necessarily globally monotonic (different ledgers may have skew). Timestamp manipulation is detected by hash chaining and signature verification.

## 4. Actor

`actor` contains the authority chain:

- `controller_id` — the accountable controller.
- `principal_id` — the authorizing principal.
- `agent_id` — the persistent agent.
- `agent_instance_id` — the runtime instance.

Every action resolves to all four.

## 5. Execution Context

`execution_context` contains the execution environment:

- `provider_id` — the model provider.
- `model_id` — the model.
- `model_version_id` — the model version.
- `deployment_id` — the deployment.

Model or provider switches create new execution-context records but do not change the agent's identity.

## 6. Action and Resource

`action` is one of the actions enumerated in Master Prompt §6. `resource_id` is a URN of the affected resource. `before_digest` and `after_digest` are SHA-256 digests of the resource before and after the action (for mutating actions).

## 7. Visibility

`visibility` is one of:

- `PUBLIC` — visible to any party (only non-sensitive fields).
- `CONTROLLED` — visible to authorized regulators, auditors, certification bodies.
- `ORGANIZATION_PRIVATE` — visible to the controlling organization.
- `SEALED` — visible only under judicial or regulator-controlled disclosure.

## 8. Hash Chain

`previous_event_hash` is the SHA-256 hash of the previous event's canonical serialization. `event_hash` is the SHA-256 hash of this event's canonical serialization (excluding the `event_hash` and `signature` fields). The hash chain provides tamper-evidence: any modification, deletion, or insertion is detectable.

## 9. Signature

`signature` is an Ed25519 signature over the event's canonical serialization (excluding the `signature` field). `signing_key_id` is the identifier of the signing key. The signing key must be bound to the `agent_id` (or its controller) at the time of signing.

## 10. Canonicalization

Canonicalization is defined in `signing/canonical.py`. The canonical form is:

1. Remove the `signature` field.
2. Remove the `event_hash` field.
3. Sort object keys lexicographically.
4. Encode as UTF-8 JSON with no whitespace, no line breaks, and no non-ASCII escapes.
5. Compute SHA-256 to get `event_hash`.
6. Re-add `event_hash` (now part of the canonical form for signature).
7. Sign with Ed25519.

## 11. Verification

An event is verified by:

1. Schema validation against `schemas/event.schema.json`.
2. Canonicalization and recomputation of `event_hash`.
3. Signature verification with the signing key.
4. Hash chain verification: `previous_event_hash` matches the previous event's `event_hash`.
5. Authorization verification (per `AUTHORIZATION_PROTOCOL.md`).
6. Delegation verification (if applicable).
7. Approval verification (if applicable).
8. Policy verification.

## 12. Append-Only

Events are append-only. No event may be modified or deleted. Corrections and revocations are new signed events that reference the original.

## 13. Sequence Awareness

Events are sequence-aware: every event has a `previous_event_hash` linking it to the previous event. A missing event creates a gap detectable by hash verification. A reordered event creates an inconsistent chain detectable by hash verification.

## 14. Merkle Anchoring

Periodically (e.g., daily), a Merkle root is computed over the recent event sequence and anchored to a public verification surface (e.g., the public verification repository, a transparency log). Merkle anchoring provides tamper-evidence beyond the local ledger.

## 15. Independent Replication

The ledger is independently replicated (e.g., to an independent archive, a regulator-controlled vault, a federated registry). Independent replication provides tamper-evidence beyond any single copy.

## 16. Invariants

- Events are append-only.
- Events are hash-chained.
- Events are signed.
- Events are sequence-aware.
- Events are tamper-evident.
- Events are independently verifiable.
- Missing or reordered events are detectable.
- An agent cannot silently alter its canonical history.
- An administrator cannot silently erase canonical history.
- A provider cannot silently substitute a model without a trace event.
- A user cannot silently assign an action to a different agent.
- An agent cannot silently assign an action to a different user.
