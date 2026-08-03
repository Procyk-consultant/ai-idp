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
File: government/FEDERAL_PROCUREMENT_PROFILE.md
Title: Federal Procurement Profile
Purpose: Define AI-IDP requirements for federal procurement of AI-enabled systems
Audience: Federal procurement officers, federal departments, suppliers
Document Classification: Public
Classification: policy
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: spec/AI-IDP-CORE.md; AI-IDP-CANADA.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials
Invariants: Distinguishes current law from proposed law
Failure Behaviour: Misclassification of legal status is a defect
Trace Policy: No AegisTrace event record required
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Federal Procurement Profile

## 1. Application

This profile applies to federal procurement of AI-enabled systems, including systems that incorporate AI agents, AI models, or AI services. The profile integrates with the Treasury Board Contracting Policy and the Directive on Automated Decision-Making.

## 2. Conformance Level Requirements

Federal procurement requires AI-IDP conformance at the following levels:

- L1: low-risk AI agents (personal productivity, internal automation) — minimum acceptable
- L2: moderate-risk AI agents (internal decision support, customer service) — minimum acceptable for most federal procurement
- L3: high-risk AI agents (public-facing decision support, case-worker decision support) — required for federal procurement of high-impact automated decision systems
- L4: maximum-assurance AI agents (critical infrastructure, national security) — required for federal procurement of critical infrastructure AI

## 3. Procurement Contract Clauses

Federal procurement contracts for AI-enabled systems include the following AI-IDP clauses:

- AI Actor Identifier provision: the supplier shall provide AI Actor Identifiers for all agents supplied.
- Conformance certification: the supplier shall provide conformance-level certification by an accredited body.
- Trace-evidence integration: the supplier shall integrate with the procuring department's AegisTrace instance.
- Incident reporting: the supplier shall report incidents to the procuring department within 72 hours.
- Evidence preservation: the supplier shall preserve evidence for the contract term plus seven years.
- Audit access: the supplier shall provide audit access to the procuring department, the regulator, and accredited auditors.
- Revocation effect: upon revocation of an AI Actor Identifier, the supplier shall cease deployment of the affected agent within 30 days.

## 4. Supplier Due Diligence

Federal procurement officers conduct AI-IDP due diligence on suppliers, including: verification of the supplier's registry record; verification of the supplier's conformance certification; review of the supplier's incident history; review of the supplier's key-management practices; review of the supplier's revocation history.

## 5. Indigenous Procurement

Federal procurement of AI-enabled systems for Indigenous communities or affecting Indigenous data shall comply with the Indigenous data-governance provisions of AI-IDP and the federal Indigenous Procurement Policy.
