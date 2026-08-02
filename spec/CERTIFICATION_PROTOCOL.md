---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
Secondary Contact: p.1o9.cognitive@outlook.com
Telephone: +1 (581) 668-2372
Location: Saguenay, Québec, Canada
File: spec/CERTIFICATION_PROTOCOL.md
Title: Certification Protocol
Purpose: Define how conformity is certified
Audience: Certification bodies, regulators, controllers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: CONFORMANCE_LEVELS.md; AUDIT_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Certifications are evidence-based and revocable
Failure Behaviour: Unsupported certifications are forbidden
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Certification Protocol

## 1. Certification Body

A certification body is an accredited organization that certifies conformity to AI-IDP conformance levels. Certification bodies are accredited by an accreditation authority (e.g., the Standards Council of Canada).

## 2. Certification Procedure

Certification:

1. A controller submits a certification application.
2. The certification body assigns an auditor.
3. The auditor performs a conformance audit (per `AUDIT_PROTOCOL.md`).
4. The certification body reviews the audit report.
5. The certification body issues a certification (or denies it).
6. The certification is recorded as a signed event in the registry's public tier.

## 3. Certification Record

A certification record contains:

- `certification_id` — unique identifier.
- `certified_controller_id` — the certified controller.
- `certified_agent_id` — the certified agent (if applicable).
- `conformance_level` — L1, L2, L3, or L4.
- `scope` — the certification scope (e.g., specific deployments, specific sectors).
- `issued_at` — issuance timestamp.
- `expires_at` — expiry timestamp.
- `audit_id` — the underlying audit identifier.
- `certification_body_id` — the certification body.
- `signature` — cryptographic signature by the certification body.

## 4. Certification Revocation

A certification may be revoked by the certification body for cause (e.g., conformance failure, incident, fraud). Revocation is recorded as a signed event in the registry's public tier.

## 5. Certification Renewal

Certifications expire. Renewal requires a new conformance audit.

## 6. Public Disclosure

Certifications are public-tier records. The public registry exposes:

- The certified controller's identity.
- The certified agent's identity (if applicable).
- The conformance level.
- The scope.
- The issuance and expiry timestamps.
- The certification body.
- The revocation status.

## 7. Invariants

- Certifications are evidence-based.
- Certifications are signed.
- Certifications are revocable.
- Certifications expire.
- Certifications are public-tier records.
- Unsupported certifications are forbidden.
