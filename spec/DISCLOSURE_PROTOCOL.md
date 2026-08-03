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
File: spec/DISCLOSURE_PROTOCOL.md
Title: Disclosure Protocol
Purpose: Define what may be disclosed, to whom, under what authority
Audience: Architects, privacy officers, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: REGISTRY_PROTOCOL.md; PERMANENT_RECORD_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Disclosure follows visibility tiers
Failure Behaviour: Unauthorized disclosure is a defect
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Disclosure Protocol

## 1. Visibility Tiers

Every event has a visibility tier:

- **PUBLIC** — visible to any party (only non-sensitive fields).
- **CONTROLLED** — visible to authorized regulators, auditors, certification bodies.
- **ORGANIZATION_PRIVATE** — visible to the controlling organization.
- **SEALED** — visible only under judicial or regulator-controlled disclosure.

## 2. Public Disclosure

Public disclosure includes only:

- Public provider identities
- Public model identities
- Public agent identities or classes
- Registry authorities
- Public verification keys
- Protocol versions
- Schema versions
- Revocation status
- Certification status
- Conformity status
- Signed ledger roots
- Merkle roots
- Release attestations
- Public schemas
- Public specifications

Public disclosure excludes:

- Personal information
- Sealed identity resolution
- Sealed evidence payloads
- Confidential prompts and outputs
- Confidential client files
- Trade secrets
- Security-sensitive details (e.g., specific vulnerabilities, internal network topology)

## 3. Controlled Disclosure

Controlled disclosure is to authorized regulators, auditors, and certification bodies. Disclosure requires:

- The requester's authorization (e.g., a regulator's statutory authority).
- A documented disclosure purpose.
- A disclosure log entry.

## 4. Sealed Disclosure

Sealed disclosure is under judicial or regulator-controlled authority. Disclosure requires:

- A court order or regulator order.
- A documented disclosure purpose.
- A disclosure log entry.
- Encryption of the disclosed data in transit and at rest.

## 5. Redaction

Redaction removes sensitive content from a record while preserving the integrity proof. Redaction is separately authorized and recorded.

## 6. Access Logging

All access to non-public records is logged. Access logs are themselves permanent records.

## 7. Recourse

Affected persons have a documented recourse mechanism for disputes, corrections, and revocations. The recourse mechanism is defined in `administration/APPEALS_AND_CORRECTIONS.md`.

## 8. Indigenous Data Governance

Disclosure of Indigenous data follows Indigenous data governance principles (OCAP®; First Nations, Inuit, and Métis distinctions; TRC Calls to Action). Community-controlled access is enforced.

## 9. Invariants

- Disclosure follows visibility tiers.
- Unauthorized disclosure is a defect.
- Access is logged.
- Redactions preserve integrity proofs.
- Recourse is available.
- Indigenous data governance is respected.
