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
File: spec/INCIDENT_PROTOCOL.md
Title: Incident Protocol
Purpose: Define how incidents are reported, investigated, reconstructed, and resolved
Audience: Architects, security officers, regulators
Document Classification: Public
Classification: documentation
Version: 2.0.0
Status: Submission-ready
Last Material Revision: 2026-08-01
Dependencies: EVENT_PROTOCOL.md; AUDIT_PROTOCOL.md
Source Basis: Master Execution Prompt; Canadian public-record legal materials; international technical standards
Invariants: Incidents are recorded, investigated, and resolved
Failure Behaviour: Silent incident suppression is forbidden
Trace Policy: This specification defines the trace policy
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk
---

# Incident Protocol

## 1. Incident Definition

An incident is an event or sequence of events requiring investigation and response. Incidents include:

- Security incidents (forgery, key compromise, registry tampering, unauthorized access).
- Privacy incidents (unauthorized disclosure, sealed-record leakage, correlation attacks).
- Operational incidents (agent malfunction, runaway actions, resource exhaustion).
- Accountability incidents (false attribution, missing authorization, missing approval).
- Compliance incidents (conformance failure, missing evidence, audit failure).

## 2. Incident Record

An incident record contains:

- `incident_id` — unique identifier.
- `incident_type` — security, privacy, operational, accountability, compliance.
- `severity` — low, medium, high, critical.
- `status` — open, investigating, resolved, closed.
- `reported_at` — reporting timestamp.
- `reported_by` — reporting principal.
- `affected_events` — list of affected event identifiers.
- `affected_agents` — list of affected agent identifiers.
- `affected_resources` — list of affected resource identifiers.
- `affected_persons` — list of affected persons (pseudonymous; sealed if sensitive).
- `investigation_log` — investigation steps and findings.
- `resolution` — resolution summary.
- `closed_at` — closure timestamp.
- `signature` — cryptographic signature by the incident coordinator.

## 3. Reporting

Incidents are reported by:

- The agent that detected the incident.
- The controller.
- A regulator.
- An affected person (via the recourse mechanism).
- An auditor.

Reports are submitted to the incident coordinator. Reports are recorded as incident-report events.

## 4. Investigation

Investigation:

1. The incident coordinator opens an investigation.
2. The coordinator collects evidence from the ledger, registry, and evidence store.
3. The coordinator reconstructs the incident timeline.
4. The coordinator identifies root cause.
5. The coordinator documents findings in the investigation log.
6. The coordinator recommends remediation.

## 5. Reconstruction

Incident reconstruction uses the `aegistrace.cli.reconstruct` CLI. Reconstruction:

1. Loads the ledger.
2. Filters events by the incident's scope (time, agents, resources, tasks).
3. Reconstructs the timeline.
4. Identifies the authority chain for each event.
5. Identifies the execution context for each event.
6. Identifies the resource state changes (before/after digests).
7. Produces a reconstruction report.

## 6. Resolution

Resolution:

1. The coordinator implements remediation (e.g., revoking keys, suspending agents, correcting records).
2. The coordinator verifies that the remediation is effective.
3. The coordinator closes the incident.
4. The closure is recorded as an incident-closure event.

## 7. Regulator Notification

High-severity and critical incidents are reported to the regulator. The notification includes:

- The incident record.
- The investigation log.
- The resolution.
- The remediation evidence.

## 8. Affected-Person Notification

Affected persons are notified of incidents affecting their personal information. Notification includes:

- The nature of the incident.
- The data affected.
- The remediation.
- The recourse mechanism.

## 9. Invariants

- Incidents are recorded.
- Incidents are investigated.
- Incidents are resolved.
- Regulator notification is performed for high-severity and critical incidents.
- Affected-person notification is performed for privacy incidents.
- Silent incident suppression is forbidden.
