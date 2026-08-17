---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Location: Saguenay, Québec, Canada
File: spec/AI-IDP-CORE.md
Title: AI-IDP Core Specification
Purpose: Define core concepts, invariants, and requirements of the proposed AI-IDP standard
Audience: Architects, implementers, legal reviewers, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready / reconciliation clarified
Last Material Revision: 2026-08-17
Dependencies: ACTOR_MODEL.md; IDENTITY_PROTOCOL.md; EVENT_PROTOCOL.md; AUTHORIZATION_PROTOCOL.md; DELEGATION_PROTOCOL.md; APPROVAL_PROTOCOL.md; DISCLOSURE_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Failure Behaviour: Invariant violations are non-conformant and reportable according to applicable incident policy
Trace Policy: This specification defines the core trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# AI-IDP Core Specification

## 1. Purpose and status

AI-IDP — Universal AI Identity, Delegation, Provenance, Traceability, Quality, Accountability, and Permanent Audit — is a **proposed Canadian legal and technical standard**. It is not current Canadian law, an adopted national standard, or a certification regime currently conferred on this repository.

**AegisTrace** is the reference implementation used to make the proposed mechanisms concrete, inspectable, testable, and auditable.

AI-IDP distinguishes current law/regulation/policy/guidance from proposed future AI-IDP requirements. Existing legal obligations remain governed by the actual instruments and authorities that issue them.

## 2. Core actor model

The standard distinguishes:

- jurisdiction and registry authority;
- identity issuer;
- provider and provider service;
- organization and accountable controller;
- human/service principal and user;
- model family/model/model version/model artifact;
- deployment/endpoint;
- orchestrator;
- persistent agent and runtime agent instance;
- parent/child agent and swarm;
- tool, connector, execution environment, device, session;
- task, delegation, authorization, approval, policy;
- action, event, resource, repository/database/artifact;
- quality evidence, incident, audit, certification, correction, revocation, legal hold.

## 3. Canonical principles

1. **Persistent agent identity precedes autonomous action.** The logical software actor has a persistent identifier that survives runtime/provider/model changes.
2. **Runtime instance is distinct from persistent identity.** Each execution instance is separately identifiable.
3. **Models/providers are execution components, not the persistent actor.** Switching them does not silently change agent identity.
4. **Every governed action resolves to authority.** Principal/controller/authorization and, where applicable, delegation/approval chains are reconstructable.
5. **High-impact approval applies to an exact action intent.** An approval is not a reusable permission for an action verb; material action facts are committed by a canonical digest.
6. **Canonical event evidence is signed and hash-chained.** Missing, reordered, duplicated, or modified history is detectable.
7. **Evidence collection and governance enforcement are distinguishable.** A trace collector cannot be represented as proof that authorization was enforced unless the action actually crossed the governed boundary.
8. **Public verification is not raw-public disclosure.** Public interfaces use reviewed projections that preserve verification while minimizing sensitive context.
9. **Corrections append; they do not silently rewrite history.**
10. **Implementation, validation, certification, adoption, and law are separate states.**

## 4. Required invariants

An implementation claiming AI-IDP conformance must preserve at least the following invariants:

1. Every agent instance resolves to one persistent agent.
2. Every persistent agent resolves to an accountable controller.
3. Every governed action resolves to an active agent instance.
4. Every governed action resolves to a task.
5. Every governed task/action resolves to a verifiable authority chain.
6. Every delegated child action resolves through an unbroken parent-delegation chain.
7. Every model-execution span identifies provider, model, version, and deployment.
8. Model switching preserves persistent agent identity.
9. Provider switching preserves persistent agent identity.
10. Revocation preserves historical evidence.
11. Termination preserves historical evidence.
12. Resource deletion does not erase the action record.
13. Corrections append rather than overwrite canonical history.
14. Every canonical event is cryptographically linked.
15. Every quality claim resolves to evidence appropriate to that claim.
16. Public verification does not require disclosure of raw private content.
17. Canonical history is independently verifiable with appropriate public verification material.
18. Missing, reordered, duplicated, or modified records are detectable.
19. An agent cannot silently alter canonical history through supported interfaces.
20. An administrator cannot silently erase canonical history through conformant interfaces.
21. A provider/model substitution relevant to execution is traceable.
22. An action cannot be silently reassigned to another agent or principal.
23. A restricted authority/scope dimension fails closed when the required context cannot be established.
24. Approval-gated actions match the exact approved action-intent digest.
25. Public event disclosure is allow-list based rather than automatic raw serialization.
26. Remote possession of an identifier alone is not authentication for a governed write boundary.

## 5. Action coverage

The canonical vocabulary includes discovery/read/search/query operations; create/generate/modify/delete/restore operations; execute/build/test/debug operations; install/configuration/connect/authentication/authorization operations; transmit/import/export/publication/deployment/release/version-control operations; sign/verify/approve/reject/decide/recommend operations; delegation/agent-creation/model-provider-tool-policy changes; revoke/pause/terminate/rollback; destructive/key/secret/credential/API/database/infrastructure/production/external-effect operations.

`RESOURCE_TRACE_PROTOCOL.md` and related protocols define trace granularity and high-impact controls. Organizational/deployment policies may be stricter than the reference defaults but must not weaken core invariants.

## 6. Governed operational boundary

A governed action is accepted only after the applicable implementation establishes:

