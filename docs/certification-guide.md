# AegisTrace Certification Guide

Last Material Revision: 2026-08-01

## Conformance Levels

AI-IDP defines four conformance levels (L1-L4). See `spec/CONFORMANCE_LEVELS.md`.

- **L1 (Baseline):** persistent identifiers, signed events, local ledger, basic offline operation.
- **L2 (Standard):** L1 + public verification, private evidence, delegation, authorization, approval, resource manifests, filesystem and Git adapters.
- **L3 (High Assurance):** L2 + independent archival replication, federation, database and CI/CD adapters, privacy tests, permanence tests, annual conformance audit.
- **L4 (Maximum Assurance):** L3 + dual approval, regulator-controlled vault, real-time transparency log anchoring, PQC readiness, quarterly security audit, annual privacy audit, annual operational audit, public certification.

## Certification Procedure

1. A controller submits a certification application.
2. The certification body assigns an auditor.
3. The auditor performs a conformance audit.
4. The certification body reviews the audit report.
5. The certification body issues a certification (or denies it).
6. The certification is recorded as a signed event in the registry's public tier.

## Certification Record

A certification record contains:

- `certification_id`
- `certified_controller_id`
- `certified_agent_id`
- `conformance_level` (L1, L2, L3, L4)
- `scope`
- `issued_at`
- `expires_at`
- `audit_id`
- `certification_body_id`
- `signature`

## Certification Revocation

A certification may be revoked by the certification body for cause. Revocation is recorded as a signed event in the registry's public tier.

## Certification Renewal

Certifications expire. Renewal requires a new conformance audit.

# AegisTrace Certification Guide
