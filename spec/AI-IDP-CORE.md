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
File: spec/AI-IDP-CORE.md
Title: AI-IDP Core Specification
Purpose: Define the core concepts, invariants, and requirements of the AI-IDP standard
Audience: Architects, implementers, legal reviewers, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: Master Execution Prompt; ACTOR_MODEL.md; IDENTITY_PROTOCOL.md; EVENT_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: All invariants in Section 18 of the Master Prompt hold
Failure Behaviour: Invariant violations are reportable incidents
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# AI-IDP Core Specification

## 1. Purpose

This specification defines the core concepts, invariants, and requirements of the **AI-IDP** standard — Universal AI Identity, Delegation, Provenance, Traceability, Quality, Accountability, and Permanent Audit. AI-IDP is a proposed Canadian legal and technical standard applicable to all AI agents operating in Canada or materially affecting persons in Canada. The reference implementation is **AegisTrace**.

## 2. Normative Status

AI-IDP is a **proposed** standard. It is **not** current Canadian law. The specification distinguishes:

- Current law (e.g., PIPEDA, Privacy Act, provincial privacy statutes)
- Current regulation, directive, policy, guidance, voluntary codes, standards
- Proposed legislation (e.g., AIDA under Bill C-27)
- Pending legislation
- Proposed AI-IDP requirements
- Proposed future legal obligations

Where AI-IDP references an existing instrument, the reference is to the public-record text published by the issuing authority.

## 3. Conceptual Model

AI-IDP distinguishes the following first-class concepts (formal definitions in `TERMINOLOGY.md`):

- **Jurisdiction** — the legal authority under which the standard operates (Canada, with sub-authority for provinces and territories).
- **Registry authority** — the body authorized to issue and maintain AI Actor identifiers.
- **Identity issuer** — the operational component that mints identifiers under a registry authority.
- **Provider** — the organization that supplies or operates a model or service.
- **Provider service** — a specific service offering of a provider.
- **Organization** — any legal person or entity.
- **Accountable controller** — the organization legally accountable for an agent's operation.
- **Human principal** — the human who authorizes an agent's action.
- **Service principal** — a non-human principal (e.g., another service) that authorizes an agent's action.
- **User** — the end-user on whose behalf an agent acts.
- **Model family / model / model version / model artifact** — the execution component hierarchy.
- **Deployment / endpoint** — where a model is hosted or invoked.
- **Orchestrator** — the system that coordinates agent execution.
- **Persistent agent** — the identifiable logical software actor.
- **Agent version / agent configuration** — versioning of a persistent agent.
- **Runtime agent instance** — a specific execution of an agent.
- **Parent agent / child agent / swarm** — delegation hierarchy.
- **Tool / connector / execution environment / device / session** — execution context.
- **Task / delegation / authorization / approval / policy** — governance records.
- **Action / event / resource / directory / repository / branch / commit / database / transaction / artifact** — execution records.
- **Test run / build / release / attestation** — quality records.
- **Incident / audit / certification / revocation / correction / legal hold** — accountability records.

## 4. Canonical Principles

1. **The persistent agent is the identifiable logical software actor.** A persistent agent has a permanent identifier that survives termination, revocation, provider change, model change, deployment change, and organizational restructuring.
2. **The agent instance is a specific execution of that agent.** A runtime instance has a unique identifier tied to a specific execution context (provider, model, deployment, session).
3. **The model is an execution component.** Models are not agents; they are components used by agents. Switching models does not change the agent's identity.
4. **The provider supplies or operates a model or service.** Switching providers does not change the agent's identity.
5. **The principal grants authority.** Every agent action resolves to a principal (human or service).
6. **The controller remains legally accountable.** Every agent resolves to an accountable controller.
7. **The event record connects all of them.** Every material action produces a signed, hash-chained event that resolves the full chain.

## 5. Required Invariants

The following invariants are normative. An implementation that violates any invariant is non-conformant.

1. Every agent instance resolves to one persistent agent.
2. Every persistent agent resolves to an accountable controller.
3. Every action resolves to an agent instance.
4. Every action resolves to a task.
5. Every task resolves to an authority chain.
6. Every child agent resolves to a parent delegation.
7. Every model-execution span identifies provider, model, version, and deployment.
8. Model switching preserves agent identity.
9. Provider switching preserves agent identity.
10. Revocation preserves historical records.
11. Termination preserves historical records.
12. Resource deletion preserves the action record.
13. Corrections append; they do not overwrite.
14. Every event is cryptographically linked.
15. Every quality claim resolves to evidence.
16. Public verification does not expose raw private content.
17. Canonical history is independently verifiable.
18. Missing or reordered records are detectable.
19. An agent cannot silently alter its canonical history.
20. An administrator cannot silently erase canonical history.
21. A provider cannot silently substitute a model without a trace event.
22. A user cannot silently assign an action to a different agent.
23. An agent cannot silently assign an action to a different user.

