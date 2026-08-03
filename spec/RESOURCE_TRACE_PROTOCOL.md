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
File: spec/RESOURCE_TRACE_PROTOCOL.md
Title: Resource Trace Protocol
Purpose: Define how resources are traced, manifest, and audited
Audience: Architects, implementers, auditors
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: EVENT_PROTOCOL.md; manifests/
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Every protected resource has a manifest
Failure Behaviour: Missing manifests are defects
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Resource Trace Protocol

## 1. Resource Manifest

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

## 2. Resource Manifest Fields

`resource_manifest.json` contains:

- `directory_id` — unique identifier for the directory or resource scope.
- `resource_owner` — the controller owning the directory.
- `first_ai_access` — timestamp of first AI access.
- `latest_ai_access` — timestamp of latest AI access.
- `agent_ids` — all agent IDs that have accessed the directory.
- `instance_ids` — all instance IDs that have accessed the directory.
- `controller_references` — controllers of those agents.
- `task_references` — tasks that operated on the directory.
- `action_summaries` — counts of each action type.
- `registry_references` — registry records for the directory and its resources.
- `policy_version` — current policy version.
- `current_state_digest` — SHA-256 digest of the directory's current state.
- `latest_ledger_sequence` — sequence number of the latest event in the ledger.
- `integrity_status` — `verified`, `unverified`, or `failed`.
- `legal_hold_status` — `none`, `held`, or `released`.
- `incident_status` — `none`, `open`, or `resolved`.
- `verification_procedure` — reference to the verification procedure used.

## 3. Supported Modes

1. **Embedded mode** — `.aitrace/` lives inside the protected directory.
2. **Sidecar mode** — `.aitrace/` lives in a sibling directory.
3. **Central organizational ledger mode** — `.aitrace/` is a reference into a central organizational ledger.
4. **GitHub private evidence mode** — `.aitrace/` references a private GitHub evidence repository.
5. **Public verification mode** — `.aitrace/` references a public verification repository (for public-tier events).
6. **Federated registry mode** — `.aitrace/` references a federated registry.
7. **Offline mode** — `.aitrace/` is a local buffer that reconciles with the canonical ledger when connectivity is restored.
8. **Independent archival mode** — `.aitrace/` references an independent archive.

## 4. Action Coverage

The protocol traces at least the actions enumerated in Master Prompt §6 (DISCOVER, ENUMERATE, OPEN, READ, SEARCH, QUERY, CREATE, GENERATE, MODIFY, REWRITE, PATCH, MOVE, RENAME, COPY, DELETE, RESTORE, EXECUTE, RUN, COMPILE, BUILD, TEST, DEBUG, INSTALL, CONFIGURE, CONNECT, AUTHENTICATE, AUTHORIZE, DENY, TRANSMIT, RECEIVE, UPLOAD, DOWNLOAD, EXPORT, IMPORT, PUBLISH, DEPLOY, RELEASE, MERGE, COMMIT, BRANCH, TAG, SIGN, VERIFY, APPROVE, REJECT, RECOMMEND, DECIDE, DELEGATE, CREATE_AGENT, CREATE_SUB_AGENT, CHANGE_MODEL, CHANGE_PROVIDER, CHANGE_TOOL, CHANGE_PERMISSION, CHANGE_POLICY, REVOKE, PAUSE, TERMINATE, ROLLBACK, DESTROY_RESOURCE, DESTROY_KEY, ACCESS_SECRET, USE_CREDENTIAL, CALL_API, WRITE_DATABASE, DELETE_DATABASE_RECORD, ALTER_DATABASE_SCHEMA, MODIFY_INFRASTRUCTURE, MODIFY_PRODUCTION, TRIGGER_EXTERNAL_EFFECT).

## 5. Action Classification

The protocol classifies actions:

- **Individual records required** — material actions (CREATE, MODIFY, DELETE, DEPLOY, etc.).
- **Aggregation permitted** — low-risk reads (DISCOVER, ENUMERATE, READ on public resources) may be aggregated into periodic summaries.
- **Human approval required** — high-impact actions (per AIA), production deployments, destructive actions, privilege changes.
- **Dual approval required** — production deployments of high-impact systems, privilege changes for high-privilege agents, cross-organization delegations involving critical infrastructure, destructive actions on sealed resources, cryptographic key destruction.
- **Regulator-visible evidence required** — incidents, revocations, certifications, high-impact automated decisions.
- **Fail-closed** — production deployments, destructive actions, privilege changes, cross-organization delegations, external effects, database schema changes, infrastructure modifications.
- **Offline mode permitted** — most read and write actions; reconciliation on reconnect.
- **Stronger runtime attestation required** — actions involving secrets, credentials, production infrastructure, sealed records.

## 6. Filesystem Watcher

A filesystem watcher monitors protected directories and generates events for filesystem changes (CREATE, MODIFY, MOVE, RENAME, COPY, DELETE, RESTORE). The watcher is implemented in `adapters/filesystem.py`.

## 7. Git Adapter

A Git adapter monitors Git repositories and generates events for Git operations (COMMIT, BRANCH, MERGE, TAG). The adapter is implemented in `adapters/git.py`.

## 8. Database Adapter

A database adapter monitors database operations (WRITE_DATABASE, DELETE_DATABASE_RECORD, ALTER_DATABASE_SCHEMA) and generates events. The adapter is implemented in `adapters/database.py`.

## 9. CI/CD Adapter

A CI/CD adapter monitors CI/CD operations (BUILD, TEST, RELEASE, DEPLOY) and generates events with build evidence, test evidence, and release attestations.

## 10. MCP Adapter

An MCP (Model Context Protocol) adapter monitors MCP operations (tool calls, resource accesses) and generates events.

## 11. Verification

Verification of a resource manifest:

1. The manifest exists.
2. The manifest's `current_state_digest` matches a recompute of the directory's state.
3. The manifest's `latest_ledger_sequence` matches the ledger's actual sequence.
4. The manifest's `integrity_status` is `verified`.
5. The manifest's `agent_ids`, `instance_ids`, `controller_references`, and `task_references` are consistent with the ledger.

Verification is performed by `aegistrace.cli.verify`.

## 12. Invariants

- Every protected resource has a manifest.
- Manifests are consistent with the ledger.
- Manifests are up-to-date (within a configurable freshness window).
- Manifest integrity is verifiable.
- Manifest changes are recorded as events.
