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
File: SKILL.md
Title: Skill Description
Purpose: Describe the AI-IDP / AegisTrace skill for agent systems
Audience: Agent frameworks, skills registries
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Approved
Last Material Revision: 2026-08-01
Dependencies: AGENTS.md
Source Basis: Master Execution Prompt
Invariants: Skill scope matches project scope
Failure Behaviour: Skill drift is escalated
Trace Policy: Skill invocations are AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# SKILL.md — AI-IDP / AegisTrace

## Skill Name

`aegistrace`

## Description

A skill that provides persistent AI Actor identity, delegation, provenance, traceability, quality evidence, accountability, and permanent audit for AI agents operating in Canada. The skill exposes the AegisTrace reference implementation as an importable Python package, a CLI, and a FastAPI server.

## Capabilities

Issue persistent AI Actor identifiers; issue runtime agent instance identifiers; register providers, models, deployments, controllers, principals, agents, tasks, delegations, authorizations, approvals; record material actions as append-only, hash-chained, signed events; verify ledger integrity; audit-reconstruct incidents from the ledger; export public verification data (Merkle roots, revocation status, certification status); manage key rotation, suspension, revocation, termination; manage corrections, revocations, disputes as new signed events; support offline mode with later reconciliation; support federation between AegisTrace instances.

## Interfaces

Python: `import aegistrace`. CLI: `python3 -m aegistrace.cli <subcommand>`. API: `from aegistrace.api.server import app`.

## Dependencies

Python 3.12+; `cryptography` for Ed25519 signatures; `pydantic` for data models; `fastapi` for the API server; `jsonschema` for schema validation; `pytest` for tests.

## Prohibited Uses

External publication without authorization; public licence application without authorization; brand asset modification; logo generation; author data fabrication; citation fabrication; data fabrication.

## Authority

Pierre-Edward Procyk is the sole authority for skill release, licensing, and external distribution.