## 6. Required Coverage

AI-IDP applies to every AI agent used, created, deployed, distributed, controlled, executed, or made available in Canada or materially affecting persons in Canada, including but not limited to: commercial, enterprise, public-sector, consumer, personal, professional coding, vibe-coding, no-code, low-code, desktop, research, administrative, operational, customer-service, business-process, financial, healthcare-support, educational, local, offline, open-source, embedded, temporary, persistent, autonomous, semi-autonomous, swarm, delegated sub-agent, multi-model, multi-provider, MCP-enabled, terminal-enabled, database-enabled, deployment, CI/CD, and infrastructure agents.

## 7. Required Action Coverage

AI-IDP requires trace records for at least the actions enumerated in Master Prompt §6 (DISCOVER, ENUMERATE, OPEN, READ, SEARCH, QUERY, CREATE, GENERATE, MODIFY, REWRITE, PATCH, MOVE, RENAME, COPY, DELETE, RESTORE, EXECUTE, RUN, COMPILE, BUILD, TEST, DEBUG, INSTALL, CONFIGURE, CONNECT, AUTHENTICATE, AUTHORIZE, DENY, TRANSMIT, RECEIVE, UPLOAD, DOWNLOAD, EXPORT, IMPORT, PUBLISH, DEPLOY, RELEASE, MERGE, COMMIT, BRANCH, TAG, SIGN, VERIFY, APPROVE, REJECT, RECOMMEND, DECIDE, DELEGATE, CREATE_AGENT, CREATE_SUB_AGENT, CHANGE_MODEL, CHANGE_PROVIDER, CHANGE_TOOL, CHANGE_PERMISSION, CHANGE_POLICY, REVOKE, PAUSE, TERMINATE, ROLLBACK, DESTROY_RESOURCE, DESTROY_KEY, ACCESS_SECRET, USE_CREDENTIAL, CALL_API, WRITE_DATABASE, DELETE_DATABASE_RECORD, ALTER_DATABASE_SCHEMA, MODIFY_INFRASTRUCTURE, MODIFY_PRODUCTION, TRIGGER_EXTERNAL_EFFECT).

For each action class, the specification determines (in `RESOURCE_TRACE_PROTOCOL.md`): which actions require individual records; whether low-risk reads may be aggregated; which actions require human approval; which actions require dual approval; which actions require regulator-visible evidence; which actions must fail closed; which actions may operate in offline mode; and which actions require stronger runtime attestation.

## 8. Required Trace Structure

Every protected directory or equivalent resource scope contains or resolves to a trace manifest (`.aitrace/`):

```
.aitrace/
├── README.md
├── AUDIT.md
├── ledger.jsonl
├── registry_refs.json
├── policies.json
├── resource_manifest.json
├── verification.json
└── evidence/
```

Supported modes: embedded, sidecar, central organizational ledger, GitHub private evidence, public verification, federated registry, offline, independent archival.

## 9. Permanent Identity and Traceability

AI Actor Identifiers are permanently unique, never reassigned, never reused, and remain resolvable after termination, revocation, provider closure, model retirement, repository transfer, and organizational restructuring. Material events are append-only, cryptographically protected, sequence-aware, tamper-evident, independently verifiable, and survive agent termination, account deletion, provider withdrawal, Git history rewriting (via independent replication), and repository deletion. Corrections, revocations, disputes, and redactions are new signed events; legal access restrictions do not destroy the underlying integrity proof.

## 10. Quality Evidence

Every quality claim (tested, verified, secure, compliant, production-ready) resolves to evidence: test runs, builds, releases, attestations, audits, certifications. The completion language (Master Prompt §37) is normative: "tested" only after tests were executed; "verified" only after direct inspection and cross-checking; "implemented" only when functional code exists; "validated" only when a defined validation procedure was executed; "reproducible" only after a clean rerun; "publication-ready" only after all paper gates pass; "audit-ready" only after independent audit evidence exists; "complete" only when every required artifact and gate passes.

## 11. Registry Tiers

AI-IDP defines four registry tiers:

