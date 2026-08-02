# AegisTrace Developer Guide

Last Material Revision: 2026-08-01

## Architecture Overview

AegisTrace has six layers: identity, ledger, governance, event, adapter, and storage. See `technical/AEGISTRACE_TECHNICAL_ARCHITECTURE.md` for the full architecture.

## Registering an Agent

```python
from aegistrace import Registry, KeyService, make_identifier

registry = Registry()
keys = KeyService()

controller_id = str(make_identifier("controller", "org-001"))
agent_id = str(make_identifier("agent", "my-agent", version="v1"))
registry.register(controller_id, "controller")
registry.register(agent_id, "agent")

key_id = "aitrace://ca/key/key-001"
keys.create_key(key_id, bound_entity_id=agent_id)
```

## Recording an Event

```python
from aegistrace import AppendOnlyLedger, EventCollector, Actor, ExecutionContext

ledger = AppendOnlyLedger()
collector = EventCollector(ledger, keys)

actor = Actor(
    controller_id=controller_id,
    principal_id=str(make_identifier("principal", "user-001")),
    agent_id=agent_id,
    agent_instance_id=str(make_identifier("agent-instance", "my-agent", version="run-1")),
)
ec = ExecutionContext(
    provider_id=str(make_identifier("provider", "prov-001")),
    model_id=str(make_identifier("model", "llm-001")),
    model_version_id=str(make_identifier("model", "llm-001", version="v1.0")),
    deployment_id=str(make_identifier("deployment", "dep-001")),
)

event = collector.record(
    actor=actor,
    execution_context=ec,
    task_id=str(make_identifier("task", "task-001")),
    action="SEARCH",
    visibility="ORGANIZATION_PRIVATE",
    signing_key_id=key_id,
    resource_id="urn:web:example.com",
)
```

## Verifying a Ledger

```python
from aegistrace import LedgerVerifier

verifier = LedgerVerifier(keys)
report = verifier.verify(ledger)
print(report)
```

## Using the Filesystem Adapter

```python
from aegistrace import FilesystemAdapter
from pathlib import Path

fa = FilesystemAdapter(Path("/tmp/my-project"))
result = fa.create(Path("test.txt"), b"hello")
# result = {"resource_id": ..., "before_digest": None, "after_digest": "sha256:..."}

# Record an event for the filesystem operation
collector.record(
    actor=actor, execution_context=ec, task_id=str(make_identifier("task", "task-002")),
    action="CREATE", visibility="ORGANIZATION_PRIVATE",
    signing_key_id=key_id,
    resource_id=result["resource_id"],
    after_digest=result["after_digest"],
)
```

## Using the Git Adapter

```python
from aegistrace import GitAdapter

git = GitAdapter(Path("/tmp/my-repo"))
git.add(["README.md"])
commit_hash = git.commit("Initial commit")
```

## Using the GitHub Evidence Adapter

```python
from aegistrace import GitHubEvidenceAdapter

sk = keys.get_signing_key(key_id)
adapter = GitHubEvidenceAdapter(key_id, sk.public_pem())
anchor = adapter.make_merkle_root_anchor(ledger.events())
print(anchor)
```

## Using the Policy Engine

```python
from aegistrace import PolicyEngine

policy = PolicyEngine(keys)
auth = policy.issue_authorization(
    principal_id=actor.principal_id,
    controller_id=controller_id,
    agent_id=agent_id,
    task_id=str(make_identifier("task", "task-003")),
    scope={"action_classes": ["SEARCH", "READ"]},
    signing_key_id=key_id,
)
decision = policy.evaluate(action="SEARCH", authorization_id=auth.authorization_id)
print(decision)
```

## Using the Delegation Broker

```python
from aegistrace import DelegationBroker, DelegationScope

broker = DelegationBroker(keys)
dlg = broker.create(
    parent_agent_id=agent_id,
    parent_instance_id=actor.agent_instance_id,
    child_agent_id=str(make_identifier("agent", "child-agent")),
    principal_id=actor.principal_id,
    controller_id=controller_id,
    scope=DelegationScope(action_classes=["SEARCH"], delegation_depth=0),
    signing_key_id=key_id,
)
```

## Persistence

```python
from pathlib import Path
ledger.save(Path("ledger.jsonl"))
# Later:
# from aegistrace import AppendOnlyLedger
# ledger2 = AppendOnlyLedger.load(Path("ledger.jsonl"))
```

## SQLite Storage

```python
from aegistrace import SQLiteStorage

storage = SQLiteStorage(Path("aegistrace.db"))
storage.append_event(seq=0, event=event.to_dict())
retrieved = storage.get_event(event.event_id)
```

# AegisTrace Developer Guide
