"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/integration/test_lifecycle.py
Purpose: Integration tests for the AegisTrace evidence lifecycle
Version: 2.0.0
Last Material Revision: 2026-08-17
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

    for entity_id in [
        controller_id,
        principal_id,
        agent_id,
        instance_id,
        provider_id,
        model_id,
        model_version_id,
        deployment_id,
    ]:
        registry.register(entity_id, entity_id.split("/")[3].split("#")[0])

    controller_key_id = "aitrace://ca/key/ctrl-001"
    keys.create_key(controller_key_id, bound_entity_id=controller_id)
    principal_key_id = "aitrace://ca/key/principal-001"
    keys.create_key(principal_key_id, bound_entity_id=principal_id)
    agent_key_id = "aitrace://ca/key/agent-001"
    keys.create_key(agent_key_id, bound_entity_id=agent_id)

    actor = Actor(
        controller_id=controller_id,
        principal_id=principal_id,
        agent_id=agent_id,
        agent_instance_id=instance_id,
    )
    execution_context = ExecutionContext(
        provider_id=provider_id,
        model_id=model_id,
        model_version_id=model_version_id,
        deployment_id=deployment_id,
    )

    return {
        "ledger": ledger,
        "keys": keys,
        "registry": registry,
        "collector": collector,
        "policy": policy,
        "delegations": delegations,
        "actor": actor,
        "ec": execution_context,
        "ctrl_key_id": controller_key_id,
        "principal_key_id": principal_key_id,
        "agent_key_id": agent_key_id,
        "controller_id": controller_id,
        "principal_id": principal_id,
        "agent_id": agent_id,
    }


