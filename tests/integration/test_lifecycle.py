"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/integration/test_lifecycle.py
Purpose: Integration tests for the complete AegisTrace lifecycle
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from aegistrace.adapters.filesystem import FilesystemAdapter
from aegistrace.adapters.github import GitHubEvidenceAdapter
from aegistrace.authorization.engine import PolicyEngine
from aegistrace.delegation.broker import DelegationBroker, DelegationScope
from aegistrace.events.collector import EventCollector
from aegistrace.events.models import Actor, ExecutionContext
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier


@pytest.fixture
def stack():
    ledger = AppendOnlyLedger()
    keys = KeyService()
    registry = Registry()
    collector = EventCollector(ledger, keys)
    policy = PolicyEngine(keys)
    delegations = DelegationBroker(keys)

    controller_id = str(make_identifier("controller", "org-001"))
    principal_id = str(make_identifier("principal", "user-012"))
    agent_id = str(make_identifier("agent", "research-agent", version="v3"))
    instance_id = str(make_identifier("agent-instance", "research-agent", version="run-0042"))
    provider_id = str(make_identifier("provider", "provider-001"))
    model_id = str(make_identifier("model", "example-llm"))
    model_version_id = str(make_identifier("model", "example-llm", version="v1.2"))
    deployment_id = str(make_identifier("deployment", "deployment-001"))

    for eid in [controller_id, principal_id, agent_id, instance_id, provider_id, model_id, model_version_id, deployment_id]:
        registry.register(eid, eid.split("/")[3].split("#")[0])

    ctrl_key_id = "aitrace://ca/key/ctrl-001"
    keys.create_key(ctrl_key_id, bound_entity_id=controller_id)
    agent_key_id = "aitrace://ca/key/agent-001"
    keys.create_key(agent_key_id, bound_entity_id=agent_id)

    actor = Actor(controller_id=controller_id, principal_id=principal_id, agent_id=agent_id, agent_instance_id=instance_id)
    ec = ExecutionContext(provider_id=provider_id, model_id=model_id, model_version_id=model_version_id, deployment_id=deployment_id)

    return {
        "ledger": ledger,
        "keys": keys,
        "registry": registry,
        "collector": collector,
        "policy": policy,
        "delegations": delegations,
        "actor": actor,
        "ec": ec,
        "ctrl_key_id": ctrl_key_id,
        "agent_key_id": agent_key_id,
        "controller_id": controller_id,
        "principal_id": principal_id,
        "agent_id": agent_id,
    }


