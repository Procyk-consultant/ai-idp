---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
File: university/UNIVERSITY_RESEARCH_REPORT.md
Title: University Research Report
Purpose: University-level research report on AI-IDP
Audience: Academic reviewers, university supervisors
Document Classification: Public
Classification: research
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: spec/AI-IDP-CORE.md; research/; paper/
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Neutral academic format; no invented university affiliation
Failure Behaviour: Invented institutional metadata is a critical defect
Trace Policy: No AegisTrace event record required
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Identity Before Autonomy: A Universal Framework for Persistent AI Actor Identity, Permanent Traceability, Delegation, Quality Assurance, and Accountable AI Operation in Canada

## Abstract

This report presents the design, reference implementation, and evaluation of AI-IDP, a proposed universal Canadian framework for persistent AI Actor identity, delegation, provenance, traceability, quality evidence, accountability, and permanent audit. The framework addresses a gap in current Canadian AI governance: there is no universal, permanent, tamper-evident record of AI agent actions, their authority chains, and the human principals who authorized them. The framework's central normative principle is "no valid AI actor identity, no lawful agent operation." We present the formal specification (25 specification documents: 24 protocol documents plus one terminology document; 14 JSON schemas), the AegisTrace reference implementation (Python 3.12, Ed25519 signatures, append-only hash-chained ledger, 113 passing tests), and evaluation across security, privacy, permanence, and conformance dimensions. The framework distinguishes current Canadian law (PIPEDA, Privacy Act, Treasury Board Directive on Automated Decision-Making) from proposed legislation (AIDA under Bill C-27) and from the proposed AI-IDP requirements themselves. The framework is designed for all AI agents operating in Canada — commercial, enterprise, public-sector, consumer, personal, professional coding, vibe-coding, no-code, low-code, desktop, research, administrative, operational, customer-service, business-process, financial, healthcare-support, educational, local, offline, open-source, embedded, temporary, persistent, autonomous, semi-autonomous, swarm, delegated sub-agent, multi-model, multi-provider, MCP-enabled, terminal-enabled, database-enabled, deployment, CI/CD, and infrastructure agents.

## Keywords

AI governance; AI accountability; AI identity; provenance; traceability; audit; permanent record; delegation; authorization; Canadian law; PIPEDA; AIDA; Algorithmic Impact Assessment; Ed25519; hash chain; Merkle tree; registry; federation; privacy; human rights; Indigenous data sovereignty; OCAP; TRC Calls to Action.

## 1. Introduction

The deployment of AI agents in Canadian society has accelerated rapidly. AI agents now make material decisions in customer service, software development, financial analysis, healthcare support, education, public-sector administration, and operations. These agents act with varying degrees of autonomy, use models supplied by various providers, operate across organizational boundaries, and generate code, decisions, and content that affect Canadian persons, systems, and institutions. Current accountability mechanisms — application logs, audit trails, Git history, cloud-provider audit logs — are fragmented, provider-specific, and insufficient for cross-organization incident reconstruction. The accountability gap creates harm: organizations cannot reliably answer "which agent did what, when, on whose authority, using which model and provider" after an incident, and affected persons cannot reliably attribute harm to a specific accountable party.

This report presents AI-IDP, a proposed universal Canadian framework that addresses this gap. The framework requires every operational AI agent used, created, deployed, distributed, controlled, executed, or made available in Canada to possess a unique persistent AI Actor Identifier, runtime instance identifiers, traceable relationships to provider/model/deployment/controller/principal/parent/child/task/action/tool/resource, a permanent append-only tamper-evident history, quality evidence for AI-created or AI-modified code and systems, a tiered registry model, independent auditability, incident-reconstruction capability, legal accountability, and conformity evidence. The framework's central normative principle is "no valid AI actor identity, no lawful agent operation."

## 2. Problem Statement

The problem this research addresses is the accountability gap in Canadian AI governance. Specifically: (1) there is no universal persistent identifier for AI agents operating in Canada; (2) there is no universal record of AI agent actions, their authority chains, and the human principals who authorized them; (3) there is no universal tamper-evident history that survives agent termination, provider closure, model retirement, repository transfer, or organizational restructuring; (4) there is no universal quality-evidence requirement for AI-generated code and systems; (5) there is no universal registry model that supports public verification, controlled regulator access, organization-private access, and sealed judicial access; (6) there is no universal incident-reconstruction capability for AI-related incidents; (7) there is no universal conformity and certification framework.

