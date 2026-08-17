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
Status: Approved / reconciliation source implementation updated
Last Material Revision: 2026-08-17
Dependencies: spec/DISCLOSURE_PROTOCOL.md; government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md
Source Basis: Master Execution Prompt
Invariants: Personal information is minimized, sealed, and access-controlled
Failure Behaviour: Privacy failures are recorded as incidents
Trace Policy: Privacy-relevant events are first-class AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Privacy Policy

## Principles

Minimization: only the personal information necessary for identity, accountability, and audit is collected. Purpose limitation: personal information is used only for declared purposes. Pseudonymization: user and principal identifiers are pseudonymous by default. Sealed records: sensitive personal information is sealed and access-controlled. Content separation: permanent metadata is separated from content; permanent records may contain a cryptographic commitment without retaining content. Access control: access to sealed records is logged, auditable, and subject to the applicable authorization model. Correction and revocation: corrections and revocations are new signed events. Retention: permanent minimal metadata and cryptographic commitments follow the AI-IDP permanent-record objective; full content follows a documented retention schedule and applicable legal requirements. Transparency: public registry/event projections expose only explicitly reviewed non-sensitive fields. Recourse: affected persons have a documented recourse mechanism.

## Privacy Enforcement in the Reconciliation Source

The recorded 2026-08-02 validation corpus includes privacy tests under `tests/privacy/` and privacy-related specification requirements. The historical **113/113** result remains the last executed full validation and does not automatically validate the current branch.

The 2026-08-17 reconciliation source adds/hardens concrete privacy enforcement paths:

- allow-listed `PUBLIC` event proof projections rather than raw canonical event disclosure;
- non-public event non-enumeration through public event routes;
- public registry records only when explicitly marked public, with separate reviewed `public_attributes`;
- public verification-key export scoped to keys required by public event proofs and omitting private entity bindings by default;
- aggregate public verification status rather than internal failure-detail disclosure;
- action-intent approvals bound to visibility, preventing an approval for a private disclosure tier from being silently retargeted to `PUBLIC`;
- API proof-of-possession and replay protection before a governed public/private event can be accepted;
- signed federation public-resolution paths that reject unreviewed remote fields.

The corresponding privacy/API/federation test source has been strengthened, but these branch tests have **not been rerun** in this reconciliation session.

## Target Privacy Controls

The normative target remains:

- pseudonymous principal/user identifiers by default;
- tiered disclosure (`PUBLIC`, `CONTROLLED`, `ORGANIZATION_PRIVATE`, `SEALED`);
- protected identity resolution;
- content separation and cryptographic commitments;
- auditable access to non-public records;
- append-only corrections and revocations;
- recourse for affected persons;
- data-minimization and purpose-limitation controls;
- fail-closed public disclosure;
- authenticated/authorized controlled or sealed disclosure.

External IAM, regulator/judicial disclosure infrastructure, organizational access-control integration, and deployment-specific retention/legal requirements remain environment/institutional dependencies rather than claims of completed external deployment.

## Conflicts

Persistent traceability can conflict with privacy objectives involving retention, correction, disclosure, and erasure. AI-IDP's intended resolution uses minimal permanent metadata, cryptographic commitments, protected identity resolution, encrypted or access-controlled evidence payloads, sealed records, cryptographic agility, and append-only corrections rather than silent historical alteration. See `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md` for the detailed legal/policy analysis.

## Indigenous Data Governance

See `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md` and `research/synthesis/INDIGENOUS_DATA_GOVERNANCE_ANALYSIS.md` for the Indigenous data-governance analysis grounded in OCAP® principles, First Nations, Inuit, and Métis distinctions, and relevant reconciliation/data-sovereignty frameworks.

Meaningful rights-holder engagement is a required project objective **when a deployment materially affects Indigenous rights, community data, governance authority, or services**. It is not a universal implementation gate for deployments with no material Indigenous rights/data/governance nexus. Context-specific legal duties, agreements, and community governance requirements remain applicable where they exist.
