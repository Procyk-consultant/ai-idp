---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Location: Saguenay, Québec, Canada
File: spec/CONFORMANCE_LEVELS.md
Title: Conformance Levels
Purpose: Define cumulative AI-IDP L1-L4 target assurance levels
Audience: Implementers, auditors, regulators, certification bodies
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready / reconciliation clarified
Last Material Revision: 2026-08-17
Dependencies: AI-IDP-CORE.md; CERTIFICATION_PROTOCOL.md
Source Basis: Master Execution Prompt; AI-IDP architecture; assurance model
Invariants: Levels are cumulative; implementation evidence is distinct from certification
Failure Behaviour: Unsupported or uncertified conformance claims are forbidden
Trace Policy: Conformance evidence must resolve to auditable records
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Conformance Levels

AI-IDP defines four cumulative target assurance levels. Each level includes the requirements of lower levels.

These levels describe the **proposed standard's conformity destination**. They do not imply that AegisTrace, this repository, or any deployment is currently certified at a level merely because source modules implementing part of that level exist.

## L1 — Baseline

L1 target requirements include:

- persistent AI Actor identifiers;
- runtime agent-instance identifiers;
- signed and hash-chained material-event evidence;
- local append-only ledger;
- on-demand integrity/signature verification with appropriate verification material;
- basic offline operation/reconciliation;
- verification tooling.

Typical target context: small developers, personal/low-risk agents, open-source projects, and lower-assurance deployments.

## L2 — Standard

L2 includes L1 plus target requirements such as:

- public verification evidence / Merkle anchoring;
- private evidence separation;
- enforceable delegation lineage;
- signed bounded authorization;
- exact-action, single-use approval controls;
- resource manifests;
- filesystem/Git integration paths;
- audit/reconstruction tooling;
- executable conformance tests;
- strict public disclosure projection rather than raw event publication.

Typical target context: enterprise/commercial agents and mid-size organizational deployments.

## L3 — High Assurance

L3 includes L2 plus target requirements such as:

- independent archival replication*;
- federation support*;
- production-grade database and CI/CD integration*;
- stronger privacy controls and access logging*;
- permanence/rotation/migration evidence;
- recurring independent conformance audit*;
- context-appropriate incident reporting and regulatory evidence*;
- distributed enforcement semantics appropriate to multi-node deployments*.

Typical target context: regulated sectors, public-sector deployments, high-value systems, and critical operational workflows.

## L4 — Maximum Assurance

L4 includes L3 plus target requirements such as:

- dual control for all policy-designated high-impact actions;
- regulator/independent-controlled evidence infrastructure where applicable*;
- real-time external transparency anchoring*;
- cryptographic migration readiness including documented PQC path*;
- high-assurance HSM/KMS-backed key custody*;
- recurring security, privacy, and operational audits*;
- accredited/public certification where an applicable certification regime exists*.

Typical target context: high-impact automated decisions, national or critical infrastructure contexts, and systems requiring maximum independent assurance.

## Conformance claim vocabulary

The following terms are intentionally distinct:

- **implementation target** — the level an implementation is being built toward;
- **self-assessment** — internal evidence against the level requirements;
- **validated implementation evidence** — executable/inspection evidence produced by a defined validation procedure;
- **certified conformance** — conformity established through the applicable authorized/accredited certification process.

An implementation may claim `conforms to AI-IDP L{n}` only when the certification requirements defined by `CERTIFICATION_PROTOCOL.md` are satisfied. Internal tests or self-assessment alone do not constitute certified conformance.

## AegisTrace reference implementation status

AegisTrace is the reference implementation used to make AI-IDP mechanisms concrete, inspectable, testable, and auditable.

The project retains L1-L4 as its normative engineering destination. The existence of code paths for L2-L4 mechanisms does **not** mean the repository is currently certified at those levels.

The last fully executed project-wide validation remains the 2026-08-02 historical baseline. The 2026-08-17 reconciliation branch contains additional source hardening and requires fresh execution before becoming a new validated baseline.

## Invariants

- Levels are cumulative.
- A higher level cannot weaken a lower-level invariant.
- Self-assessment is not certification.
- A capability interface is not proof of live production activation.
- Conformance/certification evidence must be traceable and reproducible.
- Certification may expire or be revoked according to the applicable protocol.
- External infrastructure/authority requirements remain part of the target even when not activated by the reference repository.

> `*` Starred requirements depend on the applicable external infrastructure, service, hardware, deployment topology, independent assessor, regulator, or certification authority. This notation describes activation/assurance dependencies without removing the normative target.