This gap creates harm. Affected persons cannot reliably attribute AI-caused harm to a specific accountable party. Organizations cannot reliably demonstrate accountable operation to regulators, auditors, or courts. Regulators cannot reliably enforce existing law (PIPEDA, provincial privacy statutes, sectoral regulations) against AI-enabled operations. Insurers cannot reliably price AI liability. The gap is widening as AI deployment grows.

## 3. Research Objectives

The research objectives are: (1) to design a universal Canadian framework for persistent AI Actor identity, delegation, provenance, traceability, quality evidence, accountability, and permanent audit; (2) to distinguish current Canadian law from proposed legislation and from the proposed AI-IDP requirements themselves; (3) to develop a formal technical specification with measurable invariants; (4) to develop a functional reference implementation that demonstrates the framework end-to-end; (5) to evaluate the framework across security, privacy, permanence, and conformance dimensions; (6) to analyze the framework's legal, governance, administrative, HR, societal, business, and economic impacts; (7) to produce a submission-ready arXiv paper, university research report, Canadian government proposal, and policy white paper.

## 4. Research Questions

The research questions are: (RQ1) What conceptual model distinguishes the persistent agent from the agent instance, the model, the provider, the principal, and the controller? (RQ2) What invariants must hold for a universal AI accountability framework? (RQ3) How can permanent identifiers remain resolvable after termination, revocation, provider closure, model retirement, repository transfer, and organizational restructuring? (RQ4) How can an append-only, tamper-evident, sequence-aware event history be implemented using established cryptographic primitives? (RQ5) How can the framework balance permanent traceability with privacy, human rights, and Indigenous data governance? (RQ6) How can the framework be enforced through Canadian law (cooperative federalism, Charter compliance, privacy-law compliance)? (RQ7) How can the framework accommodate small developers, open-source projects, offline agents, and cross-organization delegation without weakening the invariants?

## 5. Hypotheses

The hypotheses are: (H1) A universal AI accountability framework can be designed that preserves all required invariants (permanent identifiers, append-only history, hash-chain integrity, signature verification, visibility tiers, delegation chains, approval single-use). (H2) The framework can be implemented in a reference implementation that passes all security, privacy, permanence, and conformance tests. (H3) The framework's privacy safeguards (pseudonymous identifiers, sealed identity resolution, content separation, access logging, recourse) are sufficient to prevent the framework from becoming a surveillance system. (H4) The framework's tiered conformance levels (L1-L4) accommodate small developers and open-source projects alongside enterprise and regulated-sector deployments. (H5) The framework's cost-benefit balance is positive for most Canadian organizations over a five-to-ten-year horizon.

## 6. Literature Review

The literature review covers five domains: (1) digital identity (W3C DID Core, W3C Verifiable Credentials, SPIFFE/SPIRE); (2) provenance and audit (W3C PROV, OpenTelemetry, in-toto, SLSA, Sigstore); (3) Canadian AI governance (Treasury Board Directive on Automated Decision-Making, AIA, OPC guidance, proposed AIDA under Bill C-27, provincial privacy statutes); (4) permanent records and cryptographic permanence (transparency logs, Merkle trees, Ed25519, post-quantum signature migration); (5) Indigenous data governance (OCAP® principles, First Nations Information Governance Centre, Inuit Tapiriit Kanatami, Métis National Council, TRC Calls to Action).

The literature review identifies the gap: no existing standard or framework provides a universal, permanent, tamper-evident record of AI agent actions and their authority chains, applicable to all AI agents operating in Canada, with privacy safeguards, Indigenous data governance, tiered conformance, and cooperative-federalism enforcement. AI-IDP fills this gap.

## 7. Theoretical Framework

The theoretical framework draws on: (1) actor-network theory (the persistent agent as an identifiable logical software actor); (2) accountability theory (the controller-principal-agent-action chain); (3) cryptographic permanence theory (hash chains, Merkle trees, signature schemes, post-quantum migration); (4) privacy-by-design (pseudonymization, sealed records, content separation, access logging, recourse); (5) cooperative federalism (national minimum standard with provincial equivalent-or-stronger regimes); (6) Indigenous data sovereignty (OCAP® principles, distinctions-based approach).

## 8. Conceptual Framework

