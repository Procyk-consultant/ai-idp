---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
File: FILING_INSTRUCTIONS.md
Title: Filing Instructions — What Goes Where, To Who, Why, What For
Purpose: Practical guide for Pierre-Edward Procyk to sort, file, and submit project documents
Audience: Pierre-Edward Procyk (only)
Document Classification: Confidential
Version: 2.0.0
Status: Final
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Filing Instructions

**For:** Pierre-Edward Procyk
**Date:** Saturday 1 August 2026
**Project root:** `C:\Cognitive Industries\AI-IDP-AegisTrace`

This guide tells you what each document is, who it's for, where to send it, why it exists, and what for. Read this before filing anything.

---

## 1. Documents You File Yourself (Require Your Credentials)

These are the documents that only you can submit because they require accounts in your name. I cannot submit them for you.

### 1.1 arXiv Submission

| Field | Value |
|-------|-------|
| **What** | `paper/main.tex` + `paper/references.bib` + `paper/main.pdf` |
| **Where** | https://arxiv.org/submit |
| **Who** | You (requires your arXiv account + ORCID) |
| **Why** | To establish academic priority and make the research public |
| **What for** | Academic publication; citable reference for the framework |
| **Category** | Primary: `cs.CY` (Computers and Society); Cross-list: `cs.CR` (Cryptography and Security) |
| **Format** | Upload `main.tex` and `references.bib` as a single .zip; arXiv compiles it |
| **Licence** | Select arXiv's non-exclusive licence at submission time |
| **Check before submitting** | Read `paper/README_SUBMISSION.md` for the step-by-step checklist |

### 1.2 Government Submission

| Field | Value |
|-------|-------|
| **What** | `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.pdf` (primary document) |
| **Supporting** | `government/CANADIAN_POLICY_WHITE_PAPER.pdf`, `government/PROPOSED_AI_ACTOR_IDENTITY_AND_TRACEABILITY_ACT.md`, `government/FEDERAL_PROVINCIAL_JURISDICTION_ANALYSIS.pdf`, `government/CHARTER_ANALYSIS.pdf`, `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.pdf` |
| **Where** | Contact your MP or the Minister of Innovation, Science and Economic Development; or submit via the Treasury Board Secretariat consultation process |
| **Who** | You (as the project originator and IP owner) |
| **Why** | To propose AI-IDP as a national standard and legislative framework |
| **What for** | Policy adoption; legislative consideration; national standards route |
| **Format** | PDF for formal submission; DOCX if editable versions are requested |
| **Cover letter** | Use `brand/CONTACT_BLOCKS.md` — the "Government Proposal" block |

### 1.3 Standards Council of Canada Submission

| Field | Value |
|-------|-------|
| **What** | Standards-route materials: `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.md`, `research/synthesis/STANDARDS_CROSSWALK.md`, and the normative `spec/` documents |
| **Where** | https://www.scc.ca/en/standards/proposing-a-standard |
| **Who** | You (requires SCC account) |
| **Why** | To propose AI-IDP as a National Standard of Canada |
| **What for** | Voluntary national standard; certification framework basis |
| **Format** | Follow SCC's standards proposal template; use the technical specification (`spec/`) as normative content |

### 1.4 University Submission (if applicable)

| Field | Value |
|-------|-------|
| **What** | `university/UNIVERSITY_RESEARCH_REPORT.pdf` |
| **Where** | Your university department (if you are affiliated with one) |
| **Who** | You |
| **Why** | Academic review; potential supervision; degree credit (if applicable) |
| **What for** | Academic credential; peer review feedback |
| **Note** | No university affiliation is invented. The report uses a neutral academic format. If you are not affiliated with a university, you can still share the report informally with academic contacts. |

---

## 2. Documents for Your Records (Do Not Submit)

These are internal documents you keep for your own reference, governance, and audit trail.

### 2.1 Project Control

