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
File: SECURITY.md
Title: Security Policy
Purpose: Define security reporting and handling
Audience: Security researchers, operators, auditors
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Approved
Last Material Revision: 2026-08-01
Dependencies: threat-model/THREAT_MODEL.md
Source Basis: Master Execution Prompt
Invariants: Security reports are handled confidentially
Failure Behaviour: Security failures are recorded as incidents
Trace Policy: Security events are first-class AegisTrace events
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Security Policy

## Reporting a Vulnerability

Security correspondence: Pierre-Edward Procyk, Cognitive Industries — Les Industries Cognitives, p.procyk.media@gmail.com. For sensitive reports, please use encrypted email.

When reporting, include: affected component (module, file, schema, CLI, API endpoint); affected version; description of the vulnerability; reproduction steps; impact assessment; suggested mitigation.

## Threat Model

See `threat-model/THREAT_MODEL.md` for the complete threat model, attack trees, abuse cases, and mitigations.

## Security Properties

The AegisTrace reference implementation enforces the following security properties (verified by `tests/security/`): forged agent/user/provider/model events are rejected by signature verification; stolen or revoked keys cannot produce valid new events; replay attacks are detected by sequence numbers and timestamps; event deletion, insertion, reordering, and timestamp manipulation are detected by hash chaining; modified digests are detected by event hash verification; hidden model substitution is detected by execution-context verification; adapter bypass is prevented by mandatory event collection; watcher bypass is detected by periodic reconciliation; unauthorized child agents are rejected by delegation verification; approval reuse is prevented by single-use approval records; path traversal, command injection, and secret leakage are prevented by input validation; Git history rewriting is detected by external Merkle anchoring; registry tampering is detected by independent replication; malicious administrator erasure is detected by independent archival replication; denial of logging is treated as a fail-closed incident.

## Cryptographic Choices

Signatures: Ed25519 (RFC 8032) via the `cryptography` library. No custom primitives. Hashes: SHA-256 for content and event hashes. BLAKE2b-256 available for high-throughput paths. Key management: key service with rotation, suspension, revocation, and termination. Sealed records for high-value keys.

## Cryptographic Migration

The signing interface is abstract. Ed25519 can be migrated to a post-quantum scheme (e.g., CRYSTALS-Dilithium or SLH-DSA) when standardized and mature. The migration is documented in `spec/PERMANENT_RECORD_PROTOCOL.md`.
