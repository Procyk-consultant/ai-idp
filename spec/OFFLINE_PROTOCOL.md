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
File: spec/OFFLINE_PROTOCOL.md
Title: Offline Protocol
Purpose: Define how agents operate offline and reconcile later
Audience: Architects, implementers, operators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: EVENT_PROTOCOL.md; RESOURCE_TRACE_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Offline operation does not weaken invariants
Failure Behaviour: Unreconciled offline buffers are flagged
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Offline Protocol

## 1. Purpose

Agents may operate without network connectivity. Offline operation buffers events locally and reconciles with the canonical ledger when connectivity is restored.

## 2. Offline Buffer

The offline buffer is a local append-only, hash-chained ledger. The buffer:

- Records events in the same format as the canonical ledger.
- Uses a local sequence (independent of the canonical ledger).
- Is signed by the agent's signing key.
- Is encrypted at rest.
- Is reconciled with the canonical ledger on reconnect.

## 3. Reconciliation

Reconciliation:

1. The agent connects to the canonical ledger.
2. The agent submits the buffered events.
3. The canonical ledger verifies each event (signature, hash chain, authorization, policy).
4. The canonical ledger appends the verified events with canonical sequence numbers.
5. The canonical ledger returns the canonical sequence numbers to the agent.
6. The agent updates its local buffer with the canonical sequence numbers.
7. The agent's local buffer is now consistent with the canonical ledger.

## 4. Conflict Handling

Conflicts may arise during reconciliation:

- An authorization may have been revoked while the agent was offline. In this case, the agent's offline actions are recorded but flagged as `authorization_revoked_after`.
- A policy may have changed while the agent was offline. The agent's offline actions are evaluated against the policy in effect at the time of the action (recorded in the event).
- A key may have been revoked while the agent was offline. The agent's offline signatures are still verifiable (the key was valid at the time of signing), but the events are flagged as `key_revoked_after`.

## 5. Offline Verification

Offline events are verified:

- The event's signature is valid (the key was valid at the time of signing).
- The event's hash chain is consistent within the offline buffer.
- The event's authorization was valid at the time of the action.
- The event's policy was in effect at the time of the action.

## 6. Offline Mode Limits

Offline mode has limits:

- Maximum offline duration (per policy; default 30 days).
- Maximum buffer size (per policy; default 100,000 events).
- Maximum number of offline actions per task (per policy; default 1,000).
- Required reconciliation frequency (per policy; default on reconnect).

## 7. Invariants

- Offline operation does not weaken the invariants.
- Offline events are signed and hash-chained.
- Reconciliation preserves the canonical ledger's integrity.
- Conflicts are flagged, not silently resolved.
- Unreconciled offline buffers are flagged.