1. authenticated submitting actor/request at remote boundaries;
2. active identity/controller/instance/execution-context relationships;
3. valid signed authorization and exact actor/task/controller/principal binding;
4. fail-closed scope evaluation;
5. complete delegation lineage when applicable;
6. canonical exact action-intent digest;
7. required single/dual approval set for that digest;
8. signed/hash-chained canonical event evidence.

A denied action remains denied even if denial evidence cannot itself be recorded.

## 7. Trace structure and permanence

Protected resources may contain or resolve to `.aitrace/` manifests/ledgers/evidence, or equivalent sidecar/central/federated storage. Canonical trace evidence is append-oriented, sequence-aware, tamper-evident, and designed for independent verification and archival replication appropriate to the assurance level.

AegisTrace's reference in-memory ledger isolates canonical records from caller mutation; production storage must provide equivalent backend-appropriate guarantees.*

## 8. Authorization, delegation, and approval

Authorization is signed and bounded. Restricted task/resource/geography/tool/model/provider/time/depth dimensions are fail-closed.

Delegation cannot widen parent authority. Nested delegation preserves controller/principal lineage, consumes delegation depth, verifies signatures, and rejects cycles/revoked/expired chains.

Approval-gated actions use a SHA-256 `action_digest` over deterministic action facts, including applicable actor/runtime/execution context, task, action, **visibility**, jurisdiction, delegation, resource, before/after digests, and evaluated scope context. Changing a bound fact requires a new approval.

## 9. Verification and public disclosure

Full verification checks chain integrity, event hashes, and signatures against available public verification keys. A separate explicitly labelled hash-only mode may verify integrity without claiming signature verification.

Public event disclosure is a strict reviewed projection. Sensitive actor, authority, resource, delegation, approval, exact-intent, and denial context remains non-public unless separately authorized by the disclosure protocol.

Public verification-key export must not expose private key material and should not expose private entity bindings by default.

## 10. Quality evidence

Completion language is evidence-bound. `tested`, `verified`, `validated`, `reproducible`, `audit-ready`, `certified`, and `complete` must not be used beyond the evidence actually produced.

A historical passing test result applies to the source/corpus that was executed; material later source changes require a new validation gate before inheriting that claim.

## 11. Registry/disclosure tiers

AI-IDP retains four disclosure/registry tiers:

- PUBLIC;
- CONTROLLED;
- ORGANIZATION_PRIVATE;
- SEALED.

Resolution within a private registry is not equivalent to public disclosure. Public registry fields require an explicit reviewed projection.

## 12. Conformance levels

AI-IDP defines cumulative L1-L4 target assurance levels in `CONFORMANCE_LEVELS.md`. They describe the proposed standard's destination, not automatic certification of the reference repository.

The AegisTrace reference implementation remains non-certified. External certification, accreditation, government adoption, standards-body adoption, procurement acceptance, or legislative enactment requires the applicable external process.*

## 13. Federation and high-assurance infrastructure*

AI-IDP retains federation, independent archival replication, regulator-visible evidence, regulator-controlled/sealed infrastructure, production database/HSM/KMS, transparency anchoring, and cryptographic-migration requirements at the applicable assurance levels.

The reference repository may contain implementation/interface paths for such capabilities without representing the external institutional/hardware/service environment as live.

## 14. Offline operation

AI-IDP supports controlled offline operation using append-only local evidence and later reconciliation. Offline mode must not silently weaken identity, scope, integrity, or conflict-detection invariants.

## 15. Privacy and correction

Permanent accountability evidence is balanced against privacy through minimization, content separation, cryptographic commitments, protected identity resolution, tiered disclosure, controlled/sealed evidence, and append-only correction/revocation records.

Context-specific legal retention/access requirements remain governed by applicable law and policy.

## 16. Indigenous data governance

Where Indigenous rights, community data, governance authority, or services are materially implicated, meaningful distinctions-based rights-holder engagement and appropriate Indigenous data-governance requirements are part of responsible implementation. Public-framework analysis is not a substitute for engagement in those cases.

This is not a universal gate for unrelated deployments with no material Indigenous nexus.

## 17. Versioning and extension

Protocol/schema/specification versions are tracked. Backward-incompatible changes require appropriate versioning/migration. Extensions may strengthen sectoral/provincial/organizational requirements but must not weaken core invariants.

## 18. Relationship to existing standards

AI-IDP is designed to interoperate conceptually/technically with relevant identity, provenance, software-supply-chain, observability, SBOM, security/privacy, and assurance standards such as SPIFFE/SPIRE, W3C PROV/DID/VC where applicable, in-toto/SLSA/Sigstore, OpenTelemetry, SPDX/CycloneDX, ISO/IEC 27001-family controls, NIST security/identity/SSDF guidance, and Ed25519/SHA standards.

Interoperability claims must be limited to what is actually mapped/implemented/validated in the corresponding project evidence.

## 19. Normative conformance statement

An implementation may claim AI-IDP conformance only when the requirements of the claimed level, the core invariants, applicable protocols/schemas, and the certification requirements in `CERTIFICATION_PROTOCOL.md` are satisfied by appropriate evidence.

Self-assessment, reference implementation status, or passing internal tests are not by themselves certified conformance.

> `*` Starred capabilities/assurance requirements depend on the applicable external infrastructure, service, hardware, deployment topology, regulator/institutional authority, or independent certification process. This notation preserves the normative target while accurately describing activation status.
