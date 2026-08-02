# AegisTrace Security Guide

Last Material Revision: 2026-08-01

## Threat Model

See `threat-model/THREAT_MODEL.md` for the complete threat model covering 24 threats.

## Security Properties

AegisTrace enforces:

- Forgery resistance
- Revocation enforcement
- Hash-chain integrity
- Event-hash correctness
- Signature verification
- Approval single-use
- Scope enforcement
- Fail-closed operation
- Path-traversal protection
- Public/private separation

## Cryptographic Choices

- Signatures: Ed25519 (RFC 8032)
- Hashes: SHA-256
- Optional: BLAKE2b-256 for high-throughput paths
- Key management: in-memory KeyService (reference); HSM or KMS for production

## Reporting a Vulnerability

Security correspondence: Pierre-Edward Procyk, Cognitive Industries — Les Industries Cognitives, p.procyk.media@gmail.com. For sensitive reports, use encrypted email.

## Cryptographic Migration

The signing interface is abstract. Ed25519 can be migrated to a post-quantum scheme when standardized and mature. See `spec/PERMANENT_RECORD_PROTOCOL.md` for the migration procedure.

## Key Management

Keys have lifecycles: creation, rotation, suspension, revocation, termination. Revoked or terminated keys cannot produce valid new events. Rotated keys remain verifiable. See `spec/IDENTITY_LIFECYCLE.md` for the full lifecycle.

## Hardening for Production

- Use HSM-backed or KMS-backed key storage
- Use PostgreSQL-compatible storage with replication
- Use a higher-throughput append-only store for high-volume deployments
- Add authentication to the API
- Add rate limiting
- Add monitoring and alerting
- Add independent archival replication
- Add Merkle anchoring to a public transparency log

# AegisTrace Security Guide
