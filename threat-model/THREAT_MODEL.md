---
Organization: Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author: Pierre-Edward Procyk
Role: Founder / CEO
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
Contact: p.procyk.media@gmail.com
File: threat-model/THREAT_MODEL.md
Title: AegisTrace Threat Model
Purpose: Define the threat model, attack trees, abuse cases, and mitigations for AegisTrace
Audience: Security researchers, auditors, implementers
Document Classification: Public
Classification: documentation
Version: 2.1.0
Status: Submission-ready
Last Material Revision: 2026-09-07
Dependencies: spec/AI-IDP-CORE.md; spec/EVENT_PROTOCOL.md; src/aegistrace/
Source Basis: Master Execution Prompt; STRIDE/attack-tree methodology; NIST cybersecurity guidance
Invariants: Each threat has a documented mitigation and an automated test
Failure Behaviour: Unmitigated threats are escalated
Trace Policy: No AegisTrace event record required
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# AegisTrace Threat Model

## 1. Methodology

The threat model uses a combination of STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) and attack-tree methodology. Each threat is documented with: description, attack tree, abuse case, severity, likelihood, mitigation, and automated test. The model covers forgery, key compromise, registry tampering, replay, event tampering, hidden model substitution, adapter bypass, watcher bypass, unauthorized child agents, approval reuse, path traversal, command injection, secret leakage, Git history rewriting, registry tampering, malicious administrator erasure, malicious auditor, and denial of logging.

## 2. Threat Catalog

### T-001 — Forged Agent Event

**Description.** An attacker attempts to create a fraudulent event under another agent's identity by using a different signing key.

**Attack tree.** Attacker creates a new signing key; attacker attempts to record an event with `actor.agent_id = victim_agent_id` but `signing_key_id = attacker_key_id`.

**Mitigation.** The EventCollector checks that the signing key's `bound_entity_id` matches the `actor.agent_id` (or `actor.controller_id` for controller-level signing). Mismatches raise `PermissionError`.

**Test.** `tests/security/test_attacks.py::TestAttacks::test_forged_agent_event_rejected`.

### T-002 — Stolen Key After Revocation

**Description.** An attacker steals a signing key and attempts to use it after it has been revoked.

**Attack tree.** Attacker obtains the private key material; the legitimate controller discovers the compromise and revokes the key; attacker attempts to sign new events.

**Mitigation.** The KeyService's `is_active()` returns False for revoked keys. The EventCollector's `get_signing_key()` raises `PermissionError` for revoked keys.

**Test.** `tests/security/test_attacks.py::TestAttacks::test_stolen_key_cannot_sign_after_revoke`.

### T-003 — Event Modification

**Description.** An attacker modifies an event in the ledger (changes action, resource, or other field).

**Attack tree.** Attacker gains write access to the ledger file; attacker modifies a JSON line; attacker re-signs the event with the original key (if available) or a forged key.

**Mitigation.** Hash-chain verification detects any modification. Event-hash recomputation catches any field change. Signature verification catches any signed-content change.

**Test.** `tests/security/test_attacks.py::TestAttacks::test_event_modification_detected`, `test_chain_modification_detected`.

### T-004 — Event Deletion

**Description.** An attacker deletes an event from the ledger.

**Attack tree.** Attacker gains write access to the ledger file; attacker removes a JSON line.

**Mitigation.** Hash-chain verification detects deletion: the next event's `previous_event_hash` no longer matches.

**Test.** `tests/security/test_attacks.py::TestAttacks::test_event_deletion_detected`.

### T-005 — Event Reordering

**Description.** An attacker reorders events in the ledger.

**Mitigation.** Hash-chain verification detects reordering: each event's `previous_event_hash` must match the prior event's `event_hash`.

**Test.** `tests/security/test_attacks.py::TestAttacks::test_event_reordering_detected`.

### T-006 — Timestamp Manipulation

**Description.** An attacker modifies event timestamps to misrepresent the sequence of events.

**Mitigation.** Hash-chain verification detects any field modification, including timestamp. The signature covers the timestamp. Merkle anchoring provides independent time evidence.

**Test.** Covered by `test_event_modification_detected`.

### T-007 — Modified Digest

**Description.** An attacker modifies a resource's before/after digest to hide a change.

**Mitigation.** Hash-chain verification detects any field modification. The signature covers the digest fields. Resource manifests provide independent recomputation.

