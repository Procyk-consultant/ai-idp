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
File: GOVERNANCE.md
Title: Governance Model
Purpose: Define how the project is governed during preparation
Audience: All agents and reviewers
Document Classification: Internal
Classification: documentation
Version: 2.0.0
Status: Approved
Last Material Revision: 2026-08-01
Dependencies: PROJECT_CHARTER.md
Source Basis: Master Execution Prompt
Invariants: Pierre-Edward Procyk is the final authority
Failure Behaviour: Governance violations are escalated to A01 guardian
Trace Policy: Governance decisions are recorded in DECISION_LOG.md
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Governance Model

## Authority Structure

Pierre-Edward Procyk is the Project Originator with final authority for all material decisions. The A01 Project Authority Guardian preserves originator intent, scope, IP, and branding. The A02 Program Orchestrator maintains the task graph, dependencies, and status. The A35 Final Release Controller assembles only validated artifacts.

## Decision Authority

Routine implementation decisions (libraries, schemas, file layout) are autonomous and recorded in `project-control/DECISION_LOG.md`. Material scope changes, external publication, licensing, brand modifications, and external submission require Pierre-Edward Procyk's authorization. Blocker escalations are consolidated in `project-control/BLOCKER_REGISTER.md`.

## Agent Role Separation

No critical agent may be the sole validator of its own output. The A31 Citation and Claim Auditor, A32 Independent Engineering Validator, A33 Adversarial Legal and Social Reviewer, A34 Visual and Document Quality Validator, and A35 Final Release Controller form the independent validation chain.

## Pause Conditions

Execution pauses only when an essential private source is missing and no defensible alternative exists; a decision would materially change the central legal or technical objective; a required action would publish, send, deploy, purchase, delete, or expose information externally; a safety or legal constraint prevents execution; a required credential is unavailable and the task cannot be completed locally; or the environment cannot perform an essential operation. When such a blocker occurs, all non-blocked work continues; blockers are consolidated in `project-control/BLOCKER_REGISTER.md`.
