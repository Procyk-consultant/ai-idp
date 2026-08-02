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
File: spec/PERMANENT_RECORD_PROTOCOL.md
Title: Permanent Record Protocol
Purpose: Define how permanent records are preserved, migrated, and accessed
Audience: Architects, implementers, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: EVENT_PROTOCOL.md; DISCLOSURE_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Records are permanent and tamper-evident
Failure Behaviour: Record erasure is forbidden (corrections append)
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Permanent Record Protocol

## 1. Permanence

Permanent records are preserved indefinitely. Permanence applies to:

- **Permanent minimal metadata** — event identifiers, timestamps, action types, actor identifiers, execution context, visibility tier, hash chain references, signature references.
- **Permanent cryptographic commitments** — content digests, Merkle roots, signature values.
- **Permanent registry records** — identity records with state, key bindings, controller bindings.

Full content may be retained according to a retention schedule and may be reduced to commitments after the retention period.

## 2. Tamper-Evidence

Permanent records are tamper-evident:

- Hash chaining detects modification, deletion, insertion, and reordering.
- Signatures detect forgery and key misuse.
- Merkle anchoring provides tamper-evidence beyond the local ledger.
- Independent replication provides tamper-evidence beyond any single copy.

## 3. Correction

Corrections are new signed events that reference the original. The original event is preserved. Correction records contain:

- `corrected_event_id` — the original event's identifier.
- `correction_reason` — the reason for the correction.
- `corrected_fields` — the corrected field values.
- `signature` — the signature of the correcting principal.

Corrections append; they do not overwrite.

## 4. Revocation

Revocations are new signed events that revoke a prior authorization, delegation, approval, identifier, or key. The original record is preserved. Revocation records contain:

- `revoked_record_id` — the revoked record's identifier.
- `revocation_reason` — the reason for the revocation.
- `revoking_principal_id` — the principal revoking.
- `signature` — the signature of the revoking principal.

## 5. Dispute

Disputes are new signed events that dispute a fact in a prior event. The original event is preserved. Dispute records contain:

- `disputed_event_id` — the disputed event's identifier.
- `disputed_field` — the disputed field.
- `dispute_position` — the disputing party's position.
- `disputing_principal_id` — the disputing principal.
- `signature` — the signature of the disputing principal.

## 6. Redaction

Redactions are separately authorized and recorded. Redaction removes sensitive content from a record while preserving the integrity proof. Redaction records contain:

- `redacted_record_id` — the redacted record's identifier.
- `redacted_fields` — the redacted fields.
- `redaction_authority` — the authority authorizing the redaction.
- `redaction_reason` — the reason for the redaction.
- `redacted_at` — the redaction timestamp.
- `signature` — the signature of the redacting authority.

Redactions preserve the hash chain; the redacted record's hash is recomputed and recorded.

## 7. Legal Hold

Legal holds preserve records relevant to a legal proceeding. Legal holds override retention schedules. Legal hold records contain:

- `held_record_ids` — the held records' identifiers.
- `hold_authority` — the authority issuing the hold (e.g., a court).
- `hold_reason` — the reason for the hold.
- `hold_expires_at` — optional expiry of the hold.
- `signature` — the signature of the issuing authority.

Legal holds do not destroy the underlying integrity proof.

## 8. Sealed Records

Sealed records are accessible only under judicial or regulator-controlled disclosure. Sealed records are encrypted with a sealed-record key. The sealed-record key is itself sealed and accessible only to authorized parties. Access to sealed records is logged and auditable.

## 9. Long-Term Signature Migration

Signatures may become obsolete over long horizons (e.g., Ed25519 may eventually be replaced by post-quantum schemes). Long-term signature migration is documented:

1. A new signature scheme is adopted.
2. Existing signatures are re-signed with the new scheme.
3. The re-signing is recorded as a new signed event.
4. The original signatures are preserved.
5. The re-signing event references the original.

## 10. Cryptographic Migration

Cryptographic primitives (hash functions, signature schemes) may be migrated. Migration is documented:

1. A new primitive is adopted.
2. Records are re-hashed or re-signed with the new primitive.
3. The migration is recorded as a new signed event.
4. The original primitives are preserved.

## 11. Independent Archival Replication

Permanent records are independently replicated:

- To an independent archive (e.g., Library and Archives Canada).
- To a regulator-controlled vault.
- To a federated registry.
- To a public transparency log (for public-tier records).

Independent replication provides tamper-evidence beyond any single copy and survivability beyond any single organization.

## 12. Retention

Retention schedules apply to full content (not to permanent minimal metadata or commitments). Retention schedules are defined per record class:

- Public-tier records: indefinite.
- Controlled-tier records: indefinite.
- Organization-private records: per organization policy, with minimums defined by regulation.
- Sealed records: per sealing authority.

After the retention period, full content may be reduced to commitments (hash values) while preserving the permanent metadata.

## 13. Access

Access to permanent records is governed by the visibility tier:

- Public: any party.
- Controlled: authorized regulators, auditors, certification bodies.
- Organization-private: controlling organization.
- Sealed: judicial or regulator-controlled disclosure.

All access to non-public records is logged and auditable. Access logs are themselves permanent records.

## 14. Invariants

- Permanent records are preserved indefinitely.
- Corrections append; they do not overwrite.
- Revocations preserve historical records.
- Disputes preserve the original event.
- Redactions preserve the integrity proof.
- Legal holds do not destroy integrity proofs.
- Sealed records are encrypted and access-controlled.
- Long-term signature migration preserves original signatures.
- Independent archival replication provides survivability.
- Access is logged and auditable.
