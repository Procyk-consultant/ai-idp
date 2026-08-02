---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
File: project-control/LEGAL_STATUS_UPDATE_v2.0.0.md
Title: Legal Status Update (v2.0.0)
Purpose: Update legal status based on deeper citation chaining (depth 3+)
Audience: Legal reviewers, policy analysts
Document Classification: Public
Classification: research
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: project-control/ASSUMPTION_REGISTER.md; project-control/SOURCE_GAP_REGISTER.md
Source Basis: Web search of Canadian primary sources (July 2026)
Invariants: Distinguishes current law from proposed law
Failure Behaviour: Misclassification of legal status is a defect
Trace Policy: No AegisTrace event record required
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Legal Status Update (v2.0.0)

## Purpose

This document updates the legal status of Canadian AI governance instruments based on deeper citation chaining (depth 3+) performed via web search in July 2026. The original v1.0.0 documents referenced AIDA under Bill C-27 as "proposed, not enacted." Deeper citation chaining revealed that Bill C-27 died on the Order Paper when Parliament was prorogued on 6 January 2025. This update corrects the legal status throughout the project.

## Key Findings from Deeper Citation Chaining

### 1. Bill C-27 (AIDA) — Status Update

**Original v1.0.0 statement:** "The proposed Artificial Intelligence and Data Act (AIDA), Bill C-27, is the most recent federal horizontal AI bill of record. AI-IDP references AIDA as proposed legislation (not enacted)."

**Updated v1.1.0 statement:** "Bill C-27 (containing the proposed Artificial Intelligence and Data Act, AIDA) died on the Order Paper when Parliament was prorogued on 6 January 2025. AIDA was not enacted. A replacement bill was expected in 2026 but had not been introduced as of July 2026."

**Sources:**
- Dentons Canada LLP (2025): "With the prorogation of Parliament on January 6, 2025, until March 24, 2025, Bill C-27 died on the order paper." https://www.dentons.com/en/insights/newsletters/2025/january/23/global-regulatory-trends-to-watch/dentons-canadian-regulatory-trends-to-watch-in-2025/artificial-intelligence-trends-to-watch-in-2025
- Schwartz Reisman Institute for Technology and Society (University of Toronto): "What's Next After AIDA?" https://srinstitute.utoronto.ca/news/whats-next-for-aida
- LEGISinfo (Parliament of Canada): https://www.parl.ca/legisinfo/en/bill/44-1/c-27
- ISED AIDA Companion Document: https://ised-isde.canada.ca/site/innovation-better-canada/en/artificial-intelligence-and-data-act-aida-companion-document

**Impact on AI-IDP:** The framework's distinction between "current law" and "proposed law" is strengthened. AIDA is no longer "proposed legislation pending"; it is "expired proposed legislation not reintroduced." The legislative route proposed in the AI Actor Identity and Traceability Act remains valid and is independent of AIDA.

### 2. Canadian AI Safety Institute (CAISI) — Status Update

**Original v2.0.0 statement:** CAISI referenced as a Canadian primary source.

**Updated v2.0.0 statement:** "The Canadian Artificial Intelligence Safety Institute (CAISI) was established in November 2024 as a federal initiative under Innovation, Science and Economic Development Canada, with a mandate to advance scientific understanding of risks associated with advanced AI systems. CAISI operates in partnership with CIFAR."

**Sources:**
- ISED Canada: https://ised-isde.canada.ca/site/ised/en/canadian-artificial-intelligence-safety-institute
- CAISI official site: https://aisafety.ca/about
- ISED news release (July 2025): https://www.canada.ca/en/innovation-science-economic-development/news/2025/07/government-of-canada-partners-with-united-kingdom-to-invest-in-groundbreaking-ai-alignment-research.html
- CAISI 2025 Year in Review (CIFAR): https://report.buildingsafeai.ca/caisi-2025-year-in-review

**Impact on AI-IDP:** CAISI is identified as the natural home for AI-IDP technical research and incident coordination. The administrative implementation plan should reference CAISI as the national AI safety body that would host or coordinate the AI-IDP registry authority.

### 3. Canada's National AI Strategy ("AI for All") — New Finding

**Original v2.0.0:** Not specifically referenced.

**Updated v2.0.0:** "Canada's National Artificial Intelligence Strategy, titled 'AI for All,' was launched by Prime Minister Carney on 4 June 2026. The strategy commits $50 million to expand CAISI and targets $200 billion of economic growth and 250,000 new AI-related jobs over five years."

**Sources:**
- ISED Canada: https://ised-isde.canada.ca/site/ised/en/canadas-national-artificial-intelligence-strategy-ai-all
- Prime Minister's news release (4 June 2026): https://www.pm.gc.ca/en/news/news-releases/2026/06/04/prime-minister-carney-launches-ai-all-canadas-new-national-artificial

**Impact on AI-IDP:** The "AI for All" strategy's six pillars include safeguarding Canadian democracy and AI safety. AI-IDP's accountability framework aligns with the strategy's safety pillar. The strategy's existence strengthens the case for AI-IDP adoption as a National Standard.

### 4. Post-Quantum Cryptography Standards — Confirmed

**Original v2.0.0 statement:** "NIST PQC standardization; migration is documented."

**Updated v1.1.0 statement:** "NIST finalized three post-quantum cryptography standards on 13 August 2024: FIPS 203 (ML-KEM, formerly CRYSTALS-Kyber), FIPS 204 (ML-DSA, formerly CRYSTALS-Dilithium), and FIPS 205 (SLH-DSA, formerly SPHINCS+). The AegisTrace v1.1.0 reference implementation includes interface-complete ML-DSA-65 and SLH-DSA-128s scheme stubs (src/aegistrace/signing/pqc.py), ready for activation when liboqs-python is installed."

