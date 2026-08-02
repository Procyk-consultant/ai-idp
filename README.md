# AI-IDP / AegisTrace

Last Material Revision: 2026-08-01

**A Universal Canadian Framework for Persistent AI Actor Identity, Permanent Traceability, Delegation, Quality Assurance, and Accountable AI Operation**

© 2026 Pierre-Edward Procyk. Cognitive Industries — Les Industries Cognitives. All rights reserved.

> **Status:** v2.0.0 pushed to GitHub. No external publication, arXiv submission, government submission, or public licence has been performed. External release requires separate written authorization from Pierre-Edward Procyk.

---

## Repository

**GitHub:** https://github.com/Procyk-consultant/ai-idp

---

## Project Originator

**Pierre-Edward Procyk**  
Founder / CEO  
Cognitive Industries — Les Industries Cognitives  
Saguenay, Québec, Canada  
p.procyk.media@gmail.com  
LinkedIn: [linkedin.com/in/pierre-edward-procyk-223b75305](https://www.linkedin.com/in/pierre-edward-procyk-223b75305)

---

## What This Project Is

AI-IDP is a proposed universal Canadian legal and technical standard under which every operational AI agent used, created, deployed, distributed, controlled, executed, or made available in Canada must possess:

1. A unique persistent AI Actor Identifier.
2. A unique identifier for every runtime agent instance.
3. Traceable relationships to its provider, model, deployment, controller, principal, parent agent, delegated sub-agents, tasks, actions, tools, and resources.
4. A permanent, append-only, tamper-evident history.
5. Quality evidence for all AI-created or AI-modified code and systems.
6. A public, semi-public, private, and offline registry model.
7. Independent auditability, incident-reconstruction capability, legal accountability, and conformity evidence.

The intended Canadian normative principle is:

> **NO VALID AI ACTOR IDENTITY, NO LAWFUL AGENT OPERATION.**

This is the **proposed** standard and legal objective. It is **not** current Canadian law.

**AegisTrace** is the reference implementation: a functional Python software system that demonstrates the standard end-to-end.

---

## Quick Start

```powershell
# 1. Install
pip install -e .

# 2. Run the demo
python -m aegistrace.cli admin demo --out .aitrace-demo

# 3. Run the test suite
pytest tests/ -v

# 4. Verify a ledger
python -m aegistrace.cli verify --ledger .aitrace-demo\ledger.jsonl

# 5. Compile the arXiv paper
Set-Location -LiteralPath 'paper'
tectonic main.tex
```

---

## Repository Structure

```
ai-idp-aegistrace/
├── README.md                          ← you are here
├── OFFICIAL_PROJECT_DOCUMENT_EN.pdf   ← Official English project document
├── DOCUMENT_OFFICIEL_PROJET_FR.pdf    ← Document officiel de projet (français)
├── OFFICIAL_EMAIL_TEMPLATES.md        ← Email templates for government presentation
├── GITHUB_PUSH_INSTRUCTIONS.md        ← Step-by-step GitHub push instructions
├── FILING_INSTRUCTIONS.md             ← What goes where, to who, why
├── project-control/                   ← Control records, status, decisions
├── brand/                             ← Official brand assets (originals preserved)
├── research/                          ← Research protocol, registers, evidence, synthesis
├── university/                        ← University research package (md+docx+pdf)
├── science/                           ← Scientific method, hypotheses, results, and limitations
├── government/                        ← Canadian government proposal package
├── administration/                    ← Administrative implementation
├── impact/                            ← Business, HR, societal impact reports
├── spec/                              ← Formal technical specifications (25 documents)
├── schemas/                           ← JSON Schemas (14 schemas)
├── src/aegistrace/                    ← Functional reference implementation
├── src/aegistrace/adapters/           ← External adapters
├── tests/                             ← Unit, integration, security, privacy, permanence, conformance
├── tests/conformance/                 ← Executable conformance suite
├── examples/                          ← Worked examples
├── threat-model/                      ← Threat model and attack trees
├── docs/                              ← Developer, auditor, regulator documentation
├── paper/                             ← arXiv LaTeX project + compiled PDF
├── scripts/                           ← Generation and utility scripts
├── release/                           ← Release metadata, checksums, and completion reports
└── .github/workflows/                 ← CI workflow definitions
```

---

## Key Documents

| Audience | Start here |
|----------|-----------|
| **Government of Canada** | `OFFICIAL_PROJECT_DOCUMENT_EN.pdf` |
| **Gouvernement du Québec** | `DOCUMENT_OFFICIEL_PROJET_FR.pdf` |
| **Policy makers** | `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.pdf` |
| **Policy analysts** | `government/CANADIAN_POLICY_WHITE_PAPER.pdf` |
| **Legal reviewers** | `government/PROPOSED_AI_ACTOR_IDENTITY_AND_TRACEABILITY_ACT.md`, `government/FEDERAL_PROVINCIAL_JURISDICTION_ANALYSIS.pdf`, `government/CHARTER_ANALYSIS.pdf` |
| **Academic reviewers** | `paper/main.pdf` (arXiv paper) |
| **University supervisors** | `university/UNIVERSITY_RESEARCH_REPORT.pdf` |
| **Architects** | `spec/AI-IDP-CORE.md`, `technical/AEGISTRACE_TECHNICAL_ARCHITECTURE.pdf` |
| **Implementers** | `docs/quickstart.md`, `docs/developer-guide.md`, `src/aegistrace/` |
| **Auditors** | `docs/auditor-guide.md`, `spec/AUDIT_PROTOCOL.md` |
| **Regulators** | `docs/regulator-guide.md`, `spec/REGISTRY_PROTOCOL.md` |
| **Francophone audiences** | `government/NOTE_DE_SYNTHESE_FR.pdf`, `technical/ARCHITECTURE_TECHNIQUE_FR.pdf`, `impact/IMPACT_CANADIEN_FR.pdf` |

---

## Technical Stack

- **Python 3.12** with strict static typing
- **Ed25519 signatures** (RFC 8032) via the `cryptography` library
- **SHA-256** for content digests and event hashes
- **JSONL** append-only ledger with hash chaining
- **Merkle trees** for public verification anchoring
- **FastAPI** for the HTTP API
- **SQLite** for local storage; **PostgreSQL** for production
- **pytest** for testing (113 passing tests)
- **Tectonic** for LaTeX compilation

### Production Hardening (v2.0.0+)

- **PostgreSQL storage backend** with JSONB, BIGSERIAL, SSL-by-default
- **HSM-backed key management** (PKCS#11, AWS KMS, Azure Key Vault, GCP KMS)
- **Batched high-throughput ledger** with write-ahead log (WAL)
- **OpenTelemetry runtime exporter** for observability
- **Post-quantum signature migration** (ML-DSA per FIPS 204, SLH-DSA per FIPS 205)
- **Live GitHub remote integration** for Merkle anchor pushing

---

## Test Suite

```bash
pytest tests/ -v
```

**113 tests pass** across:
- Unit tests (identity, ledger, signing, delegation, authorization, production hardening)
- Integration tests (complete lifecycle, model/provider switch, filesystem adapter, GitHub adapter, CLI)
- Security tests (forgery, key compromise, event tampering, deletion, reordering, replay)
- Privacy tests (pseudonymization, sealed records, no contact data leakage)
- Permanence tests (revocation, termination, key rotation, archive)
- Conformance tests (schema, canonical vocabulary, invariants, append-only)

---

## Conformance Levels

AI-IDP defines four conformance levels (L1–L4):

- **L1 (Baseline):** Persistent identifiers, signed events, local ledger. For small developers and open-source.
- **L2 (Standard):** L1 + public verification, private evidence, delegation, authorization, approval, resource manifests.
- **L3 (High Assurance):** L2 + independent archival replication, federation, database/CI-CD adapters, annual audit. For regulated sectors.
- **L4 (Maximum Assurance):** L3 + dual approval, regulator-controlled vault, real-time transparency log, PQC readiness. For critical infrastructure.

---

## Privacy Safeguards

- **Pseudonymous identifiers** by default (`aitrace://ca/principal/user-XXX`)
- **Sealed records** for sensitive information (judicial/regulator-controlled access)
- **Content separation** (permanent minimal metadata + cryptographic commitments, not plaintext)
- **Access logging** for all non-public record access
- **Recourse mechanism** for affected persons

---

## Indigenous Data Governance

The framework recognizes Indigenous data sovereignty:
- **OCAP® principles** (Ownership, Control, Access, Possession) — First Nations Information Governance Centre
- **Distinctions-based approach** — First Nations, Inuit, and Métis
- **TRC Calls to Action** alignment (particularly Calls 43–44, 7, 18, 19)
- **Community-controlled access** for Indigenous community data
- **Consultation with rights-holders is a precondition for implementation**

---

## Copyright and IP

© 2026 Pierre-Edward Procyk. Cognitive Industries — Les Industries Cognitives. All rights reserved.

No licence, assignment, reproduction right, modification right, publication right, implementation right, commercial-use right, derivative-work right, or redistribution right is granted by implication. Any external use, implementation, adaptation, reproduction, publication, distribution, or commercialization requires prior written authorization from the rights holder.

Third-party rights, standards, laws, research, and software remain the property of their respective rights holders. See `NOTICE.md`.

---

## Contact

Pierre-Edward Procyk  
Founder / CEO  
Cognitive Industries — Les Industries Cognitives  
Saguenay, Québec, Canada  
p.procyk.media@gmail.com  
p.1o9.cognitive@outlook.com  
+1 (581) 668-2372  
LinkedIn: [linkedin.com/in/pierre-edward-procyk-223b75305](https://www.linkedin.com/in/pierre-edward-procyk-223b75305)

---

## Citation

```bibtex
@misc{aegistrace2026,
  author = {Pierre-Edward Procyk},
  title = {AI-IDP / AegisTrace: A Universal Framework for Persistent AI Actor Identity, Permanent Traceability, Delegation, Quality Assurance, and Accountable AI Operation},
  year = {2026},
  month = {July},
  version = {2.0.0},
  url = {https://github.com/Procyk-consultant/ai-idp}
}
```

---

## Status

See `project-control/PROJECT_STATUS.md`, `release/FINAL_COMPLETION_REPORT.md`, and `release/VALIDATION_REPORT.md` for the consolidated completion status and limitations.

**Date:** Saturday 1 August 2026 (2026-08-01)  
**Version:** 2.0.0  
**Tests:** 113/113 passing  
**arXiv paper:** Compiles via Tectonic (13 pages, 57 bibliography entries)

# AI-IDP / AegisTrace
