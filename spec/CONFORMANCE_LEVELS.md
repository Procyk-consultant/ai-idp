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
File: spec/CONFORMANCE_LEVELS.md
Title: Conformance Levels
Purpose: Define the four AI-IDP conformance levels
Audience: All readers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: AI-IDP-CORE.md; CERTIFICATION_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Conformance levels are tiered and cumulative
Failure Behaviour: False conformance claims are forbidden
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Conformance Levels

AI-IDP defines four conformance levels (L1–L4). Levels are cumulative: each level includes all requirements of lower levels.

## L1 — Baseline

L1 is the minimum baseline. L1 implementations:

- Issue persistent AI Actor identifiers for all agents.
- Issue runtime agent instance identifiers.
- Record material actions as signed, hash-chained events.
- Maintain a local append-only ledger.
- Verify the ledger integrity on demand.
- Support basic offline operation with reconciliation.
- Provide a verify CLI.

L1 is appropriate for: small developers, open-source projects, personal agents, low-risk deployments.

## L2 — Standard

L2 includes L1 plus:

- Public verification repository (Merkle anchoring).
- Private evidence repository (encrypted sensitive evidence).
- Delegation protocol enforcement.
- Authorization and approval protocols.
- Resource manifests for protected directories.
- Filesystem and Git adapters.
- Audit-reconstruction CLI.
- Conformance test suite.

L2 is appropriate for: enterprise deployments, commercial agents, mid-size developers.

## L3 — High Assurance

L3 includes L2 plus:

- Independent archival replication.
- Federation protocol support.
- Database and CI/CD adapters.
- Privacy tests (pseudonymization, sealed records, access logging).
- Permanence tests (key rotation, cryptographic migration, archival restoration).
- Annual conformance audit.
- Incident reporting to regulator.

L3 is appropriate for: regulated sectors (finance, healthcare), public-sector deployments, critical infrastructure.

## L4 — Maximum Assurance

L4 includes L3 plus:

- Dual approval for all high-impact actions.
- Independent regulator-controlled vault.
- Real-time transparency log anchoring.
- Cryptographic migration plan with documented PQC readiness.
- Quarterly security audit.
- Annual privacy audit.
- Annual operational audit.
- Public certification by an accredited body.

L4 is appropriate for: high-impact automated decisions, national-security-related AI, critical infrastructure control systems.

## Conformance Claims

Conformance claims follow the completion language (Master Prompt §37). An implementation may claim "conforms to AI-IDP L{n}" only after a successful conformance audit at that level by an accredited certification body. Self-attestation of conformance is not a conformance claim; it is a "self-attested conformance target" claim.

## Invariants

- Conformance levels are cumulative.
- Conformance claims require certification.
- Self-attestation is not certification.
- Conformance is revocable.
- Conformance expires.
