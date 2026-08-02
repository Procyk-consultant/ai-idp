# Incident Reconstruction Example

Last Material Revision: 2026-08-01

## Scenario

An organization experiences an incident: an AI agent deleted a critical database record. The incident coordinator needs to reconstruct the timeline.

## Tools

The `aegistrace reconstruct` CLI produces the incident timeline.

## Procedure

1. Identify the incident scope: which agent, which task, which resource, which time range.
2. Run the reconstruct CLI:

```bash
aegistrace reconstruct \
  --ledger /var/aegistrace/ledger.jsonl \
  --agent aitrace://ca/agent/db-agent#v2.0 \
  --resource urn:db:customers:row:42 \
  --since 2026-08-01T10:00:00Z \
  --until 2026-08-01T12:00:00Z \
  --output incident-timeline.json
```

3. The CLI produces a JSON timeline with each matched event's:
   - Event ID
   - Timestamp
   - Action
   - Agent, instance, principal
   - Task
   - Resource
   - Before/after digests
   - Event hash

4. The coordinator reviews the timeline to identify:
   - Who authorized the deletion (principal).
   - Which agent performed the deletion (agent, instance).
   - Which model and provider were used (execution context).
   - Whether the authorization was valid (policy evaluation).
   - Whether approval was required and obtained (approval record).
   - The exact before/after state of the record (before/after digests).

5. The coordinator documents findings in the incident record.
6. The coordinator implements remediation (e.g., revoking the agent's authorization, restoring the deleted record from backup, updating the policy).
7. The coordinator closes the incident and notifies the regulator if high-severity.

## Output Example

```json
{
  "filter": {
    "agent": "aitrace://ca/agent/db-agent#v2.0",
    "resource": "urn:db:customers:row:42",
    "since": "2026-08-01T10:00:00Z",
    "until": "2026-08-01T12:00:00Z"
  },
  "matched_events": 3,
  "timeline": [
    {
      "seq": "evt_01JEXAMPLE001",
      "timestamp": "2026-08-01T10:15:00Z",
      "action": "READ",
      "agent": "aitrace://ca/agent/db-agent#v2.0",
      "principal": "aitrace://ca/principal/user-012",
      "task": "aitrace://ca/task/task-00104",
      "resource": "urn:db:customers:row:42",
      "before_digest": "sha256:aaa",
      "after_digest": "sha256:aaa",
      "event_hash": "sha256:..."
    },
    {
      "seq": "evt_01JEXAMPLE002",
      "timestamp": "2026-08-01T10:45:00Z",
      "action": "DELETE_DATABASE_RECORD",
      "agent": "aitrace://ca/agent/db-agent#v2.0",
      "principal": "aitrace://ca/principal/user-012",
      "task": "aitrace://ca/task/task-00104",
      "resource": "urn:db:customers:row:42",
      "before_digest": "sha256:aaa",
      "after_digest": null,
      "event_hash": "sha256:..."
    }
  ]
}
```

# Incident Reconstruction Example
