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
File: spec/ACTOR_MODEL.md
Title: Actor Model
Purpose: Define the actor model and entity relationships
Audience: Architects, implementers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: AI-IDP-CORE.md; TERMINOLOGY.md; schemas/
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Entity relationships are consistent across all schemas
Failure Behaviour: Schema inconsistencies are defects
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Actor Model

## 1. Overview

The AI-IDP actor model defines the entities that participate in AI agent operation, their relationships, and their lifecycle. The model is grounded in the conceptual principles in `AI-IDP-CORE.md` and the terminology in `TERMINOLOGY.md`.

## 2. Entities

### 2.1 Jurisdiction-Level Entities

- **Jurisdiction** — Canada, with sub-authority for provinces and territories.
- **Registry authority** — operator of the registry tiers.
- **Identity issuer** — operational component that mints identifiers.

### 2.2 Provider-Side Entities

- **Provider** — organization that supplies or operates a model or service.
- **Provider service** — specific service offering of a provider.
- **Model family** — a family of related models.
- **Model** — a specific AI model.
- **Model version** — a versioned release of a model.
- **Model artifact** — the weights/parameters of a model version.
- **Deployment** — a specific deployment of a model or service.
- **Endpoint** — a specific network endpoint.

### 2.3 Organization-Side Entities

- **Organization** — any legal person or entity.
- **Accountable controller** — the organization legally accountable for an agent.
- **Human principal** — a human who authorizes actions.
- **Service principal** — a non-human principal.
- **User** — the end-user on whose behalf an agent acts.

### 2.4 Agent-Side Entities

- **Persistent agent** — the identifiable logical software actor.
- **Agent version** — a versioned release of a persistent agent.
- **Agent configuration** — a specific configuration of a persistent agent.
- **Runtime agent instance** — a specific execution of an agent.
- **Parent agent / child agent / swarm** — delegation hierarchy.

### 2.5 Execution-Side Entities

- **Orchestrator** — coordinates agent execution.
- **Tool** — a specific tool used by an agent.
- **Connector** — a specific connector to an external system.
- **Execution environment** — the environment in which an agent executes.
- **Device** — a specific device.
- **Session** — a specific session.

### 2.6 Governance Entities

- **Task** — a unit of work.
- **Delegation** — a bounded grant of authority from a parent to a child.
- **Authorization** — a record of authorization for an action or class.
- **Approval** — a single-use approval record.
- **Policy** — a rule governing agent actions.

### 2.7 Execution Records

- **Action** — a material operation.
- **Event** — the signed, hash-chained record of an action.
- **Resource** — any affected file, directory, repository, database, API, service, system, or infrastructure.
- **Directory / repository / branch / commit / database / transaction / artifact** — specific resource types.

### 2.8 Quality and Accountability Entities

- **Test run / build / release / attestation** — quality records.
- **Incident / audit / certification / revocation / correction / legal hold** — accountability records.

## 3. Relationships

### 3.1 Identity Resolution

- An **agent instance** resolves to exactly one **persistent agent**.
- A **persistent agent** resolves to exactly one **accountable controller**.
- An **accountable controller** resolves to one or more **organizations** (parent/subsidiary, controlling organization, etc.).
- A **human principal** resolves to one or more **users** of one or more **organizations**.
- A **service principal** resolves to a **persistent agent** or external service.

### 3.2 Execution Chain

- An **action** resolves to an **agent instance**.
- An **agent instance** resolves to a **persistent agent**, an **execution context** (provider, model, version, deployment), and a **session**.
- An **action** resolves to a **task**.
- A **task** resolves to an **authority chain** (principal → controller → ... → jurisdiction).
- A **task** may resolve to a **delegation** (if the action was delegated).

### 3.3 Delegation Chain

- A **child agent** resolves to a **parent delegation**.
- A **parent delegation** resolves to a **parent agent** and a **principal** who authorized the delegation.
- A **swarm** resolves to a set of **agents** with pairwise delegation relationships.

### 3.4 Resource Chain

- A **resource** has a **manifest** (digest, owner, scope).
- An **action** affects one or more **resources** with before/after digests.
- A **repository** contains **branches**, **commits**, **artifacts**, and **releases**.
- A **build** produces an **artifact** from **source** with **build evidence**.
- A **release** contains **artifacts**, **attestations**, and **quality evidence**.

### 3.5 Quality Chain

- A **quality claim** resolves to **quality evidence** (test run, build, release, attestation, audit, certification).
- A **certification** is issued by a **certification body** to a **controller** for a **conformance level**.
- An **audit** is performed by an **auditor** against a **scope** and produces an **audit report**.

### 3.6 Accountability Chain

- An **incident** involves one or more **events** and one or more **agents**.
- An **audit** reviews the **ledger** and produces findings.
- A **revocation** revokes an identifier, key, authorization, or agent.
- A **correction** corrects a prior event by appending a new signed event.
- A **legal hold** preserves records relevant to a legal proceeding.

## 4. Lifecycle

### 4.1 Persistent Agent Lifecycle

1. **Creation.** A persistent agent is created by a controller, with an initial version, configuration, and signing key.
2. **Operation.** The agent operates, generating agent instances, tasks, and events.
3. **Versioning.** New agent versions may be released; each is a distinct version with its own configuration.
4. **Delegation.** The agent may delegate to child agents; delegations are bounded and revocable.
5. **Suspension.** The agent may be suspended (temporary).
6. **Revocation.** The agent may be revoked (permanent).
7. **Termination.** The agent may be terminated. The permanent identifier remains resolvable; historical records are preserved.

### 4.2 Agent Instance Lifecycle

1. **Spawn.** An instance is spawned with a specific execution context.
2. **Execution.** The instance executes tasks, generating events.
3. **Model/provider switches.** Switches create new execution-context records; the instance identifier is unchanged.
4. **Termination.** The instance terminates. The instance identifier remains resolvable.

### 4.3 Key Lifecycle

1. **Creation.** A key is created and bound to an entity.
2. **Active use.** The key is used to sign events.
3. **Rotation.** A new key is created; the old key is rotated out but not destroyed.
4. **Suspension.** The key may be suspended (temporary).
5. **Revocation.** The key may be revoked (permanent). Revoked keys cannot produce valid new events.
6. **Termination.** The key is terminated. Historical signatures remain verifiable.

### 4.4 Event Lifecycle

1. **Creation.** An event is created, signed, and appended to the ledger.
2. **Verification.** The event is verifiable indefinitely by anyone with the ledger.
3. **Correction.** An error in the event may be corrected by appending a correction event. The original event is preserved.
4. **Revocation.** An authorization recorded in the event may be revoked by appending a revocation event. The original event is preserved.
5. **Dispute.** A fact in the event may be disputed by appending a dispute event. The original event is preserved.
6. **Legal hold.** A legal hold may be placed on the event, preventing deletion or modification (events cannot be modified in any case; legal hold prevents deletion of related resources).

## 5. Schemas

Each entity has a JSON Schema in `schemas/`. The schemas are normative; implementations must validate against them.