| File | What it is | Why you keep it |
|------|-----------|----------------|
| `project-control/VERIFIED_AUTHOR_DATA.md` | Your verified identity and contact data | Single source of truth for all identity fields |
| `project-control/VERIFIED_CONTACT_DATA.json` | Machine-readable contact data | For scripts and tools |
| `project-control/MISSING_AUTHOR_DATA.md` | List of fields you did NOT provide | Prevents fabrication; documents gaps |
| `project-control/DECISION_LOG.md` | All autonomous decisions made during execution | Audit trail; shows reasoning |
| `project-control/ASSUMPTION_REGISTER.md` | All assumptions made | Audit trail; transparency |
| `project-control/RISK_REGISTER.md` | All identified risks | Risk management |
| `project-control/LEGAL_STATUS_UPDATE_v1.1.0.md` | Updated legal status (Bill C-27 died, CAISI established, etc.) | Critical for legal accuracy |
| `project-control/PUBLICATION_METADATA_STATUS.md` | Tracks that no external submission was performed | Proves no premature submission |
| `project-control/HANDOFF.md` | Handoff state for future work | If you resume work later |

### 2.2 Brand Assets

| File | What it is | Why you keep it |
|------|-----------|----------------|
| `brand/originals/` | Your 3 official logo PNGs (preserved verbatim) | Brand assets; never modify |
| `brand/originals/SHA256SUMS.txt` | Checksums of the originals | Verify integrity |
| `brand/AUTHOR_IDENTITY.md` | How your identity appears on documents | Consistency reference |
| `brand/CONTACT_BLOCKS.md` | Reusable contact blocks for different contexts | Copy-paste for correspondence |
| `brand/DOCUMENT_IDENTITY_RULES.md` | Header rules for all files | Consistency reference |

### 2.3 IP and Licensing

| File | What it is | Why you keep it |
|------|-----------|----------------|
| `AUTHORSHIP_AND_IP.md` | IP declaration | Legal protection |
| `LICENSING_STATUS.md` | No licence applied (yet) | Controls licensing decisions |
| `TRADEMARK_AND_BRAND_POLICY.md` | Brand protection rules | Protects your trademarks |
| `NOTICE.md` | Third-party attributions | Legal compliance |

---

## 3. Documents for Specific Audiences (Share on Request)

### 3.1 For Legal Reviewers

| File | What it is | Who to share with | Why |
|------|-----------|-------------------|-----|
| `government/PROPOSED_AI_ACTOR_IDENTITY_AND_TRACEABILITY_ACT.md` | Draft statute | Legislative counsel; constitutional lawyer | Legal review before introduction |
| `government/FEDERAL_PROVINCIAL_JURISDICTION_ANALYSIS.pdf` | Jurisdiction analysis | Constitutional lawyer; policy advisor | Validates federal jurisdiction |
| `government/CHARTER_ANALYSIS.pdf` | Charter compliance analysis | Constitutional lawyer | Validates Charter compliance |
| `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.pdf` | Privacy/HR analysis | Privacy lawyer; OPC; civil liberties orgs | Validates privacy compliance |

### 3.2 For Technical Reviewers / Architects

| File | What it is | Who to share with | Why |
|------|-----------|-------------------|-----|
| `technical/AEGISTRACE_TECHNICAL_ARCHITECTURE.pdf` | Technical architecture | CTOs; architects; implementers | Technical evaluation |
| `spec/` (25 specification documents) | Formal specification | Standards bodies; implementers | Normative reference |
| `schemas/` (14 JSON schemas) | JSON Schemas | Developers; integrators | Implementation reference |
| `threat-model/THREAT_MODEL.md` | Threat model (24 threats) | Security researchers; auditors | Security evaluation |

### 3.3 For Policy Analysts and Civil Society

| File | What it is | Who to share with | Why |
|------|-----------|-------------------|-----|
| `government/CANADIAN_POLICY_WHITE_PAPER.pdf` | Policy white paper | Policy analysts; think tanks; civil society | Policy advocacy |
| `impact/societal/SOCIETAL_IMPACT_ASSESSMENT.pdf` | Societal impact | Civil society organizations; public consultation | Public interest evaluation |
| `impact/human-resources/HR_AND_LABOUR_IMPACT_REPORT.pdf` | HR/labour impact | Labour unions; HR associations; employment lawyers | Worker impact evaluation |
| `impact/business-and-operations/BUSINESS_AND_OPERATIONS_IMPACT_REPORT.pdf` | Business impact | Business associations; chambers of commerce | Economic evaluation |

