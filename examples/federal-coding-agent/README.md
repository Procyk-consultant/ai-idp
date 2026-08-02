# Federal Coding Agent Example

Last Material Revision: 2026-08-01

## Scenario

A federal department deploys an AI coding agent to assist software developers. The agent operates at conformance level L3.

## Participants

- **Controller:** Federal department (registered as `aitrace://ca/controller/federal-dept-001`)
- **Principal:** Individual developer (pseudonymous `aitrace://ca/principal/user-XXX`)
- **Agent:** Coding agent (`aitrace://ca/agent/coding-agent#v2.0`)
- **Agent instance:** Specific execution (`aitrace://ca/agent-instance/coding-agent#run-001`)
- **Provider:** AI provider (`aitrace://ca/provider/provider-001`)
- **Model:** AI model (`aitrace://ca/model/llm#v2.0`)
- **Deployment:** Federal deployment (`aitrace://ca/deployment/federal-dep-001`)

## Workflow

1. Developer (principal) authorizes the coding agent to modify a specific file.
2. Policy engine evaluates the request: action=MODIFY, scope=file:src/api/handlers.py.
3. Approval required for MODIFY; developer issues single-use approval.
4. Coding agent reads the file (READ event).
5. Coding agent generates the modification (GENERATE event).
6. Developer reviews the modification.
7. Coding agent writes the modification (MODIFY event with before/after digests).
8. Coding agent runs tests (TEST event with test results).
9. CI/CD pipeline builds and releases (BUILD, RELEASE events with attestations).
10. All events are recorded in the federal department's AegisTrace ledger.

## Quality Evidence

- Test coverage record
- Test results record (pass/fail per test)
- Code review record (reviewer, comments, approval)
- Static analysis record
- Build record (build provenance, SLSA level)
- Release attestation (Sigstore signature)

## Public Records

The federal department's public verification repository contains:
- Public agent identity: `aitrace://ca/agent/coding-agent#v2.0`
- Public model identity: `aitrace://ca/model/llm#v2.0`
- Public verification key for the coding agent
- Conformance certification: L3 (issued by accredited body)
- Signed ledger roots (Merkle anchors)
- Release attestations

## Private Records

The federal department's private evidence repository contains:
- Full action ledger
- Before/after digests for all modifications
- Code-review evidence
- Test evidence
- Build evidence

## Incident Procedure

If the coding agent generates defective code that reaches production:
1. The federal department opens an incident.
2. The reconstruct CLI produces the timeline of events leading to the defect.
3. The investigation identifies root cause.
4. The remediation revokes the affected release.
5. The regulator is notified (high-severity incident).
6. The affected public is notified if the defect caused harm.

# Federal Coding Agent Example
