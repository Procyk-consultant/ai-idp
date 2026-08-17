"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/cli/admin.py
Purpose: admin CLI - administrative operations + governed demo scenario
Classification: application
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from aegistrace.authorization.engine import PolicyEngine
from aegistrace.delegation.broker import DelegationBroker, DelegationScope
from aegistrace.events.collector import EventCollector
from aegistrace.events.models import Actor, ExecutionContext
from aegistrace.governance.service import GovernedEventService
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier
from aegistrace.ledger.merkle import merkle_root


def run_demo(out_dir: Path) -> int:
    """Run a governed AegisTrace scenario and persist verification evidence."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger = AppendOnlyLedger()
    keys = KeyService()
    registry = Registry()
    collector = EventCollector(ledger, keys)
    policy = PolicyEngine(keys)
    delegations = DelegationBroker(keys)
    governed = GovernedEventService(
        collector=collector,
        policy_engine=policy,
        delegation_broker=delegations,
        registry=registry,
    )

    controller_id = str(make_identifier("controller", "org-001"))
    principal_id = str(make_identifier("principal", "user-012"))
    agent_id = str(make_identifier("agent", "research-agent", version="v3"))
    agent_instance_id = str(make_identifier("agent-instance", "research-agent", version="run-0042"))
    provider_id = str(make_identifier("provider", "provider-001"))
    model_id = str(make_identifier("model", "example-llm"))
    model_version_id = str(make_identifier("model", "example-llm", version="v1.2"))
    deployment_id = str(make_identifier("deployment", "deployment-001"))
    task_id = str(make_identifier("task", "task-00104"))

    registry.register(controller_id, "controller")
    registry.register(principal_id, "principal")
    registry.register(agent_id, "agent", {"controller_id": controller_id})
    registry.register(agent_instance_id, "agent-instance", {"agent_id": agent_id})
    registry.register(provider_id, "provider")
    registry.register(model_id, "model")
    registry.register(model_version_id, "model")
    registry.register(deployment_id, "deployment")
    registry.register(task_id, "task")

    controller_key_id = str(make_identifier("key", "key-ctrl-001"))
    keys.create_key(controller_key_id, bound_entity_id=controller_id)
    agent_key_id = str(make_identifier("key", "key-agent-001"))
    keys.create_key(agent_key_id, bound_entity_id=agent_id)

    authorization = policy.issue_authorization(
        principal_id=principal_id,
        controller_id=controller_id,
        agent_id=agent_id,
        task_id=task_id,
        scope={"action_classes": ["SEARCH", "READ", "PUBLISH", "DELEGATE"]},
        signing_key_id=controller_key_id,
    )
    publish_approval = policy.issue_approval(
        action="PUBLISH",
        approver_id=principal_id,
        authorization_id=authorization.authorization_id,
        signing_key_id=controller_key_id,
    )

    child_agent_id = str(make_identifier("agent", "literature-search-agent", version="v1"))
    registry.register(child_agent_id, "agent", {"controller_id": controller_id})
    delegation = delegations.create(
        parent_agent_id=agent_id,
        parent_instance_id=agent_instance_id,
        child_agent_id=child_agent_id,
        principal_id=principal_id,
        controller_id=controller_id,
        scope=DelegationScope(
            task_classes=["literature-search"],
            action_classes=["SEARCH", "READ"],
            delegation_depth=0,
        ),
        signing_key_id=agent_key_id,
    )
    registry.update(child_agent_id, {"parent_delegation_id": delegation.delegation_id})

    actor = Actor(
        controller_id=controller_id,
        principal_id=principal_id,
        agent_id=agent_id,
        agent_instance_id=agent_instance_id,
    )
    execution_context = ExecutionContext(
        provider_id=provider_id,
        model_id=model_id,
        model_version_id=model_version_id,
        deployment_id=deployment_id,
    )

    event_1 = governed.record(
        actor=actor,
        execution_context=execution_context,
        task_id=task_id,
        action="SEARCH",
        visibility="ORGANIZATION_PRIVATE",
        signing_key_id=agent_key_id,
        authorization_id=authorization.authorization_id,
        resource_id="urn:web:arxiv:2401.00001",
    )
    event_2 = governed.record(
        actor=actor,
        execution_context=execution_context,
        task_id=task_id,
        action="READ",
        visibility="ORGANIZATION_PRIVATE",
        signing_key_id=agent_key_id,
        authorization_id=authorization.authorization_id,
        resource_id="urn:web:arxiv:2401.00001",
    )
    event_3 = governed.record(
        actor=actor,
        execution_context=execution_context,
        task_id=task_id,
        action="PUBLISH",
        visibility="ORGANIZATION_PRIVATE",
        signing_key_id=agent_key_id,
        authorization_id=authorization.authorization_id,
        approval_id=publish_approval.approval_id,
        resource_id="urn:artifact:research-summary",
    )
    event_4 = governed.record(
        actor=actor,
        execution_context=execution_context,
        task_id=task_id,
        action="DELEGATE",
        visibility="ORGANIZATION_PRIVATE",
        signing_key_id=agent_key_id,
        authorization_id=authorization.authorization_id,
        resource_id=delegation.delegation_id,
    )
    assert {event_1.action, event_2.action, event_3.action, event_4.action} == {
        "SEARCH",
        "READ",
        "PUBLISH",
        "DELEGATE",
    }
    assert all(event.governance_mode == "GOVERNED" for event in ledger.events())
    assert policy.get_approval(publish_approval.approval_id).used is True  # type: ignore[union-attr]

    report = LedgerVerifier(keys).verify(ledger)
    assert report.ok, f"verification failed: {report.failures}"
    root = merkle_root(ledger.events())

    ledger_path = out_dir / "ledger.jsonl"
    keys_path = out_dir / "public_keys.json"
    ledger.save(ledger_path)
    keys_path.write_text(
        json.dumps(keys.export_public_registry(), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    summary = {
        "events": len(ledger),
        "event_ids": [event.event_id for event in ledger],
        "governance_mode": "GOVERNED",
        "merkle_root": root,
        "verification": "OK",
        "verified_signatures": report.verified_signature_count,
        "ledger_path": str(ledger_path),
        "public_keys_path": str(keys_path),
        "controller_key_id": controller_key_id,
        "agent_key_id": agent_key_id,
        "authorization_id": authorization.authorization_id,
        "approval_id": publish_approval.approval_id,
        "delegation_id": delegation.delegation_id,
    }
    (out_dir / "demo_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aegistrace.admin", description="AegisTrace administrative CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo", help="Run the governed demo scenario")
    demo.add_argument("--out", default=".aitrace-demo", help="Output directory")

    args = parser.parse_args(argv)
    if args.cmd == "demo":
        return run_demo(Path(args.out))
    return 2


if __name__ == "__main__":
    sys.exit(main())