### 3.4 For Indigenous Communities and Organizations

| File | What it is | Who to share with | Why |
|------|-----------|-------------------|-----|
| `research/synthesis/INDIGENOUS_DATA_GOVERNANCE_ANALYSIS.md` | Indigenous data governance analysis | First Nations, Inuit, and Métis organizations; FNIGC; ITK; MNC | Consultation precondition |
| `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.pdf` (Section on Indigenous data) | Privacy/HR analysis (Indigenous section) | Same as above | Same as above |
| **Important** | Consultation with rights-holders is a precondition for implementation. Do not proceed with implementation without meaningful consultation. | | |

### 3.5 For Implementers and Developers

| File | What it is | Who to share with | Why |
|------|-----------|-------------------|-----|
| `docs/quickstart.md` | Quickstart guide | Developers | Onboarding |
| `docs/developer-guide.md` | Developer guide | Developers | Implementation reference |
| `docs/architecture-guide.md` | Architecture guide | Architects | Design reference |
| `docs/api-guide.md` | API guide | Integrators | API reference |
| `docs/cli-guide.md` | CLI guide | Operators; auditors | CLI reference |
| `examples/` | Worked examples | Developers | Reference implementations |
| `src/aegistrace/` | Reference implementation | Developers; implementers | Code reference |

### 3.6 For Auditors and Regulators

| File | What it is | Who to share with | Why |
|------|-----------|-------------------|-----|
| `docs/auditor-guide.md` | Auditor guide | Auditors; certification bodies | Audit procedure reference |
| `docs/regulator-guide.md` | Regulator guide | Regulators (OPC; CAISI; sectoral regulators) | Regulatory oversight reference |
| `spec/AUDIT_PROTOCOL.md` | Audit protocol | Auditors | Normative audit reference |
| `spec/REGISTRY_PROTOCOL.md` | Registry protocol | Regulators; registry operators | Normative registry reference |
| `spec/CERTIFICATION_PROTOCOL.md` | Certification protocol | Certification bodies | Normative certification reference |

### 3.7 For French-Speaking Audiences

| File | What it is | Who to share with | Why |
|------|-----------|-------------------|-----|
| `government/NOTE_DE_SYNTHESE_FR.pdf` | French executive summary | Francophone policymakers; Quebec government; French-speaking public | Bilingual access |
| `technical/ARCHITECTURE_TECHNIQUE_FR.pdf` | French technical summary | Francophone architects; implementers | Bilingual access |
| `impact/IMPACT_CANADIEN_FR.pdf` | French impact summary | Francophone civil society; Quebec public | Bilingual access |

---

## 4. Release Package

| File | What it is | What for |
|------|-----------|----------|
| `AI-IDP-01-ARXIV-PAPER.zip` through `AI-IDP-10-ROOT-AND-DELIVERABLES.zip` | Ten audience- and function-specific project packages | Backup; transfer; controlled submission packages |
| `release/NUMBERED_ARCHIVES.sha256` | Hashes for the ten numbered packages | Verify package integrity |
| `release/CHECKSUMS.sha256` | Checksums for all files | Verify any individual file |
| `release/VALIDATION_REPORT.md` | Independent validation report | Evidence of quality |
| `release/FINAL_COMPLETION_REPORT.md` | Consolidated completion report | Status overview |
| `release/release_summary.json` | Machine-readable summary | Quick reference |
| `release/metadata/` | Author, org, contact, publication metadata | Machine-readable metadata |

---

## 5. Filing Checklist for Saturday 1 August 2026

### Before You Start
- [ ] Read this document completely
- [ ] Read `project-control/LEGAL_STATUS_UPDATE_v2.0.0.md` for the latest legal status
- [ ] Verify your contact data in `project-control/VERIFIED_AUTHOR_DATA.md`
- [ ] Verify every numbered ZIP against `release/NUMBERED_ARCHIVES.sha256` and CRC-test each package

