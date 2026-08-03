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
File: spec/AUDIT_PROTOCOL.md
Title: Audit Protocol
Purpose: Define how audits are performed
Audience: Auditors, regulators, controllers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: EVENT_PROTOCOL.md; QUALITY_EVIDENCE_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Audits are independent and evidence-based
Failure Behaviour: Audit failures are escalated
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Audit Protocol

## 1. Audit Types

AI-IDP defines:

- **Conformance audit** — verifies conformance to a specified AI-IDP conformance level.
- **Security audit** — verifies security properties (forgery detection, key management, registry integrity).
- **Privacy audit** — verifies privacy properties (minimization, pseudonymization, sealed-record access).
- **Operational audit** — verifies operational properties (ledger integrity, manifest consistency, incident response).
- **Compliance audit** — verifies compliance with applicable law and regulation.
- **Financial audit** — verifies financial impacts (penalties, civil liability, insurance).

## 2. Audit Scope

Audit scope includes:

- The ledger (events, hash chain, signatures).
- The registry (entities, states, bindings).
- The evidence store (quality evidence, supply-chain evidence).
- The manifests (resource manifests, integrity).
- The policies (versions, enforcement).
- The incidents (reports, investigations, resolutions).
- The disclosures (access logs, redactions).

## 3. Audit Procedure

An audit is performed by:

1. The auditor opens an audit with a defined scope and procedure.
2. The auditor collects evidence from the ledger, registry, evidence store, manifests, policies, incidents, and disclosures.
3. The auditor verifies the evidence (signatures, hash chain, schema compliance, policy compliance).
4. The auditor documents findings in an audit report.
5. The auditor signs the audit report.
6. The audit report is recorded as a signed event in the ledger.

## 4. Audit Report

An audit report contains:

- `audit_id` — unique identifier.
- `audit_type` — conformance, security, privacy, operational, compliance, financial.
- `scope` — the audit scope.
- `procedure` — the audit procedure reference.
- `findings` — list of findings (severity, description, evidence).
- `recommendations` — list of recommendations.
- `conclusion` — overall conclusion (pass, fail, conditional).
- `auditor_id` — the auditor's identifier.
- `audited_at` — audit timestamp.
- `signature` — cryptographic signature by the auditor.

## 5. Audit Independence

Auditors are independent of the controllers they audit. Auditors are accredited by an accreditation body. Auditor accreditation is recorded in the registry.

## 6. Audit Frequency

Audit frequency is defined by policy:

- High-conformance-level (L4) implementations: annual conformance audit; quarterly security audit.
- Medium-conformance-level (L3) implementations: biennial conformance audit; semi-annual security audit.
- Low-conformance-level (L1–L2) implementations: triennial conformance audit; annual security audit.
- Incident-triggered audits: as needed.

## 7. Invariants

- Audits are independent.
- Audits are evidence-based.
- Audit reports are signed.
- Audit findings are recorded.
- Audit failures are escalated.