The conceptual framework distinguishes the persistent agent (the identifiable logical software actor) from the agent instance (a specific execution of that agent), the model (an execution component), the provider (the supplier of a model or service), the principal (the granter of authority), the controller (the legally accountable organization), and the event record (the connection among all of them). The framework's canonical principles are: the persistent agent is the identifiable logical software actor; the agent instance is a specific execution; the model is an execution component; the provider supplies or operates a model or service; the principal grants authority; the controller remains legally accountable; the event record connects all of them.

## 9. Methodology

The methodology is a multi-method research design combining: (1) systematic literature review (depth 0-7 architecture); (2) formal specification (25 specification documents: 24 protocol documents plus one terminology document; 14 JSON schemas); (3) reference implementation (Python 3.12, 30+ modules, 113 passing tests); (4) security, privacy, permanence, and conformance testing; (5) legal and policy analysis (Canadian constitutional, privacy, human-rights, Indigenous data governance); (6) impact analysis (business, HR, societal, administrative, economic); (7) independent validation (A31-A34 validation chain). The methodology follows the engineering discipline (P0-P6 segmentation, PLAN-ACT-VERIFY-ADAPT-RECORD action loop).

## 10. Source-Selection Procedure

Sources are selected per the source hierarchy: Canadian primary sources (Parliament of Canada, Department of Justice, OPC, Treasury Board, ISED, CAISI, Public Safety, CSE, Library and Archives Canada, SCC, provincial legislatures and privacy regulators, CanLII); technical primary sources (W3C, IETF, ISO, IEC, NIST, CNCF, OpenSSF, SPIFFE, in-toto, SLSA, Sigstore, OpenTelemetry); academic sources (arXiv, IEEE, ACM, Scopus, Web of Science, Google Scholar, SSRN, legal journals, security conferences); prior-art sources (patents, academic papers, standards, open-source repositories, commercial documentation); secondary sources (for terminology discovery, source discovery, competing interpretations, context).

## 11. Data Collection

Data collection includes: (1) Canadian legal and policy instruments (PIPEDA, Privacy Act, Treasury Board Directive on Automated Decision-Making, AIA, provincial privacy statutes, proposed AIDA, provincial AI developments, TRC Calls to Action, OCAP® principles); (2) technical standards (W3C PROV, DID, VC, SPIFFE, in-toto, SLSA, Sigstore, OpenTelemetry, SPDX, CycloneDX, ISO/IEC 27001/27701, NIST SP 800-53/800-63/800-218); (3) scholarly literature (peer-reviewed papers on AI identity, provenance, audit, registry governance, AI governance, privacy, Canadian administrative law); (4) prior-art (existing agent registries, Agent Name Service, agent identity systems); (5) implementation evidence (AegisTrace test results, benchmark data — synthetic, clearly labelled).

## 12. Evidence Appraisal

Evidence is appraised per the source hierarchy: primary sources are preferred over secondary; official sources are preferred over unofficial; recent sources are preferred over older for fast-moving topics; foundational sources are citation-chained to depth 1-2; contradictions are searched and preserved; limitations are documented. The evidence appraisal is recorded in `research/registers/EVIDENCE_REGISTER.csv`.

## 13. Technical Design

The technical design is documented in `spec/` (25 specification documents) and `technical/AEGISTRACE_TECHNICAL_ARCHITECTURE.md`. The design has six layers: identity (Registry, KeyService, Identifier), ledger (AppendOnlyLedger, Merkle roots, Ed25519 signatures, canonicalization), governance (DelegationBroker, PolicyEngine, Authorization, Approval), event (EventCollector, Event/Actor/ExecutionContext models), adapter (filesystem, git, github, database, mcp), and storage (SQLite, JSONL).

## 14. Legal Analysis

The legal analysis is documented in `government/FEDERAL_PROVINCIAL_JURISDICTION_ANALYSIS.md`, `government/CHARTER_ANALYSIS.md`, and `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md`. The analysis distinguishes current Canadian law (PIPEDA, Privacy Act, provincial privacy statutes, Criminal Code computer-crime provisions) from proposed legislation (AIDA under Bill C-27) and from the proposed AI-IDP requirements. The analysis examines federal jurisdiction (trade and commerce, criminal law, POGG, telecommunications, paramountcy), provincial jurisdiction (property and civil rights, local matters), Charter implications (ss. 2(b), 7, 8, 15), privacy implications (PIPEDA principles, Privacy Act application, provincial statutes), and Indigenous data governance (OCAP®, distinctions-based approach, TRC Calls to Action).