### If Filing to arXiv
- [ ] Read `paper/README_SUBMISSION.md`
- [ ] Create a `.zip` of `paper/main.tex` and `paper/references.bib`
- [ ] Log in to https://arxiv.org/submit
- [ ] Select category `cs.CY` with cross-list `cs.CR`
- [ ] Paste the abstract from `paper/main.tex`
- [ ] Upload the `.zip`
- [ ] Select a licence (arXiv non-exclusive or your chosen licence)
- [ ] Submit

### If Filing to Government
- [ ] Print `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.pdf`
- [ ] Attach a cover letter using the "Government Proposal" block from `brand/CONTACT_BLOCKS.md`
- [ ] Include supporting documents (white paper, draft statute, jurisdiction analysis, Charter analysis, privacy analysis)
- [ ] Send to your MP and/or the Minister of ISED
- [ ] Consider also sending to the Treasury Board Secretariat (for AIA integration)

### If Filing to Standards Council of Canada
- [ ] Visit https://www.scc.ca/en/standards/proposing-a-standard
- [ ] Follow the SCC's standards proposal process
- [ ] Use `spec/` as the normative technical content
- [ ] Use `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.pdf` as the cover document and include `research/synthesis/STANDARDS_CROSSWALK.md` plus the normative specification set as supporting material

### For Your Records
- [ ] Save copies of all ten numbered release packages and `release/NUMBERED_ARCHIVES.sha256` to secure backup
- [ ] Save a copy of `release/CHECKSUMS.sha256` to verify future integrity
- [ ] Record what you submitted, where, and when in a personal log

---

## 6. Important Notes

### What NOT to Do
- **Do NOT** apply a public licence without your explicit written authorization
- **Do NOT** modify the brand originals in `brand/originals/`
- **Do NOT** generate a replacement logo
- **Do NOT** invent author, organization, contact, or business data
- **Do NOT** release synthetic data as empirical observation
- **Do NOT** proceed with implementation without Indigenous data-governance consultation
- **Do NOT** suppress criticism, contradictions, or negative findings

### What to Do Before Any External Submission
1. Verify the archive checksum matches
2. Verify the test suite passes from the root: `.\.venv\Scripts\python.exe -m pytest tests\ -v`
3. Verify the paper compiles: `Set-Location -LiteralPath 'C:\Cognitive Industries\AI-IDP-AegisTrace\paper'; tectonic main.tex`
4. Read `project-control/LEGAL_STATUS_UPDATE_v2.0.0.md` for the latest legal status
5. Confirm you are the sole authority for external publication

### Who to Contact
- **You (Pierre-Edward Procyk):** p.procyk.media@gmail.com, +1 (581) 668-2372
- **Secondary email:** p.1o9.cognitive@outlook.com
- **LinkedIn:** linkedin.com/in/pierre-edward-procyk-223b75305

### Date
All documents are dated **Saturday 1 August 2026**.

---

## 7. Quick Reference: Document-to-Audience Map

```
arXiv paper (paper/main.tex)
  → You submit to arxiv.org

Government proposal (government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.pdf)
  → You submit to MP / Minister of ISED / Treasury Board

Policy white paper (government/CANADIAN_POLICY_WHITE_PAPER.pdf)
  → Share with policy analysts, civil society, public consultation

Draft statute (government/PROPOSED_AI_ACTOR_IDENTITY_AND_TRACEABILITY_ACT.md)
  → Share with legislative counsel for legal review

Technical architecture (technical/AEGISTRACE_TECHNICAL_ARCHITECTURE.pdf)
  → Share with CTOs, architects, implementers

Impact reports (impact/*/)
  → Share with business, HR, societal stakeholders

University report (university/UNIVERSITY_RESEARCH_REPORT.pdf)
  → Share with academic contacts (if applicable)

French translations (government/NOTE_DE_SYNTHESE_FR.pdf, etc.)
  → Share with Francophone audiences, Quebec government

Numbered release suite (AI-IDP-01 through AI-IDP-10) plus release/NUMBERED_ARCHIVES.sha256
  → Keep for your records; transfer if needed

Reference implementation (src/aegistrace/)
  → Share with developers; basis for GitHub repo (when authorized)
```

---

© 2026 Pierre-Edward Procyk. Cognitive Industries — Les Industries Cognitives. All rights reserved.
