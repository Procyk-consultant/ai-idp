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
File: spec/DELEGATION_PROTOCOL.md
Title: Delegation Protocol
Purpose: Define how authority is delegated from parent agents to child agents
Audience: Architects, implementers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: ACTOR_MODEL.md; AUTHORIZATION_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Every child agent resolves to a parent delegation
Failure Behaviour: Undelegated child agents are rejected
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Delegation Protocol

## 1. Purpose

Delegation allows a parent agent to grant a bounded scope of authority to a child agent. Delegation is a first-class governance record in AI-IDP. Every child agent resolves to a parent delegation; every delegation resolves to a delegating principal.

## 2. Delegation Record

A delegation record contains:

- `delegation_id` — unique identifier (`aitrace://ca/delegation/<slug>`).
- `parent_agent_id` — the persistent agent identifier of the parent.
- `parent_instance_id` — the agent instance identifier of the parent at the time of delegation.
- `child_agent_id` — the persistent agent identifier of the child.
- `principal_id` — the principal authorizing the delegation.
- `controller_id` — the controller accountable for the child.
- `scope` — the bounded scope of authority delegated (e.g., task classes, resource classes, action classes, time bounds, geography).
- `expires_at` — optional expiry timestamp.
- `revocable` — whether the delegation is revocable.
- `created_at` — creation timestamp.
- `signature` — cryptographic signature by the parent.

## 3. Delegation Operations

### 3.1 Create

A delegation is created by:

1. The parent agent (or its principal) submits a delegation request.
2. The delegation broker validates the request.
3. The delegation is recorded as a signed event in the ledger.
4. The child agent's registry record references the delegation.

### 3.2 Verify

A delegation is verified by:

1. The delegation record exists in the ledger.
2. The delegation is in an active state (not revoked, not expired).
3. The delegation's scope encompasses the proposed child action.
4. The parent agent is active.
5. The principal is authorized.
6. The signature is valid.

### 3.3 Revoke

A delegation may be revoked by:

1. The parent agent (or its principal).
2. An authorized regulator (for cause).
3. The delegation's expiry (automatic revocation).

Revocation is a new signed event. Historical records are preserved.

### 3.4 Expire

A delegation with `expires_at` automatically expires at the expiry timestamp. Expiry is a new signed event recorded by the delegation broker.

## 4. Scope

Delegation scope is bounded by:

- **Task classes** — the child may perform only specified task classes.
- **Resource classes** — the child may access only specified resource classes.
- **Action classes** — the child may perform only specified action classes.
- **Time bounds** — the child may operate only within the specified time window.
- **Geography** — the child may operate only within the specified geography.
- **Tool classes** — the child may use only specified tool classes.
- **Model classes** — the child may use only specified model classes.
- **Provider classes** — the child may use only specified provider classes.
- **Delegation depth** — the child may not delegate further (or may delegate to a specified depth).

Scope is enforced by the policy engine before any action by the child agent.

## 5. Delegation Chains

Delegations form chains: a parent delegates to a child, which may delegate to a grandchild, and so on. The delegation chain is recorded for every action:

```
principal -> controller -> parent_agent -> delegation_1 -> child_agent -> delegation_2 -> grandchild_agent -> action
```

The chain is verifiable end-to-end. Any broken link invalidates the action.

## 6. Delegation Depth

Delegation depth is bounded by policy. The default maximum depth is 3 (parent → child → grandchild → great-grandchild). Deeper delegations require dual authorization.

## 7. Swarm Delegation

In a swarm, multiple agents operate together. Swarm delegations are pairwise: each pair has a delegation record. The swarm itself has a swarm record listing its members and their pairwise delegations.

## 8. Cross-Organization Delegation

A delegation may cross organizational boundaries (e.g., organization A's agent delegates to organization B's agent). Cross-organization delegations require:

- Mutual recognition of the two organizations' registry authorities.
- A federation agreement (if the organizations are in different federations).
- Dual authorization (both organizations' principals).
- Enhanced logging (cross-organization delegations are logged at controlled tier).

## 9. Invariants

- Every child agent resolves to a parent delegation.
- A delegation's scope is enforced.
- A revoked or expired delegation produces no new valid child actions.
- A delegation chain is verifiable end-to-end.
- A delegation does not change the parent's accountability; the parent's controller remains accountable for the child's actions within the delegated scope.

## 10. Examples

### 10.1 Simple Delegation

A research agent delegates a sub-task (literature search) to a sub-agent:

```json
{
  "delegation_id": "aitrace://ca/delegation/dlg-00104",
  "parent_agent_id": "aitrace://ca/agent/research-agent#v3",
  "parent_instance_id": "aitrace://ca/agent-instance/research-agent#run-0042",
  "child_agent_id": "aitrace://ca/agent/literature-search-agent#v1",
  "principal_id": "aitrace://ca/principal/user-012",
  "controller_id": "aitrace://ca/controller/org-001",
  "scope": {
    "task_classes": ["literature-search"],
    "resource_classes": ["web-search", "arxiv"],
    "action_classes": ["SEARCH", "READ", "QUERY"],
    "time_bounds": {"not_after": "2026-08-01T20:00:00Z"},
    "delegation_depth": 0
  },
  "expires_at": "2026-08-01T20:00:00Z",
  "revocable": true,
  "created_at": "2026-08-01T18:00:00Z",
  "signature": "..."
}
```

### 10.2 Cross-Organization Delegation

Organization A's compliance agent delegates a verification sub-task to organization B's audit agent. The delegation includes a federation reference and dual authorization.
