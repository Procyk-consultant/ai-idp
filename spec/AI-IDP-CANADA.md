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
File: spec/AI-IDP-CANADA.md
Title: AI-IDP Canada-Specific Specification
Purpose: Define Canada-specific requirements, jurisdiction, and legal interfaces
Audience: Legal reviewers, policy analysts, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: AI-IDP-CORE.md; FEDERAL_PROVINCIAL_JURISDICTION_ANALYSIS.md; CHARTER_ANALYSIS.md; PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Distinguishes current law from proposed law
Failure Behaviour: Misclassification of legal status is a defect
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# AI-IDP Canada-Specific Specification

## 1. Jurisdiction

AI-IDP is a proposed Canadian standard. Its primary jurisdiction is Canada. It applies to:

- AI agents hosted in Canada
- AI agents controlled from Canada
- AI agents supplied to Canadian users
- AI agents processing Canadian data
- AI agents acting on Canadian systems
- AI agents materially affecting persons in Canada
- AI agents used by Canadian governments
- AI agents used by federally regulated organizations
- AI agents used by provincially regulated organizations
- AI agents operated by foreign providers serving Canada

Foreign hosting is not a simple avoidance mechanism. The controlling organization remains accountable. See `government/FEDERAL_PROVINCIAL_JURISDICTION_ANALYSIS.md` for the detailed jurisdictional nexus test.

## 2. Current Legal Landscape

### 2.1 Federal

- **Constitution Acts 1867 and 1982** — division of powers; Charter of Rights and Freedoms.
- **Personal Information Protection and Electronic Documents Act (PIPEDA), S.C. 2000, c. 5** — private-sector privacy.
- **Privacy Act, R.S.C. 1985, c. P-21** — public-sector privacy.
- **Access to Information Act, R.S.C. 1985, c. A-1** — public-sector transparency.
- **Canada Evidence Act, R.S.C. 1985, c. C-5** — evidentiary standards.
- **Criminal Code, R.S.C. 1985, c. C-46** — computer crime, fraud, identity-related offences.
- **Copyright Act, R.S.C. 1985, c. C-42** — authorship and AI-generated works.
- **Treasury Board Directive on Automated Decision-Making** — public-sector automated decision systems; Algorithmic Impact Assessment (AIA).
- **Canadian Centre for Cyber Security guidance** — baseline cyber controls.
- **Communications Security Establishment (CSE) guidance** — signals and cyber.
- **Office of the Privacy Commissioner of Canada (OPC) guidance** — privacy interpretation and enforcement.

### 2.2 Proposed

- **Artificial Intelligence and Data Act (AIDA), Bill C-27** — proposed horizontal AI legislation (status: proposed, not enacted). AI-IDP references AIDA as proposed legislation only.

### 2.3 Provincial

- **Quebec Law 25** — private-sector privacy strengthening.
- **Quebec Quebec AI regulatory developments.
- **British Columbia PIPA** — private-sector privacy.
- **Alberta PIPA** — private-sector privacy.
- **Provincial freedom-of-information and privacy acts** — public-sector privacy.
- **Provincial consumer protection statutes** — consumer-facing AI.

AI-IDP's cooperative-federalism model preserves provincial authority over provincial matters while establishing a national minimum standard. See `government/FEDERAL_PROVINCIAL_JURISDICTION_ANALYSIS.md`.

## 3. Constitutional Analysis

The federal government's jurisdiction over AI agent identity and traceability is grounded in:

- **Trade and commerce** (s. 91(2)) — interprovincial and international AI services.
- **Criminal law** (s. 91(27)) — fraud, identity theft, computer crime facilitated by AI.
- **Peace, order, and good government** (s. 91 opening) — national concern doctrine for a novel regulatory subject.
- **Telecommunications** (s. 92(10)(a) federal jurisdiction over interprovincial telecommunications).
- **Paramountcy** — where federal and provincial law conflict, federal law prevails.