### T-008 — Hidden Model Substitution

**Description.** A provider silently substitutes a different model (e.g., a cheaper or weaker model) without a trace event.

**Mitigation.** Every model-execution span identifies provider, model, version, and deployment. Model switches create new execution-context records (events). The execution_context field in every event provides evidence of which model was used.

### T-009 — Adapter Bypass

**Description.** An agent performs an action through a non-instrumented adapter (e.g., direct filesystem access bypassing the FilesystemAdapter).

**Mitigation.** Mandatory event collection: agents that operate on protected resources must emit AegisTrace events. Watcher-based detection: filesystem watchers, Git adapters, and database adapters detect unauthorized operations. Periodic reconciliation detects gaps.

### T-010 — Watcher Bypass

**Description.** An attacker disables or evades the filesystem watcher.

**Mitigation.** Periodic reconciliation between the ledger and the resource manifest. Merkle anchoring provides external tamper-evidence. Independent replication provides survivability.

### T-011 — Unauthorized Child Agent

**Description.** A child agent attempts to act without a valid delegation from a parent agent.

**Mitigation.** The PolicyEngine verifies delegation before permitting actions. Delegation verification checks: delegation exists, delegation is active, delegation's scope encompasses the action, delegation has not expired.

**Test.** `tests/security/test_attacks.py::TestAttacks::test_unauthorized_child_agent_rejected`.

### T-012 — Approval Reuse

**Description.** An attacker attempts to reuse an approval for multiple actions.

**Mitigation.** Approvals are single-use. The PolicyEngine's `use_approval()` sets the `used` flag. Subsequent `evaluate()` calls with a used approval return deny.

**Test.** `tests/unit/test_authorization.py::TestPolicyEngine::test_approval_single_use`.

### T-013 — Path Traversal

**Description.** An attacker attempts to access files outside the protected directory using relative path manipulation (e.g., `../../etc/passwd`).

**Mitigation.** The FilesystemAdapter's `_resolve()` method resolves paths within `base_dir` and rejects attempts to escape. Path-traversal protection is enforced.

**Test.** Tested in `tests/integration/test_lifecycle.py::TestLifecycle::test_filesystem_adapter`.

### T-014 — Command Injection

**Description.** An attacker injects commands through agent input that reaches a shell or command-execution function.

**Mitigation.** Agents use parameterized APIs (e.g., `subprocess.run` with list arguments, not shell strings). Input validation. Sandboxing of agent execution environments.

### T-015 — Secret Leakage

**Description.** An attacker extracts secrets (signing keys, API tokens, credentials) from the ledger, registry, or memory.

**Mitigation.** The ledger never contains secrets. The registry never contains private keys. The KeyService's private material is held in memory only; production deployments use HSM or KMS. Sealed records are encrypted. Test events never contain real contact data.

**Test.** `tests/privacy/test_redaction.py::TestPrivacy::test_no_real_contact_data_in_events`.

### T-016 — Git History Rewriting

**Description.** An attacker rewrites Git history to hide evidence of changes.

**Mitigation.** Git operations are recorded as AegisTrace events with commit hashes. Merkle anchoring to a public verification surface provides tamper-evidence beyond the local Git repository. Independent archival replication provides survivability beyond the local repository.

### T-017 — Registry Tampering

**Description.** An attacker tampers with the registry to alter entity records, key bindings, or state.

**Mitigation.** Registry updates are signed events. Hash-chain verification detects tampering. Merkle anchoring provides external tamper-evidence. Independent replication provides survivability.

### T-018 — Malicious Administrator Erasure

**Description.** A privileged administrator attempts to erase evidence of misconduct.

**Mitigation.** The ledger is append-only: no event can be modified or deleted. Independent archival replication: the ledger is replicated to independent archives that the administrator cannot alter. Merkle anchoring: periodic Merkle roots are anchored to public verification surfaces. Sealed records: sensitive evidence is sealed and access-controlled.

### T-019 — Malicious Auditor

**Description.** An auditor with controlled-tier access attempts to misuse access.

**Mitigation.** All access to non-public records is logged and auditable. Access logs are themselves permanent records. Auditor accreditation requires independence from the audited entity. Auditor rotation.

### T-020 — Denial of Logging

**Description.** An attacker prevents an agent from logging events (e.g., by saturating the ledger, blocking network access, or crashing the collector).

