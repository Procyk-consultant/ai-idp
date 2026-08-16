# AI-IDP
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21769036.svg)](https://doi.org/10.5281/zenodo.21769036) / AegisTrace

Last Material Revision: 2026-08-16

**A Universal Canadian Framework for Persistent AI Actor Identity, Permanent Traceability, Delegation, Quality Assurance, and Accountable AI Operation**

© 2026 Pierre-Edward Procyk. Cognitive Industries — Les Industries Cognitives. All rights reserved.

> **Status:** v2.0.0 is public on GitHub and archived on Zenodo (DOI: [10.5281/zenodo.21769036](https://doi.org/10.5281/zenodo.21769036)). The initial LinkedIn article was published on 2026-08-08. arXiv is deferred with no identifier assigned; government and standards submissions have no verified dispatch record. The project remains All Rights Reserved; no public licence has been granted.

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

This is the **proposed** standard and legal objective. It is **not** current Canadian law. The project intentionally states the full target standard and expected end-state so that implementation, regulatory review, conformity assessment, and future adoption can be measured against a clear destination.

**AegisTrace** is the reference implementation: a functional Python software system that demonstrates the standard end-to-end.

---

## Quick Start

```powershell
# 1. Install
pip install -e .

# 2. Run the demo (creates ledger.jsonl + public_keys.json)
python -m aegistrace.cli admin demo --out .aitrace-demo

# 3. Run the test suite
pytest tests/ -v

# 4. Fully verify a ledger: hash chain + Ed25519 signatures
python -m aegistrace.cli verify --ledger .aitrace-demo\ledger.jsonl --keys .aitrace-demo\public_keys.json

# Optional: integrity-only verification when public keys are intentionally unavailable
python -m aegistrace.cli verify --ledger .aitrace-demo\ledger.jsonl --hash-only

# 5. Compile the research paper
Set-Location -LiteralPath 'paper'
tectonic main.tex
```

---

## Repository Structure

```
ai-idp-aegistrace/
├── README.md                          ← you are here
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
├── paper/                             ← Research-paper LaTeX project + compiled PDF
├── scripts/                           ← Generation and utility scripts
├── release/                           ← Release metadata, checksums, and completion reports
└── .github/workflows/                 ← CI workflow definitions
```

---

## Key Documents

| Audience | Start here |
|----------|-----------|
| **Government of Canada** | `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.pdf` |
| **Gouvernement du Québec** | `government/NOTE_DE_SYNTHESE_FR.pdf` |
| **Policy makers** | `government/CANADIAN_NATIONAL_PROJECT_PROPOSAL.pdf` |
| **Policy analysts** | `government/CANADIAN_POLICY_WHITE_PAPER.pdf` |
| **Legal reviewers** | `government/PROPOSED_AI_ACTOR_IDENTITY_AND_TRACEABILITY_ACT.md`, `government/FEDERAL_PROVINCIAL_JURISDICTION_ANALYSIS.pdf`, `government/CHARTER_ANALYSIS.pdf` |
| **Academic reviewers** | `paper/main.pdf` (research paper; Zenodo archival record) |
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
- **SQLite** for local storage; **PostgreSQL** for production*
- **pytest** for testing (113/113 passed in the last recorded full validation on 2026-08-02)
- **Tectonic** for LaTeX compilation (last recorded clean compile: 2026-08-02)

### Production Hardening (v2.0.0+)

- **PostgreSQL storage backend*** with JSONB, BIGSERIAL, SSL-by-default
- **HSM-backed key management*** (PKCS#11, AWS KMS, Azure Key Vault, GCP KMS)
- **Batched high-throughput ledger** with write-ahead log (WAL)
- **OpenTelemetry runtime exporter*** for observability
- **Post-quantum signature migration*** (ML-DSA per FIPS 204, SLH-DSA per FIPS 205)
- **Live GitHub remote integration*** for Merkle anchor pushing

> * **Capability-status note:** starred production capabilities are part of the intended high-assurance implementation and their interfaces/modules were included in the 2026-08-02 validated 113-test corpus. Live activation still depends on the corresponding external service, credential, hardware, runtime library, or endpoint. This notation preserves the intended end-state without presenting an external integration as already activated in production.

---

## Test Suite

```bash
pytest tests/ -v
```

**Last recorded full validation: 113/113 tests passed on 2026-08-02** across:
- Unit tests (identity, ledger, signing, delegation, authorization, production hardening)
- Integration tests (complete lifecycle, model/provider switch, filesystem adapter, GitHub adapter, CLI)
- Security tests (forgery, key compromise, event tampering, deletion, reordering, replay)
- Privacy tests (pseudonymization, sealed records, no contact data leakage)
- Permanence tests (revocation, termination, key rotation, archive)
- Conformance tests (schema, canonical vocabulary, invariants, append-only)

**Current reconciliation status:** the historical 113/113 result remains the last executed full validation. The `reconcile-2026-08-14` branch contains post-validation hardening changes identified through static code/specification review and therefore requires a fresh controlled validation pass before it can inherit the historical 113/113 status or be merged as a validated release.

**GitHub CI note:** the latest observed GitHub Actions failure did not execute any workflow step because GitHub reported the account locked due to a billing issue; it is therefore not evidence of a code, test, or compilation failure.

---

## Conformance Levels

AI-IDP defines four conformance levels (L1–L4) as the target implementation and regulatory standard:

- **L1 (Baseline):** Persistent identifiers, signed events, local ledger. For small developers and open-source.
- **L2 (Standard):** L1 + public verification, private evidence, delegation, authorization, approval, resource manifests.
- **L3 (High Assurance):** L2 + independent archival replication, federation, database/CI-CD adapters, annual audit. For regulated sectors.
- **L4 (Maximum Assurance):** L3 + dual approval, regulator-controlled vault, real-time transparency log, PQC readiness. For critical infrastructure.

These levels define the intended conformity destination of the standard; adoption or legal enforceability depends on the applicable standards, administrative, contractual, procurement, or legislative route.

---

## Privacy Safeguards

- **Pseudonymous identifiers** by default (`aitrace://ca/principal/user-XXX`)
- **Sealed records** for sensitive information (judicial/regulator-controlled access)
- **Content separation** (permanent minimal metadata + cryptographic commitments, not plaintext)
- **Access logging** for all non-public record access
- **Recourse mechanism** for affected persons

---

## Indigenous Data Governance

The framework recognizes Indigenous data sovereignty as an important design objective where Indigenous rights, data, communities, or governance contexts are materially involved:
- **OCAP® principles** (Ownership, Control, Access, Possession) — First Nations Information Governance Centre
- **Distinctions-based approach** — First Nations, Inuit, and Métis
- **TRC Calls to Action** alignment as a policy/design objective where relevant
- **Community-controlled access** for Indigenous community data where applicable
- **Meaningful rights-holder engagement before deployments that materially affect Indigenous rights, community data, or governance**

This is **not a universal implementation gate for unrelated deployments**. AI-IDP preserves the objective of strong Indigenous data governance while applying engagement requirements contextually to deployments where those rights or data are actually implicated.

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
LinkedIn: [linkedin.com/in/pierre-edward-procyk-223b75305](https://www.linkedin.com/in/pierre-edward-procyk-223b75305)

---

## Citation

```bibtex
@misc{aegistrace2026,
  author = {Pierre-Edward Procyk},
  title = {AI-IDP / AegisTrace: A Universal Framework for Persistent AI Actor Identity, Permanent Traceability, Delegation, Quality Assurance, and Accountable AI Operation},
  year = {2026},
  month = {August},
  version = {2.0.0},
  doi = {10.5281/zenodo.21769036},
  url = {https://doi.org/10.5281/zenodo.21769036},
  howpublished = {Code and specifications: https://github.com/Procyk-consultant/ai-idp}
}
```

---

## Status

See `project-control/PROJECT_STATUS.md`, `project-control/VALIDATION_STATUS.md`, `release/FINAL_COMPLETION_REPORT.md`, and `release/VALIDATION_REPORT.md` for the consolidated completion status, verified results, target capabilities, and limitations.

**Project baseline:** v2.0.0 / 2026-08-01  
**Reconciliation branch material:** 2026-08-16  
**Version:** 2.0.0  
**Tests:** 113/113 passing in the last recorded full validation (2026-08-02); branch changes not yet rerun  
**Research paper:** Last recorded clean Tectonic compile passed on 2026-08-02; public archival record at https://doi.org/10.5281/zenodo.21769036
