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
File: AGENTS.md
Title: Agent Protocol
Purpose: Define how logical agents operate in this project
Audience: Multi-agent orchestration systems, A01-A35 roles
Document Classification: Internal
Classification: documentation
Version: 2.0.0
Status: Approved
Last Material Revision: 2026-08-01
Dependencies: PROJECT_SCOPE_LOCK.md; research/protocol/AGENTSWARM_PROCEDURE.md
Source Basis: Master Execution Prompt
Invariants: Every agent has a unique ID, bounded mandate, and validation agent
Failure Behaviour: Agent violations are escalated
Trace Policy: Agent actions are first-class AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Agent Protocol

## Agent Roles

The project uses 35 logical agent roles (A01-A35) defined in `research/protocol/AGENTSWARM_PROCEDURE.md`. AgentSwarm is the research and project-execution method, not the project, not the standard, not the legal subject.

## Per-Agent Requirements

Every agent must receive: a unique research-agent ID; parent-task ID; role; bounded mandate; source permissions; tool permissions; required outputs; evidence requirements; prohibited actions; escalation conditions; validation agent; completion criteria.

## Agent Identity in AegisTrace

When an agent operates on a project artifact, the operation is recorded as an AegisTrace event with agent_id, agent_instance_id, principal_id, controller_id, task_id, delegation_id, authorization_ref, action, resource_id, before_digest, after_digest, execution_context, visibility, previous_event_hash, event_hash, and signature. Example events use synthetic identifiers (aitrace://ca/principal/user-XXX), never real contact data.

## Validation Agent

No critical agent may be the sole validator of its own output. A31 (citation auditor), A32 (engineering validator), A33 (adversarial reviewer), A34 (visual/document validator), and A35 (final release controller) form the independent validation chain.

## Prohibited Agent Actions

External publication; external deployment; public licence application; brand asset modification; logo generation; author data fabrication; citation fabrication; data fabrication; silent scope reduction or expansion; suppressing criticism, contradictions, or negative findings.
