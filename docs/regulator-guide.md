# AegisTrace Regulator Guide

Last Material Revision: 2026-08-01

## Registry Tiers

AI-IDP defines four registry visibility tiers (see `spec/REGISTRY_PROTOCOL.md`):

- **PUBLIC** — accessible to any party; contains only approved non-sensitive fields.
- **CONTROLLED** — accessible to authorized regulators, auditors, and certification bodies.
- **ORGANIZATION-PRIVATE** — accessible to the controlling organization.
- **SEALED** — accessible only under judicial or regulator-controlled disclosure.

## Regulator Access

Regulators have controlled-tier access. Regulator access is logged and auditable. Regulators may access:

- Provider registrations (with non-public operational metadata)
- Model registrations (with non-public evaluation metadata)
- Deployment records
- Controller records
- Agent definitions, versions, configurations
- Agent-instance records
- Task records, delegation records, authorization records
- Action ledgers (with non-public event metadata)
- Resource manifests
- Quality evidence
- Incidents, revocations, corrections, audit reports

## Sealed-Record Access

Sealed records are accessible only under judicial or regulator-controlled disclosure. Sealed-record access requires:

- A court order or regulator order
- A documented disclosure purpose
- A disclosure log entry
- Encryption of the disclosed data in transit and at rest

## Incident Notification

High-severity and critical incidents are reported to the regulator. The notification includes the incident record, the investigation log, the resolution, and the remediation evidence.

## Annual Reporting

The regulator reports annually to Parliament on:
- The state of the national AI-IDP registry
- Incident trends and resolutions
- Conformance and certification activity
- Provincial federation status
- Civil-society oversight board findings
- Recommendations for legislative or regulatory amendments

## Enforcement

Regulators have enforcement options (see `government/ENFORCEMENT_OPTIONS.md`):

- Civil penalties (administrative monetary penalties)
- Service suspension (regulator authority to suspend non-compliant services)
- Procurement bar (non-compliant agents barred from federal procurement)
- Civil liability (statutory civil liability for harms caused by non-compliant operation)
- Evidentiary consequences (non-compliant operation creates evidentiary presumptions)
- Criminal referral (for fraudulent attribution, evidence tampering)

# AegisTrace Regulator Guide
