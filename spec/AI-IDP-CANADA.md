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
Last Material Revision: 2026-08-14
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

### 2.2 Proposed / Historical Reference

- **Artificial Intelligence and Data Act (AIDA), Bill C-27** — former proposed horizontal AI legislation; not enacted. AI-IDP uses it only as a historical/proposed-policy reference where relevant.

### 2.3 Provincial

- **Quebec Law 25** — private-sector privacy strengthening.
- **Quebec AI regulatory developments** — monitor for current status before external legal reliance.
- **British Columbia PIPA** — private-sector privacy.
- **Alberta PIPA** — private-sector privacy.
- **Provincial freedom-of-information and privacy acts** — public-sector privacy.
- **Provincial consumer protection statutes** — consumer-facing AI.

AI-IDP's cooperative-federalism model is an intended standards and implementation architecture designed to preserve provincial authority over provincial matters while enabling a national minimum standard. See `government/FEDERAL_PROVINCIAL_JURISDICTION_ANALYSIS.md`.

## 3. Constitutional Analysis

The project proposes federal and cooperative implementation routes based on potential heads of power including:

- **Trade and commerce** (s. 91(2)) — interprovincial and international AI services.
- **Criminal law** (s. 91(27)) — fraud, identity theft, computer crime facilitated by AI.
- **Peace, order, and good government** (s. 91 opening) — potential national-concern arguments for a novel regulatory subject.
- **Telecommunications** (s. 92(10)(a)) — interprovincial telecommunications contexts.

Provincial jurisdiction over property and civil rights (s. 92(13)) and matters of a merely local or private nature (s. 92(16)) supports provincial regulation of provincially regulated sectors. The proposed cooperative model targets a national baseline while allowing equivalent-or-stronger provincial regimes.

See `government/CHARTER_ANALYSIS.md` for Charter implications, particularly:

- **s. 2(b)** freedom of expression — AI-assisted expression; chilling effects of registration.
- **s. 7** life, liberty, and security of the person — procedural fairness in accountability.
- **s. 8** unreasonable search and seizure — sealed-record access standards.
- **s. 15** equality — non-discrimination in registry access and recourse.

## 4. Privacy Analysis

Permanent traceability creates tension with privacy principles. The proposed standard addresses that tension through:

- **Minimization** — permanent minimal metadata only.
- **Pseudonymization** — user and principal identifiers are pseudonymous by default.
- **Content separation** — permanent commitments, not plaintext content.
- **Sealed records** — sensitive information accessible under judicial or regulator authority where legally authorized.
- **Access logging** — all access to sealed records is logged and auditable.
- **Long-term signature migration** — cryptographic agility.
- **Append-only corrections** — no erasure of history; corrections are new signed events.

See `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md` for the detailed analysis.

## 5. Indigenous Data Governance

AI-IDP recognizes Indigenous data sovereignty as an important design objective where Indigenous rights, community data, governance authority, or services are materially involved. The analysis in `research/synthesis/INDIGENOUS_DATA_GOVERNANCE_ANALYSIS.md` is grounded in:

- **OCAP® principles** (First Nations Information Governance Centre) — Ownership, Control, Access, Possession.
- **First Nations, Inuit, and Métis distinctions** — different nations have different governance authority.
- **TRC Calls to Action** — considered as policy/design objectives where relevant to the deployment context.
- **Community-controlled access** — supported for Indigenous community data where applicable.

Meaningful rights-holder engagement should occur before deployments that materially affect Indigenous rights, community data, governance authority, or services, using distinctions-based protocols appropriate to the affected community or nation. **This is not a universal implementation prerequisite for unrelated AI-IDP deployments.** AI-IDP does not override applicable Indigenous rights or data-governance obligations; it provides technical hooks for community-controlled access, sealed evidence, and dispute-resolution workflows where they are required.

## 6. Administrative Implementation

The administrative implementation is defined in `administration/ADMINISTRATIVE_IMPLEMENTATION_PLAN.md` as a target operating model:

- **National registry authority** — proposed operator of the public and controlled tiers.
- **Sectoral registry authorities** — proposed for regulated sectors (finance, healthcare, public sector).
- **Provincial registry authorities** — where provinces establish equivalent regimes.
- **Certification bodies** — proposed accredited conformity assessors.
- **Auditor registry** — proposed accredited auditors.
- **Incident coordinator** — proposed national coordinator for cross-sectoral AI incidents.
- **Public-sector profile** — federal, provincial, municipal government deployments.
- **Private-sector profile** — commercial deployments.
- **Open-source profile** — open-source agent compliance.
- **Small-developer profile** — reduced-burden path for small developers.
- **Offline profile** — offline-capable agents.

## 7. Enforcement

Enforcement options are proposed and analyzed in `government/ENFORCEMENT_OPTIONS.md`:

- **Civil penalties** — administrative monetary penalties.
- **Criminal liability** — for fraudulent attribution, evidence tampering, or unlawful operation if enacted.
- **Service suspension** — potential regulator authority to suspend non-compliant services.
- **Procurement bar** — potential procurement consequence for non-conforming agents.
- **Civil liability** — potential statutory civil liability for harms caused by non-compliant operation.
- **Evidentiary consequences** — potential evidentiary presumptions tied to non-compliant operation.

See `government/PENALTY_OPTIONS.md` and `government/CIVIL_LIABILITY_OPTIONS.md` for the detailed proposals.

## 8. Procurement

The proposed federal procurement profile is defined in `government/FEDERAL_PROCUREMENT_PROFILE.md`. The target model would integrate with Treasury Board procurement and automated-decision governance. Under the proposed AI-IDP standard, federal procurement of higher-risk AI agents would require elevated conformance levels such as L3 or higher. This is a proposed requirement, not current federal procurement law.

## 9. Algorithmic Impact Assessment

The proposed AIA extension is defined in `government/AIA_EXTENSION_PROPOSAL.md`. The target design adds AI-IDP registration and trace-evidence fields for relevant automated decisions. It is a proposed extension, not a current Treasury Board requirement.

## 10. Standards Route

The Standards Council route materials are `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.md`, `research/synthesis/STANDARDS_CROSSWALK.md`, and the normative `spec/` set. They support a proposed AI-IDP National Standard of Canada review; no external submission has been performed.

## 11. Legislative Route

The draft statute is in `government/PROPOSED_AI_ACTOR_IDENTITY_AND_TRACEABILITY_ACT.md`. The legislative instructions are in `government/LEGISLATIVE_INSTRUCTIONS.md`. The draft statutory provisions for legal review are in `government/DRAFT_STATUTORY_PROVISIONS_FOR_LEGAL_REVIEW.md`. The draft regulatory framework is in `government/DRAFT_REGULATORY_FRAMEWORK.md`.

## 12. Public Consultation

The public consultation package is in `government/PUBLIC_CONSULTATION_PACKAGE.md`. The parliamentary committee brief is in `government/PARLIAMENTARY_COMMITTEE_BRIEF.md`.

## 13. Distinguishing Current from Proposed

AI-IDP documents are required to distinguish:

- **Current law** — enacted statutes and regulations currently in force.
- **Current policy/directives** — operative administrative instruments.
- **Current guidance** — regulator or government guidance.
- **Current voluntary codes** — non-binding codes and commitments.
- **Current standards** — standards actually adopted or recognized by the relevant standards body.
- **Historical or expired proposals** — including legislation that did not become law.
- **Proposed AI-IDP requirements** — the AI-IDP standard itself.
- **Proposed future legal obligations** — the AI-IDP-based legislative and administrative proposals.

Documents that misclassify the legal status of any instrument are defective and must be corrected.

## 14. Compliance Profiles

AI-IDP defines target compliance profiles for:

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

AI-IDP's effective date is contingent on the adoption route pursued, including one or more of:

- Legislative authorization
- Standards Council of Canada adoption or another recognized standards route
- Treasury Board or other administrative adoption
- Provincial agreement or equivalent provincial implementation
- Contractual/procurement adoption in organizations choosing to implement the standard voluntarily

AI-IDP's effective date is **not** triggered by this preparation. The preparation defines the target standard and submission-ready proposal; legal or institutional enforceability is determined by the applicable authorizing or adopting body.
