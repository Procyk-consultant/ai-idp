---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: project-control/SOURCE_GAP_REGISTER.md
Title: Source Gap Register
Version: 2.0.0-reconciliation
Last Material Revision: 2026-08-17
---

# Source Gap Register

Outstanding evidence, deployment, research, translation, or external-validation gaps. Items whose repository source implementation was completed during reconciliation are stated as **activation/validation gaps**, not as missing source code.

| Gap ID | Description | Handling |
|--------|-------------|----------|
| G-001 | Full-text archival storage of every cited Canadian primary source was not performed | Citation includes official title and publishing body; URL recorded in bibliography; absence of local archive noted |
| G-002 | No external peer review performed | Internal/adversarial validation records exist; independent external review remains a future validation objective |
| G-003 | Real deployment benchmark data not available | Synthetic benchmark data is labelled; operational claims require real deployment evidence |
| G-004 | Indigenous rights-holder engagement not performed | Public-framework analysis only. Engagement is required before deployments that materially affect Indigenous rights, community data, governance authority, or services; it is not a universal prerequisite for unrelated implementations |
| G-005 | Provincial AI legislative developments tracked at high level only | Federal-provincial analysis identifies the interaction pattern; time-sensitive provincial/legal monitoring remains required before consequential reliance |
| G-006 | Operational cost data from a deployed AI-IDP system not available | Cost-benefit analysis is model-based; production cost/performance evidence remains external |
| G-007 | PQC source paths are implemented but not freshly runtime-validated | ML-DSA-65 and SLH-DSA SHA2-128s liboqs keygen/sign/verify source paths exist on the reconciliation branch; fresh execution with the pinned liboqs runtime and target deployment assurance remain pending* |
| G-008 | Signed federation source exists but no real external registry federation has been validated | AegisTrace includes signed bilateral agreement verification, public-safe resolution, bounded caching, break detection, and disclosed-chain verification; independent remote registry operators, controlled/sealed federation and live inter-jurisdiction validation remain external* |
| G-009 | MCP adapter is not validated against a production MCP server | Adapter source implements its evidence-collection surface; live integration with an external production MCP server remains pending* |
| G-010 | Full French edition of the entire corpus has not been produced | Bilingual identity and key French deliverables exist; a complete French edition remains a publication objective |
| G-011 | HSM/KMS source paths require target-environment evidence | PKCS#11, AWS KMS, Azure Key Vault and Google Cloud KMS signing source paths are implemented; actual device/account credentials, custody/configuration and live validation remain pending* |
| G-012 | Shared durable governance state requires live deployment evidence | SQLite and PostgreSQL replay/approval-consumption source mechanisms are implemented; live multi-process/multi-node database behavior, failover and operational assurance remain pending* |
| G-013 | External IAM/directory entitlement binding not configured | Approver-entitlement contract, fail-closed default, static grants and composition exist; organization-specific IAM/directory integration and role governance remain deployment-specific* |
| G-014 | Government/standards adoption, accreditation and certification are not established | AI-IDP remains a proposed standard/legal objective; no government, Standards Council, accredited certification or regulator-operated AI-IDP infrastructure is claimed |

## Capability-status convention

An asterisk (`*`) identifies a capability whose **source implementation exists but live activation, target-environment validation, external operator/institutional participation, hardware, credential, runtime or independent assurance is still required**.

The convention must not be used to hide missing source implementation. If a capability can reasonably be implemented within the repository, it should be implemented or explicitly registered as an implementation gap.
