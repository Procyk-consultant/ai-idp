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
File: PRIVACY.md
Title: Privacy Policy
Purpose: Define privacy principles and handling
Audience: Privacy officers, regulators, data subjects
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Approved
Last Material Revision: 2026-08-01
Dependencies: spec/DISCLOSURE_PROTOCOL.md; government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md
Source Basis: Master Execution Prompt
Invariants: Personal information is minimized, sealed, and access-controlled
Failure Behaviour: Privacy failures are recorded as incidents
Trace Policy: Privacy-relevant events are first-class AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Privacy Policy

## Principles

Minimization: only the personal information necessary for identity, accountability, and audit is collected. Purpose limitation: personal information is used only for the declared purposes. Pseudonymization: user and principal identifiers are pseudonymous by default. Sealed records: sensitive personal information is sealed and access-controlled. Content separation: permanent metadata is separated from content; permanent records may contain a cryptographic commitment without retaining content. Access control: access to sealed records is logged, auditable, and subject to judicial or regulator-controlled disclosure. Correction and revocation: corrections and revocations are new signed events. Retention: permanent minimal metadata and cryptographic commitments are retained indefinitely; full content is retained according to a documented schedule. Transparency: public registry entries expose only non-sensitive fields. Recourse: affected persons have a documented recourse mechanism.

## Privacy Tests

The AegisTrace reference implementation enforces these properties via `tests/privacy/`: user enumeration prevention; public-registry leakage prevention; path exposure prevention; prompt and output exposure prevention; correlation resistance; employee-monitoring exposure prevention; evidence redaction correctness; access control correctness; sealed identity resolution correctness.

## Conflicts

Permanent traceability may conflict with privacy (retention, correction, erasure). The conflict is resolved through permanent minimal metadata, permanent cryptographic commitments, protected identity resolution, encrypted evidence payloads, access-controlled vaults, sealed records, long-term signature migration, and append-only corrections (not erasure). See `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md` for the detailed analysis.

## Indigenous Data Governance

See `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md` and `research/synthesis/INDIGENOUS_DATA_GOVERNANCE_ANALYSIS.md` for the Indigenous data-governance analysis grounded in OCAP® principles, First Nations, Inuit, and Métis distinctions, and TRC Calls to Action. Consultation with rights-holders is a precondition for implementation.