**Mitigation.** Offline mode: agents buffer events locally and reconcile when connectivity is restored. Fail-closed operation: high-risk actions are denied if logging is unavailable. Incident reporting: denial-of-logging is treated as an incident.

### T-021 — Replay Attack

**Description.** An attacker replays a previously valid event to cause a duplicate effect.

**Mitigation.** Hash-chain sequencing: each event's `previous_event_hash` links it to the prior event. Event IDs are unique ULIDs. The ledger rejects duplicate event IDs. Approvals are single-use.

### T-022 — Cryptographic Obsolescence

**Description.** Ed25519 or SHA-256 becomes obsolete over the planning horizon (10+ years).

**Mitigation.** The signing interface is abstract; future migration to post-quantum schemes (CRYSTALS-Dilithium, SLH-DSA) is documented. The migration preserves original signatures; re-signing is recorded as new signed events. Long-term signature migration is documented in `spec/PERMANENT_RECORD_PROTOCOL.md`.

### T-023 — Privacy-vs-Permanence Legal Conflict

**Description.** Privacy law (PIPEDA, provincial statutes) requires erasure; permanence requires preservation.

**Mitigation.** Permanent minimal metadata (not full content). Permanent cryptographic commitments (not plaintext). Content separation. Sealed records. Access-controlled vaults. Append-only corrections (no erasure).

### T-024 — Indigenous Data Sovereignty Conflict

**Description.** AI-IDP's permanent records conflict with Indigenous data sovereignty (OCAP® principles, First Nations, Inuit, and Métis distinctions).

**Mitigation.** Indigenous data-governance provisions recognize Indigenous data sovereignty, community-controlled access for Indigenous community data, TRC Calls to Action alignment, and meaningful rights-holder engagement before deployments that materially affect Indigenous rights, community data, governance authority, or services. Unrelated implementations do not inherit a universal engagement gate.

## 3. Risk Assessment

| ID | Threat | Severity | Likelihood | Mitigation Status |
|----|--------|----------|------------|-------------------|
| T-001 | Forged agent event | High | Medium | Mitigated, tested |
| T-002 | Stolen key after revocation | High | Medium | Mitigated, tested |
| T-003 | Event modification | High | Medium | Mitigated, tested |
| T-004 | Event deletion | High | Medium | Mitigated, tested |
| T-005 | Event reordering | Medium | Medium | Mitigated, tested |
| T-006 | Timestamp manipulation | Medium | Medium | Mitigated, tested |
| T-007 | Modified digest | High | Low | Mitigated |
| T-008 | Hidden model substitution | High | Medium | Mitigated |
| T-009 | Adapter bypass | High | Medium | Mitigated |
| T-010 | Watcher bypass | Medium | Medium | Mitigated |
| T-011 | Unauthorized child agent | High | Medium | Mitigated, tested |
| T-012 | Approval reuse | High | Medium | Mitigated, tested |
| T-013 | Path traversal | High | Medium | Mitigated, tested |
| T-014 | Command injection | High | Medium | Mitigated |
| T-015 | Secret leakage | Critical | Low | Mitigated, tested |
| T-016 | Git history rewriting | High | Medium | Mitigated |
| T-017 | Registry tampering | High | Low | Mitigated |
| T-018 | Malicious administrator erasure | Critical | Medium | Mitigated |
| T-019 | Malicious auditor | High | Low | Mitigated |
| T-020 | Denial of logging | High | Medium | Mitigated |
| T-021 | Replay attack | Medium | Medium | Mitigated, tested |
| T-022 | Cryptographic obsolescence | Medium | Medium (long horizon) | Mitigated (interface-ready) |
| T-023 | Privacy-vs-permanence conflict | High | Medium | Mitigated |
| T-024 | Indigenous data sovereignty conflict | Medium | Medium | Mitigated; rights-holder engagement required where materially implicated |

## 4. Conclusion

The AegisTrace threat model covers 24 threats across forgery, key compromise, registry tampering, replay, event tampering, hidden model substitution, adapter bypass, watcher bypass, unauthorized child agents, approval reuse, path traversal, command injection, secret leakage, Git history rewriting, registry tampering, malicious administrator erasure, malicious auditor, denial of logging, cryptographic obsolescence, privacy-vs-permanence conflict, and Indigenous data sovereignty conflict. Each threat has a documented mitigation. Most threats have automated tests. The reference implementation passes all security tests. The threat model should be reviewed periodically and updated as new threats emerge.
