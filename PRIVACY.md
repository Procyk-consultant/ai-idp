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
File: PRIVACY.md
Title: Privacy Policy
Purpose: Define privacy principles and handling
Audience: Privacy officers, regulators, data subjects
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Approved
Last Material Revision: 2026-08-16
Dependencies: spec/DISCLOSURE_PROTOCOL.md; government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md
Source Basis: Master Execution Prompt
Invariants: Personal information is minimized, sealed, and access-controlled
Failure Behaviour: Privacy failures are recorded as incidents
Trace Policy: Privacy-relevant events are first-class AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Privacy Policy

## Principles

Minimization: only the personal information necessary for identity, accountability, and audit is collected. Purpose limitation: personal information is used only for the declared purposes. Pseudonymization: user and principal identifiers are pseudonymous by default. Sealed records: sensitive personal information is sealed and access-controlled. Content separation: permanent metadata is separated from content; permanent records may contain a cryptographic commitment without retaining content. Access control: access to sealed records is logged, auditable, and subject to the applicable authorization model. Correction and revocation: corrections and revocations are new signed events. Retention: permanent minimal metadata and cryptographic commitments follow the AI-IDP permanent-record objective; full content follows a documented retention schedule and applicable legal requirements. Transparency: public registry projections are intended to expose only non-sensitive fields. Recourse: affected persons have a documented recourse mechanism.

## Privacy Verification

The recorded 2026-08-02 validation corpus includes privacy tests under `tests/privacy/` and privacy-related specification requirements. The historical 113/113 result remains the last executed full validation. Static reconciliation on the current branch has identified areas where the enforcement path and test depth should be strengthened before a future high-assurance release, including explicit public-tier projection/redaction and access-control integration. These branch changes are not represented as revalidated until a controlled test run is authorized.

The target privacy controls remain:

- pseudonymous principal/user identifiers by default;
- tiered disclosure (`PUBLIC`, `CONTROLLED`, `ORGANIZATION_PRIVATE`, `SEALED`);
- protected identity resolution;
- content separation and cryptographic commitments;
- auditable access to non-public records;
- append-only corrections and revocations;
- recourse for affected persons;
- data-minimization and purpose-limitation controls.

## Conflicts

Persistent traceability can conflict with privacy objectives involving retention, correction, disclosure, and erasure. AI-IDP's intended resolution uses minimal permanent metadata, cryptographic commitments, protected identity resolution, encrypted or access-controlled evidence payloads, sealed records, cryptographic agility, and append-only corrections rather than silent historical alteration. See `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md` for the detailed legal/policy analysis.

## Indigenous Data Governance

See `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md` and `research/synthesis/INDIGENOUS_DATA_GOVERNANCE_ANALYSIS.md` for the Indigenous data-governance analysis grounded in OCAP® principles, First Nations, Inuit, and Métis distinctions, and relevant reconciliation/data-sovereignty frameworks.

Meaningful rights-holder engagement is a required project objective **when a deployment materially affects Indigenous rights, community data, governance authority, or services**. It is not a universal implementation gate for deployments with no material Indigenous rights/data/governance nexus. Context-specific legal duties, agreements, and community governance requirements remain applicable where they exist.
