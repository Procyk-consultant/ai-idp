# AegisTrace Offline Operation Guide

Last Material Revision: 2026-08-01

## Purpose

Agents may operate without network connectivity. Offline operation buffers events locally and reconciles with the canonical ledger when connectivity is restored.

## Offline Buffer

The offline buffer is a local append-only, hash-chained ledger. The buffer:

- Records events in the same format as the canonical ledger.
- Uses a local sequence (independent of the canonical ledger).
- Is signed by the agent's signing key.
- Is encrypted at rest.
- Is reconciled with the canonical ledger on reconnect.

## Reconciliation

1. The agent connects to the canonical ledger.
2. The agent submits the buffered events.
3. The canonical ledger verifies each event (signature, hash chain, authorization, policy).
4. The canonical ledger appends the verified events with canonical sequence numbers.
5. The canonical ledger returns the canonical sequence numbers to the agent.
6. The agent updates its local buffer with the canonical sequence numbers.

## Conflict Handling

- An authorization may have been revoked while the agent was offline. The agent's offline actions are recorded but flagged as `authorization_revoked_after`.
- A policy may have changed while the agent was offline. The agent's offline actions are evaluated against the policy in effect at the time of the action.
- A key may have been revoked while the agent was offline. The agent's offline signatures are still verifiable, but the events are flagged as `key_revoked_after`.

## Limits

- Maximum offline duration: 30 days (default; configurable per policy).
- Maximum buffer size: 100,000 events (default; configurable per policy).
- Maximum number of offline actions per task: 1,000 (default; configurable per policy).
- Required reconciliation frequency: on reconnect.

# AegisTrace Offline Operation Guide
