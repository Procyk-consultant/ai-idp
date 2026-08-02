---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/RISK_REGISTER.md
Title: Risk Register
Version: 2.0.0
Last Material Revision: 2026-08-01
---

# Risk Register

Material risks to the project objective, with severity, likelihood, mitigation, and owner.

| ID | Risk | Severity | Likelihood | Mitigation | Owner |
|----|------|----------|------------|-----------|-------|
| R-001 | Permanent identifiers become surveillance enablers | High | Medium | Pseudonymous user identifiers; sealed identity resolution; regulator-controlled disclosure; privacy tests | A10 privacy |
| R-002 | Cryptographic obsolescence (Ed25519 / SHA-256) | Medium | Medium (long horizon) | Interface-isolated signing; documented PQC migration path; long-term signature migration protocol in spec/PERMANENT_RECORD_PROTOCOL.md | A09 security |
| R-003 | Provider foreign-hosting avoidance | High | High | Jurisdictional nexus test in spec/AI-IDP-CANADA.md; controlling-organization liability; data-localization for trace records; cooperation duties with Canadian regulator | A04 constitutional |
| R-004 | Provincial jurisdiction conflict | High | Medium | Federal-provincial jurisdiction analysis; cooperative federalism model; minimum-national-standard framing | A04 constitutional |
| R-005 | Small-developer / open-source burden | Medium | High | Tiered conformance levels (L1–L4); small-developer compliance profile; open-source compliance profile; cost-benefit analysis with mitigations | A14 business / A13 quality |
| R-006 | Registry compromise | High | Low | Tamper-evident ledger; independent replication; public Merkle anchoring; incident reconstruction capability | A09 security |
| R-007 | Malicious administrator erases evidence | High | Medium | Independent archival replication; sealed records; Git history rewriting detection; distributed anchoring | A09 security / A23 db |
| R-008 | Privacy-vs-permanence legal conflict | High | Medium | Encrypted evidence payloads; content separation; minimal permanent metadata; access-controlled vaults; judicial access pattern | A10 privacy / A04 constitutional |
| R-009 | Employee surveillance abuse | Medium | High | Labour-impact report; worker recourse mechanism; collective agreement interface; disciplinary-use limits | A15 HR |
| R-010 | Indigenous data sovereignty conflict | Medium | Medium | Indigenous data-governance analysis; OCAP-aligned handling; consultation precondition; community-controlled access where applicable | A11 Indigenous |
| R-011 | Compliance market concentration effect | Medium | Medium | Open standard; small-developer profile; conformity body neutrality; open-source reference implementation | A14 business / A16 societal |
| R-012 | False confidence in AI-generated code quality | Medium | Medium | Quality-evidence protocol; conformance levels; explicit "tested" vs "verified" language (§37); audit-ready vs publication-ready distinction | A13 quality |
| R-013 | Foreign-provider non-cooperation | High | Medium | Controlling-organization liability; provider-duty framework; procurement controls; data-localization for evidence; enforcement options including service suspension | A04 / A14 |
| R-014 | Scope creep beyond Canadian AI agent identity | Medium | Medium | Scope-lock document; extension policy; versioning policy | A01 guardian |
| R-015 | Project execution drift from authorial intent | High | Low | Authority guardian role (A01); scope lock; decision log; IP and branding rules | A01 guardian |
