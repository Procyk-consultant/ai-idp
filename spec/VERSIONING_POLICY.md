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
File: spec/VERSIONING_POLICY.md
Title: Versioning Policy
Purpose: Define how AI-IDP specifications, schemas, and protocols are versioned
Audience: All readers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: AI-IDP-CORE.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Versions are semantic and documented
Failure Behaviour: Silent version changes are forbidden
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Versioning Policy

## 1. Semantic Versioning

AI-IDP follows semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** — backward-incompatible changes.
- **MINOR** — backward-compatible additions.
- **PATCH** — backward-compatible bug fixes.

## 2. Versioned Components

- **Specification version** — the version of the AI-IDP specification (this document set).
- **Schema version** — the version of each JSON Schema.
- **Protocol version** — the version of each protocol.
- **Conformance level version** — the version of each conformance level definition.
- **Reference implementation version** — the version of the AegisTrace reference implementation.

## 3. Version Recording

Every event records:

- `schema_version` — the event schema version.
- `protocol_version` — the protocol version.
- `policy_version` — the policy version.

## 4. Compatibility

- Major version changes require a documented migration path.
- Minor version changes are backward-compatible.
- Patch version changes are bug fixes.

## 5. Deprecation

Deprecated features are documented. Deprecation does not remove the feature; it marks it for removal in a future major version.

## 6. Invariants

- Versions are semantic.
- Versions are documented.
- Major version changes have migration paths.
- Deprecation is documented.
- Silent version changes are forbidden.