class TestLifecycle:
    def test_complete_task_lifecycle(self, stack) -> None:
        """User authorizes agent; agent performs task; events are recorded and verified."""
        task_id = str(make_identifier("task", "t1"))
        auth = stack["policy"].issue_authorization(
            principal_id=stack["principal_id"],
            controller_id=stack["controller_id"],
            agent_id=stack["agent_id"],
            task_id=task_id,
            scope={"action_classes": ["SEARCH", "READ", "MODIFY"]},
            signing_key_id=stack["ctrl_key_id"],
        )
        ap = stack["policy"].issue_approval(
            action="MODIFY",
            approver_id=stack["principal_id"],
            authorization_id=auth.authorization_id,
            signing_key_id=stack["ctrl_key_id"],
        )
        for action in ["SEARCH", "READ"]:
            stack["collector"].record(
                actor=stack["actor"], execution_context=stack["ec"], task_id=task_id,
                action=action, visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                authorization_id=auth.authorization_id,
                resource_id=f"urn:example:{action}",
            )
        # MODIFY requires approval
        decision = stack["policy"].evaluate(
            action="MODIFY", authorization_id=auth.authorization_id, approval_id=ap.approval_id
        )
        assert decision.permitted
        stack["policy"].use_approval(ap.approval_id)
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=task_id,
            action="MODIFY", visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            authorization_id=auth.authorization_id,
            approval_id=ap.approval_id,
            resource_id="urn:file:report.md",
            before_digest="sha256:aaa",
            after_digest="sha256:bbb",
        )
        assert len(stack["ledger"]) == 3
        verifier = LedgerVerifier(stack["keys"])
        report = verifier.verify(stack["ledger"])
        assert report.ok, report.failures

    def test_parent_child_delegation(self, stack) -> None:
        """Parent agent delegates to child agent; child action is recorded."""
        child_agent_id = str(make_identifier("agent", "child"))
        stack["registry"].register(child_agent_id, "agent")
        child_key_id = "aitrace://ca/key/child-001"
        stack["keys"].create_key(child_key_id, bound_entity_id=child_agent_id)
        dlg = stack["delegations"].create(
            parent_agent_id=stack["agent_id"],
            parent_instance_id=stack["actor"].agent_instance_id,
            child_agent_id=child_agent_id,
            principal_id=stack["principal_id"],
            controller_id=stack["controller_id"],
            scope=DelegationScope(action_classes=["SEARCH"], delegation_depth=0),
            signing_key_id=stack["agent_key_id"],
        )
        # Record the delegation event
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t-delegate")),
            action="DELEGATE", visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id=dlg.delegation_id,
            delegation_id=dlg.delegation_id,
            authorization_id=str(make_identifier("authorization", "auth-parent")),
        )
        # Child performs action
        child_actor = Actor(
            controller_id=stack["controller_id"],
            principal_id=stack["principal_id"],
            agent_id=child_agent_id,
            agent_instance_id=str(make_identifier("agent-instance", "child", version="r1")),
        )
        stack["collector"].record(
            actor=child_actor, execution_context=stack["ec"], task_id=str(make_identifier("task", "t-child")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id=child_key_id,
            delegation_id=dlg.delegation_id,
            resource_id="urn:web:example",
            authorization_id=str(make_identifier("authorization", "auth-child")),
        )
        assert len(stack["ledger"]) == 2
        verifier = LedgerVerifier(stack["keys"])
        report = verifier.verify(stack["ledger"])
        assert report.ok

    def test_model_switch_preserves_agent_identity(self, stack) -> None:
        """Model switch creates new execution context but agent identity is unchanged."""
        # Initial event with model v2.0
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:1",
        )
        # Model switch to v2.0
        ec2 = ExecutionContext(
            provider_id=stack["ec"].provider_id,
            model_id=stack["ec"].model_id,
            model_version_id=str(make_identifier("model", "example-llm", version="v2.0")),
            deployment_id=stack["ec"].deployment_id,
        )
        stack["collector"].record(
            actor=stack["actor"], execution_context=ec2, task_id=str(make_identifier("task", "t2")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:2",
        )
        events = stack["ledger"].events()
        # Agent identity is unchanged
        assert events[0].actor.agent_id == events[1].actor.agent_id
        # Execution context model version differs
        assert events[0].execution_context.model_version_id != events[1].execution_context.model_version_id

    def test_provider_switch_preserves_agent_identity(self, stack) -> None:
        """Provider switch creates new execution context but agent identity is unchanged."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:1",
        )
        ec2 = ExecutionContext(
            provider_id=str(make_identifier("provider", "provider-002")),
            model_id=stack["ec"].model_id,
            model_version_id=stack["ec"].model_version_id,
            deployment_id=str(make_identifier("deployment", "dep-002")),
        )
        stack["collector"].record(
            actor=stack["actor"], execution_context=ec2, task_id=str(make_identifier("task", "t2")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:2",
        )
        events = stack["ledger"].events()
        assert events[0].actor.agent_id == events[1].actor.agent_id
        assert events[0].execution_context.provider_id != events[1].execution_context.provider_id

    def test_filesystem_adapter(self, tmp_path: Path, stack) -> None:
        """Filesystem operations produce before/after digests."""
        fa = FilesystemAdapter(tmp_path)
        path = Path("test.txt")
        result = fa.create(path, b"hello")
        assert result["after_digest"].startswith("sha256:")
        assert result["before_digest"] is None
        result2 = fa.modify(path, b"world")
        assert result2["before_digest"] != result2["after_digest"]

    def test_github_evidence_adapter(self, stack) -> None:
        """GitHub evidence adapter produces Merkle-root anchors."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:1",
        )
        # Get the public key for the GitHub adapter
        sk = stack["keys"].get_signing_key(stack["agent_key_id"])
        adapter = GitHubEvidenceAdapter(stack["agent_key_id"], sk.public_pem())
        anchor = adapter.make_merkle_root_anchor(stack["ledger"].events())
        assert anchor["schema"] == "aegistrace.merkle_root.v1"
        assert anchor["root"].startswith("sha256:")
        assert anchor["event_count"] == 1

    def test_ledger_persistence_and_reload(self, tmp_path: Path, stack) -> None:
        """Ledger can be saved to JSONL and reloaded."""
        for i in range(3):
            stack["collector"].record(
                actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", f"t{i}")),
                action="SEARCH", visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                resource_id=f"urn:web:{i}",
            )
        path = tmp_path / "ledger.jsonl"
        stack["ledger"].save(path)
        # Reload
        ledger2 = AppendOnlyLedger.load(path)
        assert len(ledger2) == 3
        # Verify reloaded ledger
        verifier = LedgerVerifier(stack["keys"])
        report = verifier.verify(ledger2)
        assert report.ok

    def test_cli_verify(self, tmp_path: Path, stack) -> None:
        """verify CLI works end-to-end."""
        from aegistrace.cli.verify import main as verify_main
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:1",
        )
        path = tmp_path / "ledger.jsonl"
        stack["ledger"].save(path)
        rc = verify_main(["--ledger", str(path)])
        assert rc == 0

    def test_cli_audit(self, tmp_path: Path, stack) -> None:
        """audit CLI produces a summary."""
        from aegistrace.cli.audit import main as audit_main
        for action in ["SEARCH", "READ", "SEARCH"]:
            stack["collector"].record(
                actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
                action=action, visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                resource_id="urn:web:1",
            )
        path = tmp_path / "ledger.jsonl"
        stack["ledger"].save(path)
        out = tmp_path / "audit.json"
        rc = audit_main(["--ledger", str(path), "--output", str(out)])
        assert rc == 0
        report = json.loads(out.read_text())
        assert report["event_count"] == 3
        assert report["actions"]["SEARCH"] == 2
        assert report["actions"]["READ"] == 1
