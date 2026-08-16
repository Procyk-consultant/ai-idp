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
File: LIMITATIONS.md
Title: Limitations (Top-Level Pointer)
Purpose: Top-level pointer to project limitations
Audience: All readers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Approved
Last Material Revision: 2026-08-16
Dependencies: project-control/SOURCE_GAP_REGISTER.md; release/FINAL_COMPLETION_REPORT.md
Source Basis: Master Execution Prompt
Invariants: Limitations are transparent without reducing the target standard
Failure Behaviour: Concealed limitations are a defect
Trace Policy: No AegisTrace event record required
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Limitations

AI-IDP intentionally defines a high-assurance target standard. AegisTrace is the reference implementation used to make that target concrete and testable. The items below identify validation, activation, deployment, or evidence boundaries; they do **not** reduce the intended L1-L4 standard.

## Validation Baseline

The last fully executed engineering-validation baseline is the **2026-08-02 v2.0.0 run: 113/113 tests passed**, with a clean demo/ledger verification, schema validation and Tectonic paper compilation recorded in `release/VALIDATION_REPORT.md`.

The current reconciliation branch contains later static hardening changes. Those changes have **not** been recompiled or retested and must not inherit the 113/113 status until a fresh controlled validation run is authorized.

External scholarly/engineering peer review remains pending. The project is already publicly archived on Zenodo and visible on GitHub; peer review is therefore an outstanding validation objective, not a claim that public archival publication has not occurred.

## Implementation and Activation Scope

The reference implementation contains the core identity, event, signing, ledger, delegation, authorization, registry, API, CLI and adapter architecture. Production-hardening capabilities include:

- PostgreSQL storage*;
- PKCS#11 / cloud-KMS integration paths*;
- batched/WAL ledger support;
- OpenTelemetry export*;
- post-quantum migration architecture*;
- GitHub remote publication/integration paths*.

> * Starred capabilities are part of the intended high-assurance implementation and have code/interface representation in the project corpus. Live activation depends on the corresponding external database, HSM/KMS, credential, collector, cryptographic runtime/library, remote service, or production environment. Where a backend method is not yet live-complete, the implementation must reach the stated target rather than lowering the standard.

Synthetic benchmark/evaluation data is not a substitute for real deployment data. Real operational performance, cost, availability and incident-response characteristics require production deployment evidence.

## Static Hardening Findings

The 2026-08-16 static reconciliation identified additional hardening work that is being tracked on the reconciliation branch, including strict public-key signature verification, explicit event-ID uniqueness, authorization/approval signature enforcement, dual-approval enforcement for designated actions, stronger WAL corruption handling, PostgreSQL sequencing review, deeper public-tier redaction enforcement, and tighter runtime integration between event collection and governance services.

These findings are treated as **implementation work toward the stated standard**, not reasons to weaken the normative requirements.

## Indigenous Data Governance Scope

The project preserves Indigenous data sovereignty and distinctions-based governance as an important design objective. Meaningful rights-holder engagement is required where a proposed deployment materially affects Indigenous rights, community data, governance authority, or services. It is **not** a universal implementation prerequisite for unrelated deployments without such a nexus.

The existing public-framework analysis is not a substitute for context-specific engagement when such rights/data/governance are actually implicated.

## Legislative and Standards Scope

AI-IDP is a **proposed Canadian standard and legal objective**, not current Canadian law and not an adopted National Standard of Canada. The repository includes proposed regulatory, legislative, administrative and conformity routes so that the intended end-state can be reviewed concretely.

Adoption, legal enforceability, accreditation and certification depend on the applicable standards body, regulator, government, contractual, procurement or legislative process. AegisTrace is not presently an externally certified L1-L4 implementation.

## Public / Operational Scope

The project is public on GitHub and archived on Zenodo. That public availability is distinct from a live regulated production deployment.

No verified government or Standards Council adoption/dispatch record is claimed. Live integrations must be activated and validated in their target environment before production claims are made.

See `project-control/SOURCE_GAP_REGISTER.md`, `project-control/VALIDATION_STATUS.md`, `project-control/STATIC_CONFORMANCE_AUDIT_2026-08-16.md`, and `release/VALIDATION_REPORT.md` for the detailed evidence and status trail.
