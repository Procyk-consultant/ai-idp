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
Last Material Revision: 2026-08-17
Dependencies: project-control/SOURCE_GAP_REGISTER.md; release/FINAL_COMPLETION_REPORT.md
Source Basis: Master Execution Prompt
Invariants: Limitations are transparent without reducing the target standard
Failure Behaviour: Concealed limitations are a defect
Trace Policy: No AegisTrace event record required
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Limitations

AI-IDP intentionally defines a high-assurance target standard. AegisTrace is the reference implementation used to make that target concrete and testable. The items below identify validation, activation, deployment, certification, or external-evidence boundaries; they do **not** reduce the intended L1-L4 standard.

## Validation Baseline

The last fully executed engineering-validation baseline is the **2026-08-02 v2.0.0 run: 113/113 tests passed**, with a clean demo/ledger verification, schema validation and Tectonic paper compilation recorded in `release/VALIDATION_REPORT.md`.

The reconciliation branch contains later source hardening and cryptographic-backend completion work. Those changes have **not** been recompiled or retested and must not inherit the historical 113/113 status until a fresh controlled validation run is authorized.

External scholarly/engineering peer review remains pending. The project is publicly archived on Zenodo and visible on GitHub; peer review is an outstanding validation objective, not a prerequisite for describing the public archival record.

## Implementation and Activation Scope

The reference implementation contains identity, event, signing, ledger, delegation, authorization, approval, governance, registry, API, CLI, disclosure and adapter layers. Production-hardening capabilities include:

- PostgreSQL storage*;
- PKCS#11 Ed25519 HSM key generation/signing*;
- AWS KMS signing* including Ed25519 and configurable asymmetric signing specifications;
- Azure Key Vault EC signing*;
- Google Cloud KMS EC signing*;
- batched/WAL ledger support;
- OpenTelemetry export*;
- ML-DSA-65 live signing/verification through liboqs*;
- SLH-DSA SHA2-128s live signing/verification through liboqs*;
- GitHub remote publication/integration paths*.

> * **External activation / validation note:** starred capabilities now have concrete source implementation paths rather than placeholder `NotImplementedError` methods. Their live operational status still depends on the corresponding external database, HSM/token, KMS account, credential, collector, liboqs runtime, remote service or deployment environment. They must be validated in the applicable target environment before a production-activation claim is made.

For PKCS#11 specifically, token support for Edwards-curve key generation and `CKM_EDDSA` is required. Cloud KMS algorithms and hardware protection depend on provider capabilities and the selected key configuration. liboqs is an external cryptographic runtime and its deployment/security posture must be assessed for the intended environment.

Synthetic benchmark/evaluation data is not a substitute for real deployment data. Real operational performance, cost, availability and incident-response characteristics require production deployment evidence.

## Reconciliation Hardening

The 2026-08-16/17 reconciliation added or strengthened:

- strict public-key signature verification;
- explicit event-ID uniqueness;
- signed authorization and approval enforcement;
- exact-action approval digests;
- designated dual-approval enforcement;
- governed API writes with request proof-of-possession and replay resistance;
- end-to-end delegation scope checks;
- allow-listed public disclosure projections;
- stronger canonical-state isolation;
- fail-closed WAL corruption handling;
- PostgreSQL sequencing corrections;
- parallel ledger verification;
- live liboqs ML-DSA / SLH-DSA code paths;
- concrete PKCS#11 and managed-KMS signing code paths.

These changes are source-complete work toward the stated standard, but they are **not newly runtime-validated** in this reconciliation session.

## Indigenous Data Governance Scope

The project preserves Indigenous data sovereignty and distinctions-based governance as an important design objective. Meaningful rights-holder engagement is required where a proposed deployment materially affects Indigenous rights, community data, governance authority, or services. It is **not** a universal implementation prerequisite for unrelated deployments without such a nexus.

The existing public-framework analysis is not a substitute for context-specific engagement when such rights, data, or governance are actually implicated.

## Legislative and Standards Scope

AI-IDP is a **proposed Canadian standard and legal objective**, not current Canadian law and not an adopted National Standard of Canada. The repository includes proposed regulatory, legislative, administrative and conformity routes so that the intended end-state can be reviewed concretely.

Adoption, legal enforceability, accreditation and certification depend on the applicable standards body, regulator, government, contractual, procurement or legislative process. AegisTrace is not presently an externally certified L1-L4 implementation.

## Public / Operational Scope

The project is public on GitHub and archived on Zenodo. That public availability is distinct from a live regulated production deployment.

No verified government or Standards Council adoption/dispatch record is claimed. External integrations must be activated and validated in their target environment before production-operation claims are made.

See `project-control/SOURCE_GAP_REGISTER.md`, `project-control/VALIDATION_STATUS.md`, `project-control/STATIC_CONFORMANCE_AUDIT_2026-08-16.md`, `project-control/CRYPTO_BACKEND_COMPLETION_2026-08-17.md`, and `release/VALIDATION_REPORT.md` for the evidence and status trail.
