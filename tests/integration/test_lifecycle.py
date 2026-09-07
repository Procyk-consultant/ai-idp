"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/integration/test_lifecycle.py
Purpose: Integration tests for the AegisTrace evidence lifecycle
Version: 2.1.0
Last Material Revision: 2026-09-07
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from aegistrace.adapters.filesystem import FilesystemAdapter
from aegistrace.adapters.github import GitHubEvidenceAdapter
from aegistrace.authorization.engine import PolicyEngine
from aegistrace.authorization.intent import ActionIntent
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

    ids = {
        "controller": str(make_identifier("controller", "org-001")),
        "principal": str(make_identifier("principal", "user-012")),
        "agent": str(make_identifier("agent", "research-agent", version="v3")),
        "instance": str(make_identifier("agent-instance", "research-agent", version="run-0042")),
        "provider": str(make_identifier("provider", "provider-001")),
        "model": str(make_identifier("model", "example-llm")),
        "model_version": str(make_identifier("model", "example-llm", version="v1.2")),
        "deployment": str(make_identifier("deployment", "deployment-001")),
        "controller_key": str(make_identifier("key", "ctrl-001")),
        "principal_key": str(make_identifier("key", "principal-001")),
        "agent_key": str(make_identifier("key", "agent-001")),
    }
    for entity_id, entity_type in (
        (ids["controller"], "controller"),
        (ids["principal"], "principal"),
        (ids["agent"], "agent"),
        (ids["instance"], "agent-instance"),
        (ids["provider"], "provider"),
        (ids["model"], "model"),
        (ids["model_version"], "model"),
        (ids["deployment"], "deployment"),
    ):
        registry.register(entity_id, entity_type)
    keys.create_key(ids["controller_key"], bound_entity_id=ids["controller"])
    keys.create_key(ids["principal_key"], bound_entity_id=ids["principal"])
    keys.create_key(ids["agent_key"], bound_entity_id=ids["agent"])

    actor = Actor(
        controller_id=ids["controller"],
        principal_id=ids["principal"],
        agent_id=ids["agent"],
        agent_instance_id=ids["instance"],
    )
    execution_context = ExecutionContext(
        provider_id=ids["provider"],
        model_id=ids["model"],
        model_version_id=ids["model_version"],
        deployment_id=ids["deployment"],
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
        "ids": ids,
    }


