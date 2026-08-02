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
File: spec/EXTENSION_POLICY.md
Title: Extension Policy
Purpose: Define how AI-IDP may be extended
Audience: Architects, sectoral/provincial extenders
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: VERSIONING_POLICY.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Extensions do not weaken invariants
Failure Behaviour: Invariant-weakening extensions are rejected
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Extension Policy

## 1. Extension Purpose

AI-IDP may be extended for:

- Sectoral requirements (e.g., finance, healthcare, energy).
- Provincial requirements (e.g., Quebec, Ontario, BC).
- Organizational requirements (e.g., enterprise-specific policies).
- International interoperation (e.g., mapping to foreign regulations).

## 2. Extension Types

- **Profile extensions** — additional compliance profiles for specific contexts.
- **Policy extensions** — additional policies for specific sectors or organizations.
- **Schema extensions** — additional fields or entities for specific use cases.
- **Adapter extensions** — additional adapters for specific tools or systems.
- **Protocol extensions** — additional protocol operations.

## 3. Extension Rules

Extensions must:

- Preserve all AI-IDP invariants.
- Be versioned and identified.
- Document the extension's purpose, scope, and authority.
- Not weaken any conformance level.
- Not add new invariants that conflict with existing invariants.
- Be documented in the extension registry.

## 4. Extension Registry

The extension registry records all extensions. The registry includes:

- Extension identifier.
- Extension type.
- Extension version.
- Extension authority.
- Extension purpose.
- Extension scope.
- Extension conformance impact.

## 5. Invariants

- Extensions do not weaken invariants.
- Extensions are versioned and identified.
- Extensions are documented.
- Extensions are registered.