Provincial jurisdiction over property and civil rights (s. 92(13)) and matters of a merely local or private nature (s. 92(16)) supports provincial regulation of provincially regulated sectors. The cooperative model sets a national minimum while allowing provincial equivalent-or-stronger regimes.

See `government/CHARTER_ANALYSIS.md` for Charter implications, particularly:

- **s. 2(b)** freedom of expression — AI-assisted expression; chilling effects of registration.
- **s. 7** life, liberty, and security of the person — procedural fairness in accountability.
- **s. 8** unreasonable search and seizure — sealed-record access standards.
- **s. 15** equality — non-discrimination in registry access and recourse.

## 4. Privacy Analysis

Permanent traceability creates tension with privacy principles. The tension is resolved through:

- **Minimization** — permanent minimal metadata only.
- **Pseudonymization** — user and principal identifiers are pseudonymous by default.
- **Content separation** — permanent commitments, not plaintext content.
- **Sealed records** — sensitive information accessible under judicial or regulator authority.
- **Access logging** — all access to sealed records is logged and auditable.
- **Long-term signature migration** — cryptographic agility.
- **Append-only corrections** — no erasure of history; corrections are new signed events.

See `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md` for the detailed analysis, including PIPEDA's principles (consent, limited collection, limited use, accuracy, safeguards, openness, individual access, challenging compliance), the Privacy Act's application to public-sector AI, and provincial privacy statutes.

## 5. Indigenous Data Governance

AI-IDP recognizes Indigenous data sovereignty. The analysis in `research/synthesis/INDIGENOUS_DATA_GOVERNANCE_ANALYSIS.md` is grounded in:

- **OCAP® principles** (First Nations Information Governance Centre) — Ownership, Control, Access, Possession.
- **First Nations, Inuit, and Métis distinctions** — different nations have different governance authority.
- **TRC Calls to Action** — particularly Calls to Action 43–44 (adoption and implementation of UNDRIP) and 7, 18, 19 (aboriginal health and reconciliation).
- **Community-controlled access** — registry access for Indigenous community data is governed by the community.

Consultation with rights-holders is a precondition for implementation. AI-IDP does not override Indigenous data governance; it provides hooks for community-controlled access and dispute resolution.

## 6. Administrative Implementation

The administrative implementation is defined in `administration/ADMINISTRATIVE_IMPLEMENTATION_PLAN.md`:

- **National registry authority** — operator of the public and controlled tiers.
- **Sectoral registry authorities** — for regulated sectors (finance, healthcare, public sector).
- **Provincial registry authorities** — where provinces establish equivalent regimes.
- **Certification bodies** — accredited conformity assessors.
- **Auditor registry** — accredited auditors.
- **Incident coordinator** — national coordinator for cross-sectoral AI incidents.
- **Public-sector profile** — federal, provincial, municipal government deployments.
- **Private-sector profile** — commercial deployments.
- **Open-source profile** — open-source agent compliance.
- **Small-developer profile** — reduced-burden path for small developers.
- **Offline profile** — offline-capable agents.

## 7. Enforcement

Enforcement options are analyzed in `government/ENFORCEMENT_OPTIONS.md`:

- **Civil penalties** — administrative monetary penalties.
- **Criminal liability** — for fraudulent attribution, evidence tampering, or operating without registration.
- **Service suspension** — regulator authority to suspend non-compliant services.
- **Procurement bar** — non-compliant agents are barred from federal procurement.
- **Civil liability** — statutory civil liability for harms caused by non-compliant operation.
- **Evidentiary consequences** — non-compliant operation creates evidentiary presumptions.

See `government/PENALTY_OPTIONS.md` and `government/CIVIL_LIABILITY_OPTIONS.md` for the detailed analysis.

## 8. Procurement

Federal procurement profile is defined in `government/FEDERAL_PROCUREMENT_PROFILE.md`. The profile integrates with the Treasury Board Contracting Policy and the Directive on Automated Decision-Making. AI agents acquired through federal procurement must be registered at conformance level L3 or higher.