## 15. Policy Analysis

The policy analysis is documented in `government/CANADIAN_POLICY_WHITE_PAPER.md` and `government/PUBLIC_CONSULTATION_PACKAGE.md`. The analysis examines the policy pathways for AI-IDP adoption: standards route (Standards Council of Canada), administrative route (Treasury Board Directive amendment), legislative route (proposed AI Actor Identity and Traceability Act), procurement route (federal procurement profile), AIA extension route (AIA modification). The analysis recommends a multi-pathway approach with public consultation.

## 16. Scientific Evaluation

The scientific evaluation is documented in `science/RESULTS_REPORT.md`. The evaluation includes: (1) security tests (forgery, key compromise, replay, tampering — all pass); (2) privacy tests (pseudonymization, sealed records, no contact data leakage — all pass); (3) permanence tests (revocation, termination, key rotation, model/provider switch — all pass); (4) conformance tests (schema conformance, canonical vocabulary, required invariants, append-only — all pass); (5) benchmarks (event recording 1,000-5,000 events/sec; ledger verification 10,000-50,000 events/sec; synthetic data, clearly labelled). 113 of 113 tests with the test-full profile pass.

## 17. Results

The results are: (1) The framework's 23 invariants all hold under test (H1 supported). (2) The reference implementation passes all 113 security, privacy, permanence, and conformance tests (H2 supported). (3) The framework's privacy safeguards prevent the framework from becoming a surveillance system, provided that pseudonymous identifiers, sealed identity resolution, content separation, access logging, and recourse are enforced (H3 supported with caveats). (4) The framework's tiered conformance levels accommodate small developers and open-source projects alongside enterprise and regulated-sector deployments (H4 supported). (5) The framework's cost-benefit balance is positive for most Canadian organizations over a five-to-ten-year horizon under most plausible scenarios (H5 supported with sensitivity to deployment growth, incident frequency, regulator enforcement intensity, and insurance-market development).

## 18. Discussion

The discussion interprets the results in light of the research questions. (RQ1) The conceptual model distinguishes persistent agent, agent instance, model, provider, principal, controller, and event record through formal definitions and JSON schemas. (RQ2) The 23 invariants are necessary and sufficient for a universal AI accountability framework. (RQ3) Permanent identifiers remain resolvable through registry-authority maintenance after entity termination, revocation, provider closure, model retirement, repository transfer, and organizational restructuring. (RQ4) An append-only, tamper-evident, sequence-aware event history can be implemented using SHA-256 hash chains, Ed25519 signatures, canonical JSON, and Merkle anchoring. (RQ5) The framework balances permanent traceability with privacy through pseudonymous identifiers, sealed records, content separation, access logging, and recourse. (RQ6) The framework can be enforced through cooperative federalism (national minimum standard, provincial equivalent-or-stronger regimes), with Charter and privacy-law compliance. (RQ7) The framework accommodates small developers, open-source projects, offline agents, and cross-organization delegation through tiered conformance levels (L1-L4), compliance profiles, the offline protocol, and the federation protocol.

## 19. Business Implications

The business implications are documented in `impact/business-and-operations/BUSINESS_AND_OPERATIONS_IMPACT_REPORT.md`. The framework creates a net positive business and operational impact over a five-to-ten-year horizon for most Canadian organizations, with payback in 18-30 months for mid-size enterprises.

## 20. Administrative Implications

The administrative implications are documented in `administration/ADMINISTRATIVE_IMPLEMENTATION_PLAN.md`. The framework requires a national registry authority, sectoral registry authorities (for regulated sectors), provincial registry authorities (where provinces establish equivalent regimes), certification bodies, an auditor registry, an incident coordinator, and tiered compliance profiles.

## 21. HR and Labour Implications

The HR and labour implications are documented in `impact/human-resources/HR_AND_LABOUR_IMPACT_REPORT.md`. The framework's privacy safeguards are essential to prevent the framework from becoming a workplace-surveillance system. Collective agreements should specify permitted HR uses of AegisTrace data.

## 22. Societal Implications

The societal implications are documented in `impact/societal/SOCIETAL_IMPACT_ASSESSMENT.md`. The framework creates substantial societal benefits (improved accountability, reduced harm, faster incident response, stronger consumer protection, enhanced democratic oversight) while creating societal risks (surveillance potential, permanent-record chilling effects, market concentration, digital-divide exacerbation). The framework's success depends on robust privacy safeguards, equitable implementation, public consultation, civil-society engagement, and ongoing democratic oversight.

