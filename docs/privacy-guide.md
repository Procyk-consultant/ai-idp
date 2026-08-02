# AegisTrace Privacy Guide

Last Material Revision: 2026-08-01

## Privacy Principles

- Minimization
- Purpose limitation
- Pseudonymization
- Sealed records
- Content separation
- Access control
- Correction and revocation
- Retention
- Transparency
- Recourse

## Visibility Tiers

- PUBLIC — accessible to any party (only non-sensitive fields)
- CONTROLLED — accessible to authorized regulators, auditors, certification bodies
- ORGANIZATION-PRIVATE — accessible to the controlling organization
- SEALED — accessible only under judicial or regulator-controlled disclosure

## Pseudonymous Identifiers

User and principal identifiers are pseudonymous by default (`aitrace://ca/principal/user-XYZ`). The mapping to real identity is sealed and access-controlled. Events never contain real email addresses, phone numbers, or LinkedIn URLs.

## Content Separation

Permanent metadata is separated from content. The permanent record may contain a cryptographic commitment without retaining the underlying content. After the retention period, full content may be reduced to commitments.

## Access Logging

All access to non-public records is logged and auditable. Access logs are themselves permanent records.

## Recourse

Affected persons have a documented recourse mechanism for disputes, corrections, and revocations. See `administration/APPEALS_AND_CORRECTIONS.md`.

## Indigenous Data Governance

See `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md` and `research/synthesis/INDIGENOUS_DATA_GOVERNANCE_ANALYSIS.md` for the Indigenous data-governance analysis grounded in OCAP® principles, First Nations, Inuit, and Métis distinctions, and TRC Calls to Action.

# AegisTrace Privacy Guide
