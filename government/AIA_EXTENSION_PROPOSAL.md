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
File: government/AIA_EXTENSION_PROPOSAL.md
Title: Algorithmic Impact Assessment Extension Proposal
Purpose: Propose an extension to the Treasury Board Algorithmic Impact Assessment that integrates AI-IDP registration
Audience: Treasury Board of Canada Secretariat, federal departments
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

# Algorithmic Impact Assessment Extension Proposal

## 1. Current AIA

The Treasury Board Directive on Automated Decision-Making requires federal institutions to complete an Algorithmic Impact Assessment (AIA) for automated decision systems. The AIA evaluates the impact level (I, II, III, IV) based on project risk factors. Higher-impact systems require more rigorous requirements (peer review, approval, disclosure, training, human intervention).

## 2. Proposed Extension

The proposed extension adds AI-IDP registration as a required field in the AIA, with trace-evidence requirements for high-impact automated decisions. The extension integrates AI-IDP with the existing AIA framework without replacing it.

## 3. Extension Fields

The extension adds the following fields to the AIA:

- AI Actor Identifier (required for impact levels II, III, IV)
- Controller identifier (required for all impact levels)
- Conformance level (L1, L2, L3, L4 — required minimum level by impact: L1 for I, L2 for II, L3 for III, L4 for IV)
- Trace-evidence location (URL or reference to the AegisTrace ledger)
- Quality-evidence location (URL or reference to the quality-evidence record)
- Incident-reporting acknowledgment (yes/no)

## 4. Trace-Evidence Requirements

For impact levels III and IV, the AIA extension requires trace evidence for at least the following decision types: (1) decisions affecting individual rights (immigration, benefits, taxation); (2) decisions affecting individual safety (healthcare, transportation); (3) decisions affecting critical infrastructure (energy, communications, finance); (4) decisions affecting national security.

## 5. Implementation

The AIA extension is implemented through Treasury Board Directive amendment. The amendment adds the new fields to the AIA instrument and requires federal institutions to complete the new fields for new and existing automated decision systems. The amendment is coordinated with the Treasury Board Contracting Policy for federal procurement of AI-enabled systems.

## 6. Relationship to AI-IDP

The AIA extension is one pathway to AI-IDP adoption. The extension covers federal public-sector automated decision systems. Other pathways (standards, legislative, procurement) cover other AI agents. The AIA extension is the most direct pathway for federal public-sector adoption because it builds on the existing AIA framework.