## 9. Algorithmic Impact Assessment

The AIA extension proposal is defined in `government/AIA_EXTENSION_PROPOSAL.md`. The extension adds AI-IDP registration as a required field in the AIA, with trace-evidence requirements for high-impact automated decisions.

## 10. Standards Route

The Standards Council route materials are `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.md`, `research/synthesis/STANDARDS_CROSSWALK.md`, and the normative `spec/` set. They support a proposed AI-IDP National Standard of Canada review; no external submission has been performed.

## 11. Legislative Route

The draft statute is in `government/PROPOSED_AI_ACTOR_IDENTITY_AND_TRACEABILITY_ACT.md`. The legislative instructions are in `government/LEGISLATIVE_INSTRUCTIONS.md`. The draft statutory provisions for legal review are in `government/DRAFT_STATUTORY_PROVISIONS_FOR_LEGAL_REVIEW.md`. The draft regulatory framework is in `government/DRAFT_REGULATORY_FRAMEWORK.md`.

## 12. Public Consultation

The public consultation package is in `government/PUBLIC_CONSULTATION_PACKAGE.md`. The parliamentary committee brief is in `government/PARLIAMENTARY_COMMITTEE_BRIEF.md`.

## 13. Distinguishing Current from Proposed

AI-IDP documents consistently distinguish:

- **Current law** (e.g., PIPEDA, Privacy Act, provincial privacy statutes, Criminal Code computer-crime provisions).
- **Current regulation** (e.g., AIA under the Treasury Board Directive).
- **Current policy** (e.g., federal AI strategy).
- **Current guidance** (e.g., OPC guidance, CCCS guidance).
- **Current voluntary codes** (e.g., industry codes of conduct).
- **Current standards** (e.g., ISO/IEC standards adopted in Canada).
- **Proposed legislation** (e.g., AIDA under Bill C-27; Quebec Quebec AI regulatory developments.
- **Expired legislation** (none referenced in this version).
- **Pending legislation** (e.g., AIDA at committee stage).
- **Proposed AI-IDP requirements** (the AI-IDP standard itself).
- **Proposed future legal obligations** (the AI-IDP-based legislative proposal).

Documents that misclassify the legal status of any instrument are defective and must be corrected.

## 14. Compliance Profiles

AI-IDP defines compliance profiles for:

- **Federal public sector** — Treasury Board AIA integration; federal procurement profile.
- **Provincial public sector** — provincial AIA-equivalent integration; provincial procurement profile.
- **Federally regulated private sector** — telecom, banking, transportation.
- **Provincially regulated private sector** — healthcare, education, provincial consumer protection.
- **Open source** — reduced-burden path with conformance level L1–L2.
- **Small developer** — tiered fees, reduced audit frequency, mentorship.
- **Offline agent** — offline-mode protocol with periodic reconciliation.
- **Critical infrastructure** — heightened conformance level L4; sectoral certification.

See `government/PUBLIC_SECTOR_IMPLEMENTATION_PROFILE.md`, `government/PRIVATE_SECTOR_IMPLEMENTATION_PROFILE.md`, `government/OPEN_SOURCE_COMPLIANCE_PROFILE.md`, `government/SMALL_DEVELOPER_COMPLIANCE_PROFILE.md`, `government/OFFLINE_AGENT_COMPLIANCE_PROFILE.md`.

## 15. Effective Date

AI-IDP's effective date is contingent on:

- Legislative authorization (if the legislative route is pursued)
- Standards Council of Canada adoption (if the standards route is pursued)
- Treasury Board Directive amendment (if the administrative route is pursued)
- Provincial agreement (if the cooperative federalism model is pursued)

AI-IDP's effective date is **not** triggered by this preparation. The preparation produces a submission-ready proposal; the effective date is determined by the authorizing body.