class TestLifecycle:
    def test_complete_task_lifecycle(self, stack) -> None:
        """Authorization, exact approval, evidence, and verification compose correctly."""
        ids = stack["ids"]
        task_id = str(make_identifier("task", "t1"))
        authorization = stack["policy"].issue_authorization(
            principal_id=ids["principal"],
            controller_id=ids["controller"],
            agent_id=ids["agent"],
            task_id=task_id,
            scope={"action_classes": ["SEARCH", "READ", "PUBLISH"]},
            signing_key_id=ids["controller_key"],
        )
        before_digest = "sha256:" + "a" * 64
        after_digest = "sha256:" + "b" * 64
        publish_intent = ActionIntent(
            controller_id=ids["controller"],
            principal_id=ids["principal"],
            agent_id=ids["agent"],
            agent_instance_id=ids["instance"],
            provider_id=ids["provider"],
            model_id=ids["model"],
            model_version_id=ids["model_version"],
            deployment_id=ids["deployment"],
            task_id=task_id,
            action="PUBLISH",
            jurisdiction_id="ca",
            visibility="ORGANIZATION_PRIVATE",
            resource_id="urn:artifact:report",
            before_digest=before_digest,
            after_digest=after_digest,
        )
        approval = stack["policy"].issue_approval(
            action="PUBLISH",
            action_digest=publish_intent.digest(),
            approver_id=ids["principal"],
            authorization_id=authorization.authorization_id,
            signing_key_id=ids["principal_key"],
        )

        for action in ("SEARCH", "READ"):
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
                signing_key_id=ids["agent_key"],
                authorization_id=authorization.authorization_id,
                resource_id=f"urn:example:{action}",
            )

        publish_decision = stack["policy"].evaluate(
            action="PUBLISH",
            authorization_id=authorization.authorization_id,
            action_digest=publish_intent.digest(),
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
            signing_key_id=ids["agent_key"],
            authorization_id=authorization.authorization_id,
            approval_id=approval.approval_id,
            action_intent_digest=publish_intent.digest(),
            resource_id="urn:artifact:report",
            before_digest=before_digest,
            after_digest=after_digest,
        )
        assert len(stack["ledger"]) == 3
        assert LedgerVerifier(stack["keys"]).verify(stack["ledger"]).ok

    def test_parent_child_delegation_evidence(self, stack) -> None:
        ids = stack["ids"]
        child_agent_id = str(make_identifier("agent", "child"))
        child_key_id = str(make_identifier("key", "child-001"))
        stack["registry"].register(child_agent_id, "agent")
        stack["keys"].create_key(child_key_id, bound_entity_id=child_agent_id)
        delegation = stack["delegations"].create(
            parent_agent_id=ids["agent"],
            parent_instance_id=ids["instance"],
            child_agent_id=child_agent_id,
            principal_id=ids["principal"],
            controller_id=ids["controller"],
            scope=DelegationScope(action_classes=["SEARCH"], delegation_depth=0),
            signing_key_id=ids["agent_key"],
        )
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t-delegate")),
            action="DELEGATE",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=ids["agent_key"],
            resource_id=delegation.delegation_id,
        )
        child_actor = Actor(
            controller_id=ids["controller"],
            principal_id=ids["principal"],
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
        )
        assert len(stack["ledger"]) == 2
        assert LedgerVerifier(stack["keys"]).verify(stack["ledger"]).ok

    def test_model_and_provider_switch_preserve_agent_identity(self, stack) -> None:
        ids = stack["ids"]
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t1")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=ids["agent_key"],
        )
        changed = ExecutionContext(
            provider_id=str(make_identifier("provider", "provider-002")),
            model_id=ids["model"],
            model_version_id=str(make_identifier("model", "example-llm", version="v2.0")),
            deployment_id=str(make_identifier("deployment", "dep-002")),
        )
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=changed,
            task_id=str(make_identifier("task", "t2")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=ids["agent_key"],
        )
        first, second = stack["ledger"].events()
        assert first.actor.agent_id == second.actor.agent_id
        assert first.execution_context.provider_id != second.execution_context.provider_id
        assert first.execution_context.model_version_id != second.execution_context.model_version_id

    def test_filesystem_adapter(self, tmp_path: Path, stack) -> None:
        adapter = FilesystemAdapter(tmp_path)
        path = Path("test.txt")
        created = adapter.create(path, b"hello")
        modified = adapter.modify(path, b"world")
        assert created["before_digest"] is None
        assert isinstance(created["after_digest"], str)
        assert created["after_digest"].startswith("sha256:")
        assert modified["before_digest"] != modified["after_digest"]

    def test_github_evidence_adapter(self, stack) -> None:
        ids = stack["ids"]
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t1")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=ids["agent_key"],
        )
        signing_key = stack["keys"].get_signing_key(ids["agent_key"])
        adapter = GitHubEvidenceAdapter(ids["agent_key"], signing_key.public_pem())
        anchor = adapter.make_merkle_root_anchor(stack["ledger"].events())
        assert anchor["schema"] == "aegistrace.merkle_root.v1"
        assert anchor["root"].startswith("sha256:")
        assert anchor["event_count"] == 1

    def test_ledger_persistence_reload_and_cli_paths(self, tmp_path: Path, stack) -> None:
        from aegistrace.cli.audit import main as audit_main
        from aegistrace.cli.verify import main as verify_main

        ids = stack["ids"]
        for index, action in enumerate(("SEARCH", "READ", "SEARCH")):
            stack["collector"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=str(make_identifier("task", f"t{index}")),
                action=action,
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=ids["agent_key"],
            )
        path = tmp_path / "ledger.jsonl"
        stack["ledger"].save(path)
        reloaded = AppendOnlyLedger.load(path)
        assert len(reloaded) == 3
        assert LedgerVerifier(stack["keys"]).verify(reloaded).ok
        assert verify_main(["--ledger", str(path), "--hash-only"]) == 0

        output = tmp_path / "audit.json"
        assert audit_main(["--ledger", str(path), "--output", str(output)]) == 0
        report = json.loads(output.read_text())
        assert report["event_count"] == 3
        assert report["actions"]["SEARCH"] == 2
        assert report["actions"]["READ"] == 1
