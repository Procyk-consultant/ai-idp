"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/cli/admin.py
Purpose: admin CLI - administrative operations + demo scenario
Classification: application
Version: 2.0.0
Last Material Revision: 2026-08-16
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
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier
from aegistrace.ledger.merkle import merkle_root


def run_demo(out_dir: Path) -> int:
    """Run a complete AegisTrace demo scenario."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger = AppendOnlyLedger()
    keys = KeyService()
    registry = Registry()
    collector = EventCollector(ledger, keys)
    policy = PolicyEngine(keys)
    delegations = DelegationBroker(keys)

    controller_id = str(make_identifier("controller", "org-001"))
    principal_id = str(make_identifier("principal", "user-012"))
    agent_id = str(make_identifier("agent", "research-agent", version="v3"))
    agent_instance_id = str(make_identifier("agent-instance", "research-agent", version="run-0042"))
    provider_id = str(make_identifier("provider", "provider-001"))
    model_id = str(make_identifier("model", "example-llm"))
    model_version_id = str(make_identifier("model", "example-llm", version="v1.2"))
    deployment_id = str(make_identifier("deployment", "deployment-001"))
    task_id = str(make_identifier("task", "task-00104"))

    for eid in [controller_id, principal_id, agent_id, agent_instance_id, provider_id, model_id, model_version_id, deployment_id, task_id]:
        etype = eid.split("/")[3].split("#")[0]
        registry.register(eid, etype)

    ctrl_key_id = str(make_identifier("key", "key-ctrl-001"))
    keys.create_key(ctrl_key_id, bound_entity_id=controller_id)

    agent_key_id = str(make_identifier("key", "key-agent-001"))
    keys.create_key(agent_key_id, bound_entity_id=agent_id)

    auth = policy.issue_authorization(
        principal_id=principal_id,
        controller_id=controller_id,
        agent_id=agent_id,
        task_id=task_id,
        scope={"action_classes": ["SEARCH", "READ", "QUERY", "MODIFY", "CREATE", "DELEGATE"]},
        signing_key_id=ctrl_key_id,
    )

    # The demo records a human approval for MODIFY as evidence even though the
    # default policy does not classify every MODIFY action as approval-required.
    ap = policy.issue_approval(
        action="MODIFY",
        approver_id=principal_id,
        authorization_id=auth.authorization_id,
        signing_key_id=ctrl_key_id,
    )

    child_agent_id = str(make_identifier("agent", "literature-search-agent", version="v1"))
    registry.register(child_agent_id, "agent")
    dlg = delegations.create(
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

    decision = policy.evaluate(action="MODIFY", authorization_id=auth.authorization_id, approval_id=ap.approval_id)
    assert decision.permitted, f"decision should be permitted, got: {decision.reason}"
    policy.use_approval(ap.approval_id)

    actor = Actor(controller_id=controller_id, principal_id=principal_id, agent_id=agent_id, agent_instance_id=agent_instance_id)
    ec = ExecutionContext(provider_id=provider_id, model_id=model_id, model_version_id=model_version_id, deployment_id=deployment_id)

    e1 = collector.record(
        actor=actor, execution_context=ec, task_id=task_id,
        action="SEARCH", visibility="ORGANIZATION_PRIVATE", signing_key_id=agent_key_id,
        resource_id="urn:web:arxiv:2401.00001",
        authorization_id=auth.authorization_id,
    )
    e2 = collector.record(
        actor=actor, execution_context=ec, task_id=task_id,
        action="READ", visibility="ORGANIZATION_PRIVATE", signing_key_id=agent_key_id,
        resource_id="urn:web:arxiv:2401.00001",
        authorization_id=auth.authorization_id,
    )
    e3 = collector.record(
        actor=actor, execution_context=ec, task_id=task_id,
        action="MODIFY", visibility="ORGANIZATION_PRIVATE", signing_key_id=agent_key_id,
        resource_id="urn:file:report.md",
        before_digest="sha256:aaa",
        after_digest="sha256:bbb",
        authorization_id=auth.authorization_id,
        approval_id=ap.approval_id,
    )
    e4 = collector.record(
        actor=actor, execution_context=ec, task_id=task_id,
        action="DELEGATE", visibility="ORGANIZATION_PRIVATE", signing_key_id=agent_key_id,
        resource_id=dlg.delegation_id,
        delegation_id=dlg.delegation_id,
        authorization_id=auth.authorization_id,
    )
    assert {e1.action, e2.action, e3.action, e4.action} == {"SEARCH", "READ", "MODIFY", "DELEGATE"}

    verifier = LedgerVerifier(keys)
    report = verifier.verify(ledger)
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
        "event_ids": [e.event_id for e in ledger],
        "merkle_root": root,
        "verification": "OK",
        "verified_signatures": report.verified_signature_count,
        "ledger_path": str(ledger_path),
        "public_keys_path": str(keys_path),
        "controller_key_id": ctrl_key_id,
        "agent_key_id": agent_key_id,
        "authorization_id": auth.authorization_id,
        "approval_id": ap.approval_id,
        "delegation_id": dlg.delegation_id,
    }
    (out_dir / "demo_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="aegistrace.admin", description="AegisTrace administrative CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    demo = sub.add_parser("demo", help="Run the demo scenario")
    demo.add_argument("--out", default=".aitrace-demo", help="Output directory")

    args = parser.parse_args(argv)
    if args.cmd == "demo":
        return run_demo(Path(args.out))
    return 2


if __name__ == "__main__":
    sys.exit(main())
