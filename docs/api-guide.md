# AegisTrace API Guide

Last Material Revision: 2026-09-07

## Base URL

```
http://127.0.0.1:8000/
```

## Endpoints

### GET /health

Returns `{"status": "ok", "version": "2.1.0"}`.

### GET /actions

Returns the list of canonical actions.

### GET /visibilities

Returns the list of visibility tiers.

### POST /events

Records a new event.

Request body:
```json
{
  "controller_id": "aitrace://ca/controller/org-001",
  "principal_id": "aitrace://ca/principal/user-012",
  "agent_id": "aitrace://ca/agent/research-agent#v3",
  "agent_instance_id": "aitrace://ca/agent-instance/research-agent#run-0042",
  "provider_id": "aitrace://ca/provider/provider-001",
  "model_id": "aitrace://ca/model/example-llm",
  "model_version_id": "aitrace://ca/model/example-llm#v1.2",
  "deployment_id": "aitrace://ca/deployment/deployment-001",
  "task_id": "aitrace://ca/task/task-00104",
  "action": "SEARCH",
  "visibility": "ORGANIZATION_PRIVATE",
  "signing_key_id": "aitrace://ca/key/key-001",
  "resource_id": "urn:web:example.com"
}
```

Returns the recorded event.

### GET /events

Returns all events in the ledger.

### GET /events/{event_id}

Returns a specific event.

### POST /verify

Verifies the ledger. Returns `{"ok": true, "failures": [], "failing_event_ids": []}` on success.

### GET /registry/{entity_id}

Resolves an entity. Returns the entity's identifier, type, state, attributes, and creation timestamp.

## Authentication

The reference implementation does not require authentication. Production deployments should add authentication (e.g., OAuth 2.0, mTLS).

## Rate Limiting

The reference implementation does not rate-limit. Production deployments should rate-limit.

## SDK

A Python SDK is available: `import aegistrace`. See `docs/developer-guide.md` for usage.

# AegisTrace API Guide