class TestLifecycle:
    def test_complete_task_lifecycle(self, stack) -> None:
        """Authorization, approval, evidence recording, and verification compose correctly."""
        task_id = str(make_identifier("task", "t1"))
        authorization = stack["policy"].issue_authorization(
            principal_id=stack["principal_id"],
            controller_id=stack["controller_id"],
            agent_id=stack["agent_id"],
            task_id=task_id,
            scope={"action_classes": ["SEARCH", "READ", "PUBLISH"]},
            signing_key_id=stack["ctrl_key_id"],
        )
        approval = stack["policy"].issue_approval(
            action="PUBLISH",
            approver_id=stack["principal_id"],
            authorization_id=authorization.authorization_id,
            signing_key_id=stack["principal_key_id"],
        )

        for action in ["SEARCH", "READ"]:
            decision = stack["policy"].evaluate(
                action=action,
                authorization_id=authorization.authorization_id,
            )
            assert decision.permitted
            stack["collector"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=task_id,
                action=action,
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                authorization_id=authorization.authorization_id,
                resource_id=f"urn:example:{action}",
            )

        publish_decision = stack["policy"].evaluate(
            action="PUBLISH",
            authorization_id=authorization.authorization_id,
            approval_id=approval.approval_id,
        )
        assert publish_decision.permitted
        assert stack["policy"].consume_approvals(publish_decision.satisfied_approval_ids)
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=task_id,
            action="PUBLISH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            authorization_id=authorization.authorization_id,
            approval_id=approval.approval_id,
            resource_id="urn:artifact:report",
            before_digest="sha256:" + "a" * 64,
            after_digest="sha256:" + "b" * 64,
        )

        assert len(stack["ledger"]) == 3
        report = LedgerVerifier(stack["keys"]).verify(stack["ledger"])
        assert report.ok, report.failures

    def test_parent_child_delegation(self, stack) -> None:
        """Delegation evidence and child evidence remain cryptographically verifiable."""
        child_agent_id = str(make_identifier("agent", "child"))
        stack["registry"].register(child_agent_id, "agent")
        child_key_id = "aitrace://ca/key/child-001"
        stack["keys"].create_key(child_key_id, bound_entity_id=child_agent_id)
        delegation = stack["delegations"].create(
            parent_agent_id=stack["agent_id"],
            parent_instance_id=stack["actor"].agent_instance_id,
            child_agent_id=child_agent_id,
            principal_id=stack["principal_id"],
            controller_id=stack["controller_id"],
            scope=DelegationScope(action_classes=["SEARCH"], delegation_depth=0),
            signing_key_id=stack["agent_key_id"],
        )
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t-delegate")),
            action="DELEGATE",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id=delegation.delegation_id,
            authorization_id=str(make_identifier("authorization", "auth-parent")),
        )

        child_actor = Actor(
            controller_id=stack["controller_id"],
            principal_id=stack["principal_id"],
            agent_id=child_agent_id,
            agent_instance_id=str(make_identifier("agent-instance", "child", version="r1")),
        )
        stack["collector"].record(
            actor=child_actor,
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t-child")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=child_key_id,
            delegation_id=delegation.delegation_id,
            resource_id="urn:web:example",
            authorization_id=str(make_identifier("authorization", "auth-child")),
        )
        assert len(stack["ledger"]) == 2
        assert LedgerVerifier(stack["keys"]).verify(stack["ledger"]).ok

    def test_model_switch_preserves_agent_identity(self, stack) -> None:
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t1")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:1",
        )
        execution_context_2 = ExecutionContext(
            provider_id=stack["ec"].provider_id,
            model_id=stack["ec"].model_id,
            model_version_id=str(make_identifier("model", "example-llm", version="v2.0")),
            deployment_id=stack["ec"].deployment_id,
        )
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=execution_context_2,
            task_id=str(make_identifier("task", "t2")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:2",
        )
        events = stack["ledger"].events()
        assert events[0].actor.agent_id == events[1].actor.agent_id
        assert events[0].execution_context.model_version_id != events[1].execution_context.model_version_id

    def test_provider_switch_preserves_agent_identity(self, stack) -> None:
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t1")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:1",
        )
        execution_context_2 = ExecutionContext(
            provider_id=str(make_identifier("provider", "provider-002")),
            model_id=stack["ec"].model_id,
            model_version_id=stack["ec"].model_version_id,
            deployment_id=str(make_identifier("deployment", "dep-002")),
        )
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=execution_context_2,
            task_id=str(make_identifier("task", "t2")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:2",
        )
        events = stack["ledger"].events()
        assert events[0].actor.agent_id == events[1].actor.agent_id
        assert events[0].execution_context.provider_id != events[1].execution_context.provider_id

    def test_filesystem_adapter(self, tmp_path: Path, stack) -> None:
        adapter = FilesystemAdapter(tmp_path)
        path = Path("test.txt")
        result = adapter.create(path, b"hello")
        assert result["after_digest"].startswith("sha256:")
        assert result["before_digest"] is None
        result_2 = adapter.modify(path, b"world")
        assert result_2["before_digest"] != result_2["after_digest"]

    def test_github_evidence_adapter(self, stack) -> None:
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t1")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:1",
        )
        signing_key = stack["keys"].get_signing_key(stack["agent_key_id"])
        adapter = GitHubEvidenceAdapter(stack["agent_key_id"], signing_key.public_pem())
        anchor = adapter.make_merkle_root_anchor(stack["ledger"].events())
        assert anchor["schema"] == "aegistrace.merkle_root.v1"
        assert anchor["root"].startswith("sha256:")
        assert anchor["event_count"] == 1

    def test_ledger_persistence_and_reload(self, tmp_path: Path, stack) -> None:
        for index in range(3):
            stack["collector"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=str(make_identifier("task", f"t{index}")),
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                resource_id=f"urn:web:{index}",
            )
        path = tmp_path / "ledger.jsonl"
        stack["ledger"].save(path)
        reloaded = AppendOnlyLedger.load(path)
        assert len(reloaded) == 3
        assert LedgerVerifier(stack["keys"]).verify(reloaded).ok

    def test_cli_verify_hash_only_compatibility(self, tmp_path: Path, stack) -> None:
        from aegistrace.cli.verify import main as verify_main

        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t1")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            resource_id="urn:web:1",
        )
        path = tmp_path / "ledger.jsonl"
        stack["ledger"].save(path)
        assert verify_main(["--ledger", str(path), "--hash-only"]) == 0

    def test_cli_audit(self, tmp_path: Path, stack) -> None:
        from aegistrace.cli.audit import main as audit_main

        for action in ["SEARCH", "READ", "SEARCH"]:
            stack["collector"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=str(make_identifier("task", "t1")),
                action=action,
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                resource_id="urn:web:1",
            )
        path = tmp_path / "ledger.jsonl"
        stack["ledger"].save(path)
        output = tmp_path / "audit.json"
        assert audit_main(["--ledger", str(path), "--output", str(output)]) == 0
        report = json.loads(output.read_text())
        assert report["event_count"] == 3
        assert report["actions"]["SEARCH"] == 2
        assert report["actions"]["READ"] == 1
