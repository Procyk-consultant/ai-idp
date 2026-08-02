# AegisTrace Auditor Guide

Last Material Revision: 2026-08-01

## Audit Types

AI-IDP defines six audit types: conformance, security, privacy, operational, compliance, and financial. See `spec/AUDIT_PROTOCOL.md` for the full audit protocol.

## Audit Procedure

1. Open an audit with a defined scope and procedure.
2. Collect evidence from the ledger, registry, evidence store, manifests, policies, incidents, and disclosures.
3. Verify the evidence (signatures, hash chain, schema compliance, policy compliance).
4. Document findings in an audit report.
5. Sign the audit report.
6. Record the audit report as a signed event in the ledger.

## Audit Tools

AegisTrace provides three CLIs for audit:

- `aegistrace verify` — verifies a ledger's hash chain, event hashes, and signatures (with a keys file).
- `aegistrace audit` — produces an audit summary (action counts, agent counts, principal counts, visibility distribution).
- `aegistrace reconstruct` — reconstructs an incident timeline by filtering on task, agent, resource, or time range.

## Audit Independence

Auditors are independent of the controllers they audit. Auditors are accredited by an accreditation body. Auditor accreditation is recorded in the registry. No critical agent may be the sole validator of its own output.

## Audit Frequency

- L4: annual conformance audit; quarterly security audit.
- L3: biennial conformance audit; semi-annual security audit.
- L1-L2: triennial conformance audit; annual security audit.
- Incident-triggered audits: as needed.

## Audit Report

An audit report contains:

- `audit_id` — unique identifier
- `audit_type` — conformance, security, privacy, operational, compliance, financial
- `scope` — the audit scope
- `procedure` — the audit procedure reference
- `findings` — list of findings (severity, description, evidence)
- `recommendations` — list of recommendations
- `conclusion` — overall conclusion (pass, fail, conditional)
- `auditor_id` — the auditor's identifier
- `audited_at` — audit timestamp
- `signature` — cryptographic signature by the auditor

# AegisTrace Auditor Guide
