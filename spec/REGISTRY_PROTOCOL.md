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
File: spec/REGISTRY_PROTOCOL.md
Title: Registry Protocol
Purpose: Define the structure, tiers, and operation of registries
Audience: Architects, registry operators, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: ACTOR_MODEL.md; DISCLOSURE_PROTOCOL.md; FEDERATION_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Registry tiers are enforced
Failure Behaviour: Cross-tier leakage is a defect
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Registry Protocol

## 1. Registry Tiers

AI-IDP defines four registry tiers:

### 1.1 Public

The public tier is accessible to any party. It contains only approved non-sensitive fields:

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

### 1.2 Controlled

The controlled tier is accessible to authorized regulators, auditors, and certification bodies. It contains:

- Provider registrations (with non-public operational metadata)
- Model registrations (with non-public evaluation metadata)
- Deployment records
- Controller records (with non-public organizational metadata)
- Agent definitions, versions, configurations
- Agent-instance records (with non-public execution metadata)
- Task records, delegation records, authorization records
- Action ledgers (with non-public event metadata)
- Resource manifests
- Code-review evidence, test evidence, CI evidence, build evidence, release evidence
- Incidents, revocations, corrections, audit reports

### 1.3 Organization-Private

The organization-private tier is accessible to the controlling organization. It contains:

- User and principal identities (pseudonymous externally; resolved internally)
- Full action ledgers
- Full evidence payloads
- Internal policy records
- Internal approval records

### 1.4 Sealed

The sealed tier is accessible only under judicial or regulator-controlled disclosure. It contains:

- Sealed identity resolution (mapping pseudonymous identifiers to real identities)
- Sealed evidence payloads (encrypted; access-controlled)
- Sealed approval records (e.g., judicial authorizations)

## 2. Registry Authority

The registry authority operates the public and controlled tiers. Sectoral registry authorities operate sectoral controlled tiers. Provincial registry authorities operate provincial controlled tiers. The federation protocol (see `FEDERATION_PROTOCOL.md`) governs inter-registry operation.

## 3. Registry API

The registry exposes:

- **Public API** — read-only access to public-tier records.
- **Controlled API** — read access for authorized regulators/auditors/certification bodies; write access for registry operators.
- **Organization-private API** — read/write access for the controlling organization.
- **Sealed API** — read access only under judicial or regulator-controlled disclosure.

## 4. Registry Operations

### 4.1 Register

A new entity is registered by submitting a registration request to the registry. The request is validated against the schema, the requesting entity's authority is verified, and the entity is minted with a permanent identifier.

### 4.2 Update

An entity may be updated by appending update events. Prior attributes are preserved.

### 4.3 Lookup

An entity may be looked up by its permanent identifier. The lookup returns the entity's current state and public attributes.

### 4.4 Resolve

An entity may be resolved to its full record (per the visibility tier and the requester's authorization).

### 4.5 Verify

An entity may be verified for state (active, suspended, revoked, terminated), bindings, and signature validity.

### 4.6 Revoke

An entity may be revoked. Revocation is a new signed event; historical records are preserved.

### 4.7 Archive

A terminated entity may be archived. The permanent identifier remains resolvable; attributes are reduced.

## 5. Public Verification Repository

The public verification repository is a public GitHub repository (or equivalent) holding only public-tier records:

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

The public verification repository is updated by the registry authority and is read-only for the public.

## 6. Private Evidence Repository

The private evidence repository is a private GitHub repository (or equivalent) holding sensitive evidence:

- Provider registrations
- Model registrations
- Deployment records
- Controller records
- User and principal identities
- Agent definitions, agent versions
- Agent-instance records
- Task records, delegation records, authorization records, approval records
- Action ledgers
- Resource manifests
- Before-and-after digests
- Git commit relationships
- Code-review evidence
- Test evidence, CI evidence, build evidence, release evidence
- Incidents, revocations, corrections
- Audit reports
- Encrypted evidence references

The private evidence repository is accessible only to authorized parties.

## 7. Forbidden Content

Never committed to any repository:

- Private keys
- Access tokens
- Secrets
- Raw credentials
- Unencrypted sensitive personal information
- Confidential prompts
- Confidential outputs
- Confidential client files
- Unrestricted private evidence

## 8. Independent Anchoring

GitHub (or any single repository host) is not the sole root of trust. AI-IDP requires independent:

- Local canonical storage
- Database storage
- Encrypted evidence storage
- Replication
- External signatures
- External anchoring (e.g., to a transparency log or a national archive)
- Archive packages
- Recovery procedures
- Export procedures

## 9. Invariants

- Public-tier records contain only approved non-sensitive fields.
- Controlled-tier records are accessible only to authorized parties.
- Organization-private records are accessible only to the controlling organization.
- Sealed records are accessible only under judicial or regulator-controlled disclosure.
- Registry tiers do not leak.
- Permanent identifiers remain resolvable.
- Registry updates are signed events.
- Independent anchoring provides survivability beyond any single host.