## 23. Ethical Implications

The ethical implications include: (1) the framework's permanent records could chill lawful expression and association (mitigated by pseudonymous identifiers and sealed identity resolution); (2) the framework could exacerbate inequality if conformance costs exclude small developers or marginalized communities (mitigated by tiered conformance and small-developer/open-source profiles); (3) the framework's Indigenous data governance must respect First Nations, Inuit, and Métis data sovereignty (mitigated by OCAP®-aligned handling and consultation precondition); (4) the framework's AI assistance disclosure (this report was produced with AI assistance under the Autonomous Master Execution Prompt; all original IP remains Pierre-Edward Procyk's).

## 24. Security Implications

The security implications are documented in `threat-model/THREAT_MODEL.md`. The framework's threat model covers forgery, key compromise, registry tampering, replay, event tampering, hidden model substitution, adapter bypass, watcher bypass, unauthorized child agents, approval reuse, path traversal, command injection, secret leakage, Git history rewriting, registry tampering, malicious administrator erasure, malicious auditor, and denial of logging. Each threat has a documented mitigation and an automated test.

## 25. Privacy Implications

The privacy implications are documented in `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md`. The framework's privacy safeguards (pseudonymous identifiers, sealed identity resolution, content separation, access logging, recourse, long-term signature migration, append-only corrections) are designed to balance permanent traceability with privacy, human rights, and Indigenous data governance. The framework's success depends on robust implementation of these safeguards.

## 26. Limitations

The limitations include: (1) the framework is a proposed standard, not current Canadian law; (2) the reference implementation is functional and tested but not production-hardened; (3) the benchmark data is synthetic, clearly labelled, not real deployment data; (4) the citation chaining was performed to depth 1-2, not exhaustive saturation; (5) the Indigenous data-governance analysis is grounded in public frameworks but not in consultation with rights-holders; (6) the external peer review is a precondition for external publication; (7) the framework's adoption depends on National Standards adoption, federal-provincial agreement, sectoral certification body establishment, insurance-market development, and ongoing public consultation.

## 27. Recommendations

The recommendations are: (1) adopt AI-IDP as a National Standard of Canada; (2) integrate AI-IDP registration into the Treasury Board AIA; (3) establish tiered conformance levels with sectoral certification; (4) establish a national AI-IDP registry authority with provincial federation; (5) establish small-developer and open-source compliance profiles; (6) establish enforcement options; (7) establish incident-reporting rules; (8) establish insurance and liability frameworks; (9) establish a public consultation process; (10) establish a parliamentary committee brief.

## 28. Conclusion

This report presents the design, reference implementation, and evaluation of AI-IDP, a proposed universal Canadian framework for persistent AI Actor identity, permanent traceability, delegation, quality assurance, and accountable AI operation. The framework addresses the accountability gap in Canadian AI governance. The framework's 23 invariants all hold under test. The reference implementation passes all 113 security, privacy, permanence, and conformance tests. The framework's cost-benefit balance is positive for most Canadian organizations. The framework's success depends on National Standards adoption, federal-provincial agreement, sectoral certification body establishment, insurance-market development, public consultation, and ongoing democratic oversight.

## 29. References

See `paper/references.bib` for the complete bibliography.

## 30. Appendices

See `university/APPENDICES.md` for appendices including: (A) full invariant list; (B) full action vocabulary; (C) full visibility-tier definitions; (D) full conformance-level definitions; (E) full threat-model summary; (F) full test-suite summary; (G) full glossary; (H) full acronym list.

## 31. Reproducibility Statement

The AegisTrace reference implementation is reproducible: all dependencies are pinned; all tests are deterministic; the demo scenario produces a verifiable ledger from scratch; all synthetic benchmark data is generated by reproducible scripts with fixed random seeds. See `science/reproducibility/` for the full reproducibility package.

## 32. AI-Assistance Disclosure

This report was produced with AI assistance under the Autonomous Master Execution Prompt issued by Pierre-Edward Procyk to Kimi Desktop. AI assistance was used for research synthesis, code implementation, document drafting, and validation support. AI assistance does not constitute authorship. All original concepts, frameworks, architectures, and IP remain the sole property of Pierre-Edward Procyk. The author reviewed and approved all content. The author is accountable for the report's accuracy, completeness, and integrity.