- **Public** — public provider identities, public model identities, public agent identities or classes, registry authorities, public verification keys, protocol versions, schema versions, revocation status, certification status, conformity status, signed ledger roots, Merkle roots, release attestations, public schemas, public specifications.
- **Controlled** — accessible to authorized regulators, auditors, and certification bodies.
- **Organization-private** — accessible to the controlling organization.
- **Sealed** — accessible only under judicial or regulator-controlled disclosure.

## 12. Conformance Levels

AI-IDP defines four conformance levels (L1–L4) in `CONFORMANCE_LEVELS.md`. L1 is the minimum baseline; L4 is the highest assurance. Small developers and open-source projects may target L1–L2; regulated sectors (finance, healthcare, public sector) target L3–L4.

## 13. Federation

AI-IDP supports federation between registry authorities (e.g., federal regulator, sectoral regulators, provincial regulators). The federation protocol is defined in `FEDERATION_PROTOCOL.md`. Federation preserves the invariants: a federated event is verifiable in any federated registry; a cross-jurisdiction delegation preserves the authority chain.

## 14. Offline Operation

AI-IDP supports offline operation: agents may operate without network connectivity, buffering events locally and reconciling with the canonical ledger when connectivity is restored. The offline protocol is defined in `OFFLINE_PROTOCOL.md`. Offline operation does not weaken the invariants; the buffer is itself an append-only, hash-chained local ledger that merges into the canonical ledger on reconciliation.

## 15. Disclosure

AI-IDP defines disclosure rules in `DISCLOSURE_PROTOCOL.md`: what may be disclosed publicly; what is controlled; what is organization-private; what is sealed; how sealed records are accessed under judicial or regulator authority; how redactions are authorized and recorded; how access is logged and audited.

## 16. Revocation, Correction, Incident

AI-IDP defines:

- `REVOCATION_PROTOCOL.md` — how identifiers, keys, agents, and authorizations are revoked.
- `CORRECTION_PROTOCOL.md` — how errors are corrected by appending new signed events (not by erasing history).
- `INCIDENT_PROTOCOL.md` — how incidents are reported, investigated, reconstructed, and resolved.
- `AUDIT_PROTOCOL.md` — how audits are performed, what evidence is required, and how audit reports are signed.
- `CERTIFICATION_PROTOCOL.md` — how conformity is certified, by whom, and with what evidence.

## 17. Versioning

AI-IDP follows semantic versioning. The versioning policy is defined in `VERSIONING_POLICY.md`. Schema versions, protocol versions, and specification versions are tracked independently. Backward-incompatible changes require a major version bump and a documented migration path.

## 18. Extension

AI-IDP may be extended for sectoral, provincial, or organizational needs. The extension policy is defined in `EXTENSION_POLICY.md`. Extensions must not weaken the invariants. Extensions are versioned and identified.

## 19. Relationship to Existing Standards

AI-IDP interoperates with: SPIFFE/SPIRE (workload identity), W3C PROV (provenance interchange), W3C DID and Verifiable Credentials (where applicable), in-toto (supply chain attestation), SLSA (supply chain levels), Sigstore/Rekor/Fulcio (transparency logs and signing), OpenTelemetry (observability), SPDX/CycloneDX (SBOM), ISO/IEC 27001/27017/27018/27701 (security and privacy), NIST SP 800-53/800-63/800-218 (security and SSDF). The standards crosswalk is in `research/synthesis/STANDARDS_CROSSWALK.md`.

## 20. Normative References

- Constitution Acts 1867 and 1982 (Canada)
- Personal Information Protection and Electronic Documents Act (PIPEDA), S.C. 2000, c. 5
- Privacy Act, R.S.C. 1985, c. P-21
- Treasury Board of Canada Secretariat, Directive on Automated Decision-Making
- Office of the Privacy Commissioner of Canada, guidance
- Canadian Centre for Cyber Security, guidance
- W3C PROV, DID Core, Verifiable Credentials
- IETF RFC 8032 (Ed25519)
- NIST FIPS 180-4 (SHA-2), FIPS 202 (SHA-3), IR 8413 (PQC status)
- ISO/IEC 27001, 27017, 27018, 27701

## 21. Informative References

See `paper/references.bib` for the full bibliography.

## 22. Conformance Statement

An implementation conforms to AI-IDP at level L{n} if it satisfies all invariants in Section 5, all required coverage in Section 6, all required action coverage in Section 7, all required trace structure in Section 8, all permanent identity and traceability requirements in Section 9, all quality evidence requirements in Section 10, and the conformance level requirements in `CONFORMANCE_LEVELS.md` for level L{n}.

Conformance is certified by an authorized certification body per `CERTIFICATION_PROTOCOL.md`. The AegisTrace reference implementation is a non-certified reference; certification requires a separate authorization process.
