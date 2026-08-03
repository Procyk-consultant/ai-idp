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
File: spec/CORRECTION_PROTOCOL.md
Title: Correction Protocol
Purpose: Define how errors are corrected by appending new signed events
Audience: Architects, implementers, auditors
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: PERMANENT_RECORD_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Corrections append; they do not overwrite
Failure Behaviour: Overwriting history is forbidden
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Correction Protocol

## 1. Purpose

Errors in events, registry records, or evidence are corrected by appending new signed events. The original record is preserved.

## 2. Correction Record

A correction record contains:

- `correction_id` — unique identifier.
- `corrected_record_id` — the original record's identifier.
- `correction_reason` — the reason for the correction.
- `corrected_fields` — the corrected field values.
- `correcting_principal_id` — the principal correcting.
- `corrected_at` — correction timestamp.
- `signature` — cryptographic signature by the correcting principal.

## 3. Correction Authority

Correction authority is defined by policy:

- The original signer may correct their own records.
- A controller may correct their organization's records.
- A regulator may correct any record for cause.
- A court may correct any record under judicial authority.

## 4. Correction Operations

### 4.1 Issue

A correction is issued by an authorized principal. The correction is recorded as a signed event in the ledger.

### 4.2 Verify

A correction is verified by:

1. The correction record exists.
2. The correcting principal is authorized.
3. The signature is valid.
4. The corrected record exists.

### 4.3 Resolve

When resolving a corrected record, the resolver returns both the original and the correction. The correction is treated as authoritative for the corrected fields; the original is preserved for history.

## 5. Invariants

- Corrections append; they do not overwrite.
- The original record is preserved.
- The correction is signed.
- Corrections are verifiable.
- Resolvers return both original and correction.