**Sources:**
- NIST FIPS 204 (final): https://csrc.nist.gov/pubs/fips/204/final
- NIST FIPS 205 (final): https://csrc.nist.gov/pubs/fips/205/final
- NIST FIPS 203 (final): https://csrc.nist.gov/pubs/fips/203/final
- NIST news release (August 2024): https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards

**Impact on AI-IDP:** The post-quantum migration path is no longer "future work" — it is "interface-ready, awaiting library installation." The v1.1.0 reference implementation includes the SchemeRegistry, MigrationService, MLDSA65Scheme, and SLHDSA128sScheme classes (with NotImplementedError stubs for sign/verify until liboqs-python is installed).

### 5. EU AI Act — Status Confirmed

**Original v2.0.0 statement:** "The European Union AI Act addresses AI governance but does not provide a universal permanent identity and traceability framework."

**Updated v2.0.0 statement:** "The European Union AI Act (Regulation (EU) 2024/1689) entered into force on 1 August 2024. The first requirements applied from 2 February 2025, with phased application through 2027. The EU AI Act addresses AI governance but does not provide a universal permanent identity and traceability framework comparable to AI-IDP."

**Sources:**
- EU AI Act official: https://artificialintelligenceact.eu/
- Implementation timeline: https://artificialintelligenceact.eu/implementation-timeline/
- White & Case analysis: https://www.whitecase.com/insight-alert/long-awaited-eu-ai-act-becomes-law-after-publication-eus-official-journal

### 6. W3C Verifiable Credentials Data Model v2.0 — New Finding

**Original v2.0.0 statement:** "W3C Verifiable Credentials v2.0."

**Updated v2.0.0 statement:** "W3C Verifiable Credentials Data Model v2.0 reached Candidate Recommendation Snapshot on 1 February 2024. AI-IDP interoperates with both v2.0 and v2.0."

**Sources:**
- W3C VC v2.0: https://www.w3.org/TR/vc-data-model-2.0/
- Publication history: https://www.w3.org/standards/history/vc-data-model-2.0

### 7. Quebec Bill 69 — Status Confirmed

**Updated v2.0.0 statement:** "Quebec Bill 69 (An Act to foster the development of and confidence in artificial intelligence) was introduced in 2024 and is subject to committee review. AI-IDP's cooperative-federalism model accommodates Quebec's parallel AI framework."

**Sources:**
- Quebec National Assembly: https://www.assnat.qc.ca/en/travaux-parlementaires/projets-loi/projet-loi-69-43-1.html

### 8. OCAP® Principles — Historical Context Confirmed

**Updated v2.0.0 statement:** "OCAP® principles were established in 1998 by the First Nations Information Governance Centre, providing a framework for asserting jurisdiction over First Nations data."

**Sources:**
- FNIGC: https://fnigc.ca/ocap-training/
- University of Toronto MDL blog: https://mdl.library.utoronto.ca/mdl-blog/first-nations-principles-ownership-control-access-and-possession-ocapr-pathway-data
- NCCID (2024): https://nccid.ca/wp-content/uploads/sites/2/2024/10/Surveillance-Advances_First-Nations-Data-Governance-2024-09-24.pdf

## Updated Assumption Register

The following assumptions are updated:

- **A-002 (updated):** Bill C-27 (AIDA) died on the Order Paper at prorogation on 6 January 2025. A replacement bill was expected in 2026 but had not been introduced as of July 2026. The legislative route proposed in the AI Actor Identity and Traceability Act is independent of AIDA's fate.

- **A-011 (new):** CAISI (established November 2024) is identified as the natural home for AI-IDP technical research and incident coordination. The administrative implementation plan should reference CAISI.

- **A-012 (new):** Canada's National AI Strategy ("AI for All," launched 4 June 2026) provides policy alignment for AI-IDP adoption. The strategy's safety pillar supports AI-IDP's accountability framework.

- **A-013 (updated):** Post-quantum cryptography standards (FIPS 203, 204, 205) were finalized on 13 August 2024. The AegisTrace v1.1.0 reference implementation includes interface-complete PQC scheme stubs.

## Updated Source Gap Register

The following gaps are closed:

- **G-011 (closed):** AIDA's legislative fate was previously uncertain. Deeper citation chaining confirmed Bill C-27 died on the Order Paper at prorogation on 6 January 2025.

- **G-012 (closed):** CAISI's mandate and establishment date were previously approximate. Deeper citation chaining confirmed CAISI was established November 2024.

The following gaps remain open:

- **G-004 (open):** Indigenous data-governance consultation with rights-holders remains a precondition for implementation. The v2.0.0 update adds the NCCID 2024 source but does not substitute for consultation.

- **G-005 (open):** Provincial AI legislative developments remain tracked at high level. Quebec Bill 69 status confirmed; other provincial developments require ongoing monitoring.

## Conclusion

Deeper citation chaining (depth 3+) updated the legal status of three key instruments: AIDA (Bill C-27 died January 2025), CAISI (established November 2024), and PQC standards (finalized August 2024). The v1.1.0 reference implementation includes interface-complete PQC scheme stubs. The legal framework's distinction between current law and proposed law is strengthened. The framework's adoption pathway through the Standards Council of Canada, CAISI coordination, and the proposed AI Actor Identity and Traceability Act remains valid and is independent of AIDA's fate.

<!-- COHERENCE UPDATE 2026-08-01: Last Material Revision date aligned to project delivery date. Historical content above is preserved unchanged. -->
