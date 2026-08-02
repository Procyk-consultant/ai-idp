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
File: spec/QUALITY_EVIDENCE_PROTOCOL.md
Title: Quality Evidence Protocol
Purpose: Define how quality claims are evidenced and verified
Audience: Architects, implementers, certification bodies
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: EVENT_PROTOCOL.md; CERTIFICATION_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Every quality claim resolves to evidence
Failure Behaviour: Unsupported claims are forbidden
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Quality Evidence Protocol

## 1. Quality Claims

A quality claim is a statement that an artifact or system has a quality property:

- Tested
- Verified
- Implemented
- Validated
- Rendered
- Visually inspected
- Reproducible
- Publication-ready
- Audit-ready
- Complete
- Secure
- Compliant
- Production-ready

## 2. Evidence Types

Each quality claim resolves to evidence:

- **Tested** — test runs (test suite, test name, test result, test log, test environment).
- **Verified** — verification records (verifier, verification procedure, verification result, verification log).
- **Implemented** — code records (repository, commit, file, function, code review).
- **Validated** — validation records (validation procedure, validation result, validation log).
- **Rendered** — rendering records (renderer, rendering parameters, output file, output hash).
- **Visually inspected** — inspection records (inspector, inspection procedure, inspection result, inspection log).
- **Reproducible** — reproduction records (reproducer, reproduction procedure, reproduction result, reproduction log).
- **Publication-ready** — publication-gate records (gate, gate result, gate log).
- **Audit-ready** — audit records (auditor, audit procedure, audit result, audit log).
- **Complete** — completeness records (manifest, manifest verification, completion log).
- **Secure** — security-test records (test suite, test result, security log).
- **Compliant** — conformance records (conformance level, conformance procedure, conformance result, conformance log).
- **Production-ready** — release records (release, release evidence, release attestation).

## 3. Evidence Record

An evidence record contains:

- `evidence_id` — unique identifier.
- `claim` — the quality claim being evidenced.
- `artifact_id` — the artifact or system being claimed about.
- `evidence_type` — the type of evidence (test run, build, release, attestation, audit, certification).
- `evidence_data` — the evidence payload (test logs, build logs, etc.).
- `evidence_hash` — SHA-256 hash of the evidence payload.
- `collected_at` — collection timestamp.
- `collected_by` — collector (agent, instance, principal).
- `signature` — cryptographic signature by the collector.

## 4. Completion Language

The completion language (Master Prompt §37) is normative:

- Use "researched" only after searches are logged and sources inspected.
- Use "verified" only after direct inspection and cross-checking.
- Use "implemented" only when functional code exists.
- Use "tested" only when tests were executed.
- Use "validated" only when a defined validation procedure was executed.
- Use "rendered" only when the output file exists.
- Use "visually inspected" only after actual page or image inspection.
- Use "reproducible" only after a clean rerun.
- Use "publication-ready" only after all paper gates pass.
- Use "audit-ready" only after independent audit evidence exists.
- Use "complete" only when every required artifact and gate passes.

Otherwise use: proposed, designed, drafted, partially implemented, not executed, incomplete, blocked, failed, inconclusive.

## 5. SBOM and Supply-Chain Evidence

Quality evidence includes supply-chain evidence:

- **SBOM** (Software Bill of Materials) — SPDX or CycloneDX format.
- **SLSA provenance** — build provenance per SLSA framework.
- **in-toto attestations** — supply-chain attestations.
- **Sigstore signatures** — artifact signatures via Sigstore.
- **Rekor entries** — transparency log entries.

## 6. AI-Generated Code Quality

For AI-generated code, quality evidence includes:

- Prompt and response provenance (with privacy-preserving digests, not raw prompts/outputs).
- Agent identifier, instance identifier, and execution context.
- Test coverage (which tests cover the AI-generated code).
- Test results (pass/fail per test).
- Code review (reviewer, review log).
- Static analysis (linter, type checker, security scanner).
- Reproduction (a clean rerun of the AI-generated code's tests).

## 7. Engineering Compliance

Quality evidence includes engineering compliance:

- Action tickets for each work unit.
- Plan/Act/Verify/Adapt/Record cycles.
- Decision log entries.
- Test evidence.
- Validation evidence.
- Release evidence.

## 8. Invariants

- Every quality claim resolves to evidence.
- Evidence is signed and hash-chained.
- Evidence is preserved indefinitely.
- Unsupported claims are forbidden.
- Completion language is used correctly.
- Supply-chain evidence is included.
- AI-generated code has AI-specific quality evidence.
