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
File: spec/TERMINOLOGY.md
Title: AI-IDP Terminology
Purpose: Define all technical and legal terms used in the AI-IDP standard
Audience: All readers
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: AI-IDP-CORE.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Terms are used consistently across all documents
Failure Behaviour: Term misuse is a defect
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# AI-IDP Terminology

This file defines the technical and legal terms used in the AI-IDP standard. Terms are used consistently across all documents. Deviations are defects.

## A

**Accountable controller.** The organization legally accountable for an agent's operation. The controller remains accountable regardless of provider, deployment, or model changes. Distinct from the principal (who grants authority for specific actions) and the provider (who supplies the model).

**Action.** A material operation performed by an agent. Actions are enumerated in Master Prompt §6 and are recorded as events in the ledger.

**Action ticket.** A sound engineering practices planning record containing the action's objective, requirements, affected files, dependencies, risks, legal/security/privacy effects, tests, acceptance criteria, and trace requirements.

**Agent.** See Persistent agent.

**Agent configuration.** A specific configuration of a persistent agent, including tool bindings, policy bindings, and execution environment parameters.

**Agent instance.** A specific execution of a persistent agent, identified by a unique runtime instance identifier tied to a specific execution context (provider, model, version, deployment, session).

**Agent version.** A versioned release of a persistent agent's definition.

**Append-only.** A property of the event ledger: events may be added but never modified or removed. Corrections and revocations are new signed events, not modifications.

**Approval.** A record that a specific human or service principal has approved a specific action. Approvals are single-use.

**Attestation.** A signed statement about a fact (e.g., build attestation, release attestation, key attestation).

**Audit.** An independent review of the ledger, registry, and evidence for conformance and integrity.

**Authorization.** A record that a principal has authorized a specific action or class of actions, subject to policy.

## B

**Before digest / after digest.** Cryptographic digests of a resource before and after a mutating action, recorded in the event for change detection and incident reconstruction.

**Branch.** A Git branch. Branch operations are recorded as events.

**Build.** A compiled or packaged artifact of a software project, with associated build evidence (provenance, inputs, environment).

## C

**Canonicalization.** A deterministic serialization of an event used for signature verification. Canonicalization is defined in `signing/canonical.py`.

**Certification.** A formal attestation by an accredited body that an implementation conforms to a specified AI-IDP conformance level.

**Child agent.** An agent created by delegation from a parent agent. Every child agent resolves to a parent delegation.

**Commit.** A Git commit. Commits are recorded as events with repository, branch, commit hash, and attestation references.

**Compliance profile.** A documented configuration of AI-IDP requirements for a specific context (e.g., federal public sector, open source, small developer).

**Conformance level.** A tier (L1–L4) of conformance to AI-IDP requirements, defined in `CONFORMANCE_LEVELS.md`.

**Controller.** See Accountable controller.

**Controlled tier.** A registry visibility tier accessible to authorized regulators, auditors, and certification bodies.

**Correction.** A new signed event that corrects an error in a prior event. Corrections append; they do not overwrite.

## D

**Delegation.** A record that a parent agent has delegated a bounded scope of authority to a child agent. Delegations are revocable and expirable.

**Deployment.** A specific deployment of a model or service, with associated endpoint, region, and operational metadata.

**Device.** A specific device on which an agent executes. Devices may be registered for forensics.

**Disclosure.** The act of making information available to a party. Disclosure rules are defined in `DISCLOSURE_PROTOCOL.md`.

**DID (Decentralized Identifier).** A W3C-standardized identifier format. AI-IDP references DIDs but does not require them.

## E

**Endpoint.** A specific network endpoint at which a model or service is invoked.

**Event.** A signed, hash-chained record of a material action, with full authority chain, execution context, before/after digests, and visibility tier.

**Execution context.** The provider, model, model version, and deployment in which an agent instance executes. Model or provider switches create new execution-context records, not new agent identities.

**Execution environment.** The environment in which an agent executes (e.g., container, VM, OS process, browser).

## F

**Federation.** The protocol by which multiple registry authorities interoperate, defined in `FEDERATION_PROTOCOL.md`.

**Forge / forgery.** An attempt to create a fraudulent event, identity, or signature. Forgery is detected by signature verification and hash chaining.

## G

**GitHub private evidence repository.** A private GitHub repository holding sensitive evidence (provider registrations, model registrations, agent definitions, action ledgers, encrypted evidence references).

**GitHub public verification repository.** A public GitHub repository holding only approved non-sensitive fields (public identities, registry authorities, public verification keys, protocol versions, schema versions, revocation status, certification status, signed ledger roots, Merkle roots, release attestations, public schemas, public specifications).

## H

**Hash chain.** A sequence of events where each event's hash includes the previous event's hash, providing tamper-evidence.

**Human principal.** A human who authorizes an agent's action. Distinct from the controller (who is accountable) and the user (on whose behalf the agent acts).

## I

**Identity issuer.** The operational component that mints identifiers under a registry authority.

**Incident.** An event or sequence of events requiring investigation and response. Incidents are recorded, investigated, reconstructed, and resolved per `INCIDENT_PROTOCOL.md`.

**Indigenous data sovereignty.** The principle that Indigenous peoples have authority over data about them, grounded in OCAP® principles, First Nations, Inuit, and Métis distinctions, and TRC Calls to Action.

## J

**Jurisdiction.** The legal authority under which AI-IDP operates. Primary jurisdiction: Canada. Sub-authority: provinces and territories.

## K

**Key.** A cryptographic key used for signing or encryption. Keys have lifecycles: creation, rotation, suspension, revocation, termination.

**Key service.** The component that manages key lifecycles.

## L

**Legal hold.** A hold placed on the deletion or modification of records relevant to a legal proceeding. Legal holds override retention schedules but do not destroy integrity proofs.

**Ledger.** The append-only, hash-chained record of events. The canonical ledger is the authoritative record.

**Liability.** Legal responsibility for harms. AI-IDP's liability allocation is analyzed in `government/CIVIL_LIABILITY_OPTIONS.md`.

## M

**Material action.** An action with potential legal, security, privacy, financial, or operational consequence. Material actions require individual event records; non-material reads may be aggregated.

**Merkle root.** A root hash of a Merkle tree constructed over a sequence of events, used for compact anchoring to public verification surfaces.

**Model.** A specific AI model (e.g., a specific LLM, vision model, embedding model). Models are execution components, not agents.

**Model artifact.** The weights, parameters, or other artifacts of a model version.

**Model family.** A family of related models (e.g., a model lineage).

**Model version.** A specific version of a model, with associated artifact, training provenance, and evaluation evidence.

## O

**OCAP®.** Ownership, Control, Access, and Possession — principles established by the First Nations Information Governance Centre for First Nations data governance.

**Offline mode.** An operational mode in which an agent operates without network connectivity, buffering events locally and reconciling with the canonical ledger when connectivity is restored.

**Orchestrator.** The system that coordinates agent execution, including task assignment, delegation, and instance lifecycle.

**Organization.** Any legal person or entity. Organizations may be providers, controllers, principals, or users (in the case of organizational agents).

**Organization-private tier.** A registry visibility tier accessible to the controlling organization.

## P

**Parent agent.** An agent that delegates to a child agent. Every child agent resolves to a parent delegation.

**Permanent identifier.** An identifier that is permanently unique, never reassigned, never reused, and remains resolvable after termination, revocation, provider closure, model retirement, repository transfer, and organizational restructuring.

**Persistent agent.** The identifiable logical software actor. A persistent agent has a permanent identifier that survives changes in provider, model, deployment, endpoint, tool, environment, session, and task.

**Policy.** A rule governing agent actions. Policies have versions and are recorded.

**Principal.** The human or service that grants authority for an action. Every action resolves to a principal.

**Privacy.** The right of individuals to control their personal information. AI-IDP's privacy analysis is in `government/PRIVACY_AND_HUMAN_RIGHTS_ANALYSIS.md`.

**Provider.** The organization that supplies or operates a model or service. Switching providers does not change agent identity.

**Provider service.** A specific service offering of a provider.

**Public tier.** A registry visibility tier accessible to any party. Contains only approved non-sensitive fields.

## Q

**Quality evidence.** Evidence (test runs, builds, releases, attestations, audits, certifications) supporting a quality claim. Every quality claim resolves to evidence.

## R

**Registry authority.** The body authorized to issue and maintain AI Actor identifiers.

**Repository.** A Git repository. Repository operations (branch, commit, merge, tag) are recorded as events.

**Resource.** Any file, directory, repository, database, API, service, system, or infrastructure resource affected by an agent action. Resources have manifests and digests.

**Revocation.** A new signed event that revokes a prior identifier, key, authorization, or agent. Revocation preserves historical records.

## S

**Sealed tier.** A registry visibility tier accessible only under judicial or regulator-controlled disclosure.

**Service principal.** A non-human principal (e.g., another service) that authorizes an agent's action.

**Session.** A specific session of agent execution. Sessions have identifiers and are recorded.

**Signature.** A cryptographic signature over an event's canonical serialization, using Ed25519 (RFC 8032) by default.

**Swarm.** A set of agents operating together, with delegation relationships among them.

## T

**Tamper-evidence.** A property of the ledger: any modification, deletion, or insertion of events is detectable by hash verification.

**Task.** A unit of work performed by an agent. Every action resolves to a task; every task resolves to an authority chain.

**Termination.** The end of an agent's lifecycle. Termination preserves historical records; the permanent identifier remains resolvable.

**Tool.** A specific tool used by an agent (e.g., a search tool, a code-execution tool, a database connector). Tool usage is recorded.

**Trace manifest.** A manifest (`.aitrace/`) associated with a protected directory or resource scope, containing the ledger, registry references, policies, resource manifest, verification data, and evidence.

## U

**User.** The end-user on whose behalf an agent acts. Users may be humans or services.

## V

**Verification.** The act of checking the integrity, authenticity, and conformance of an event, ledger, or artifact.

**Visibility tier.** One of public, controlled, organization-private, or sealed. Every event has a visibility tier.

## W

**Workload identity.** Identity for non-human workloads, as in SPIFFE/SPIRE. AI-IDP interoperates with workload identity standards.

## X, Y, Z

No terms.
