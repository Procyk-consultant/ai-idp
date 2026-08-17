"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/integration/test_governance_boundary.py
Purpose: Integration tests for fail-closed governed execution
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import pytest

from aegistrace.authorization.engine import PolicyEngine
from aegistrace.authorization.scope import ScopeContext
from aegistrace.delegation.broker import DelegationBroker, DelegationScope
from aegistrace.events.collector import EventCollector
from aegistrace.events.models import Actor, ExecutionContext
from aegistrace.governance.service import GovernanceDenied, GovernedEventService
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier


@pytest.fixture
def governed_stack():
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
    principal_id = str(make_identifier("principal", "principal-001"))
    agent_id = str(make_identifier("agent", "agent-001"))
    instance_id = str(make_identifier("agent-instance", "agent-001", version="run-001"))
    provider_id = str(make_identifier("provider", "provider-001"))
    model_id = str(make_identifier("model", "model-001"))
    model_version_id = str(make_identifier("model", "model-001", version="v1"))
    deployment_id = str(make_identifier("deployment", "deployment-001"))
    task_id = str(make_identifier("task", "task-001"))

    registry.register(controller_id, "controller")
    registry.register(principal_id, "principal")
    registry.register(agent_id, "agent", {"controller_id": controller_id})
    registry.register(instance_id, "agent-instance", {"agent_id": agent_id})
    registry.register(provider_id, "provider")
    registry.register(model_id, "model")
    registry.register(model_version_id, "model")
    registry.register(deployment_id, "deployment")
    registry.register(task_id, "task")

    controller_key_id = str(make_identifier("key", "controller-key"))
    principal_key_id = str(make_identifier("key", "principal-key"))
    agent_key_id = str(make_identifier("key", "agent-key"))
    keys.create_key(controller_key_id, bound_entity_id=controller_id)
    keys.create_key(principal_key_id, bound_entity_id=principal_id)
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
        "governed": governed,
        "actor": actor,
        "ec": execution_context,
        "controller_id": controller_id,
        "principal_id": principal_id,
        "agent_id": agent_id,
        "task_id": task_id,
        "controller_key_id": controller_key_id,
        "principal_key_id": principal_key_id,
        "agent_key_id": agent_key_id,
    }


def _authorization(stack, *, agent_id: str | None = None, task_id: str | None = None, scope=None, delegation_id=None):
    return stack["policy"].issue_authorization(
        principal_id=stack["principal_id"],
        controller_id=stack["controller_id"],
        agent_id=agent_id or stack["agent_id"],
        task_id=task_id or stack["task_id"],
        scope=scope or {"action_classes": ["SEARCH"]},
        signing_key_id=stack["controller_key_id"],
        delegation_id=delegation_id,
    )


class TestGovernedExecutionBoundary:
    def test_valid_root_action_is_governed_and_verifiable(self, governed_stack) -> None:
        stack = governed_stack
        authorization = _authorization(stack)
        event = stack["governed"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=stack["task_id"],
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            authorization_id=authorization.authorization_id,
            resource_id="urn:web:example",
        )
        assert event.governance_mode == "GOVERNED"
        assert event.authorization_id == authorization.authorization_id
        assert event.delegation_chain == []
        report = LedgerVerifier(stack["keys"]).verify(stack["ledger"])
        assert report.ok, report.failures

    def test_unknown_authorization_is_denied_and_denial_is_evidence(self, governed_stack) -> None:
        stack = governed_stack
        fake_authorization = str(make_identifier("authorization", "missing"))
        with pytest.raises(GovernanceDenied) as exc_info:
            stack["governed"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=stack["task_id"],
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                authorization_id=fake_authorization,
            )
        assert exc_info.value.denial_event_id is not None
        events = stack["ledger"].events()
        assert len(events) == 1
        assert events[0].action == "DENY"
        assert events[0].governance_mode == "DENIAL"
        assert "authorization not found" in (events[0].decision_reason or "")

    def test_authorization_actor_and_task_bindings_fail_closed(self, governed_stack) -> None:
        stack = governed_stack
        authorization = _authorization(stack)
        mismatched_actor = Actor(
            controller_id=stack["actor"].controller_id,
            principal_id=stack["actor"].principal_id,
            agent_id=str(make_identifier("agent", "other-agent")),
            agent_instance_id=stack["actor"].agent_instance_id,
        )
        with pytest.raises(GovernanceDenied):
            stack["governed"].record(
                actor=mismatched_actor,
                execution_context=stack["ec"],
                task_id=stack["task_id"],
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                authorization_id=authorization.authorization_id,
                record_denial=False,
            )

        other_task = str(make_identifier("task", "other-task"))
        stack["registry"].register(other_task, "task")
        with pytest.raises(GovernanceDenied, match="task"):
            stack["governed"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=other_task,
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                authorization_id=authorization.authorization_id,
                record_denial=False,
            )

    def test_registry_relationships_are_mandatory(self, governed_stack) -> None:
        stack = governed_stack
        authorization = _authorization(stack)
        stack["registry"].resolve(stack["agent_id"]).attributes.pop("controller_id")
        with pytest.raises(GovernanceDenied, match="controller_id"):
            stack["governed"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=stack["task_id"],
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                authorization_id=authorization.authorization_id,
                record_denial=False,
            )

    def test_high_impact_approval_is_recorded_and_consumed(self, governed_stack) -> None:
        stack = governed_stack
        authorization = _authorization(stack, scope={"action_classes": ["PUBLISH"]})
        approval = stack["policy"].issue_approval(
            action="PUBLISH",
            approver_id=stack["principal_id"],
            authorization_id=authorization.authorization_id,
            signing_key_id=stack["principal_key_id"],
        )
        event = stack["governed"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=stack["task_id"],
            action="PUBLISH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["agent_key_id"],
            authorization_id=authorization.authorization_id,
            approval_id=approval.approval_id,
        )
        assert event.approval_ids == [approval.approval_id]
        approval_record = stack["policy"].get_approval(approval.approval_id)
        assert approval_record is not None and approval_record.used
        with pytest.raises(GovernanceDenied):
            stack["governed"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=stack["task_id"],
                action="PUBLISH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key_id"],
                authorization_id=authorization.authorization_id,
                approval_id=approval.approval_id,
                record_denial=False,
            )

    def test_delegated_child_action_requires_verified_lineage(self, governed_stack) -> None:
        stack = governed_stack
        child_agent_id = str(make_identifier("agent", "child-agent"))
        child_instance_id = str(make_identifier("agent-instance", "child-agent", version="run-1"))
        child_task_id = str(make_identifier("task", "child-task"))
        child_key_id = str(make_identifier("key", "child-key"))
        stack["registry"].register(child_agent_id, "agent", {"controller_id": stack["controller_id"]})
        stack["registry"].register(child_instance_id, "agent-instance", {"agent_id": child_agent_id})
        stack["registry"].register(child_task_id, "task")
        stack["keys"].create_key(child_key_id, bound_entity_id=child_agent_id)

        delegation = stack["delegations"].create(
            parent_agent_id=stack["agent_id"],
            parent_instance_id=stack["actor"].agent_instance_id,
            child_agent_id=child_agent_id,
            principal_id=stack["principal_id"],
            controller_id=stack["controller_id"],
            scope=DelegationScope(
                action_classes=["SEARCH"],
                resource_classes=["web"],
                provider_classes=["approved-provider"],
                delegation_depth=0,
            ),
            signing_key_id=stack["agent_key_id"],
        )
        stack["registry"].update(child_agent_id, {"parent_delegation_id": delegation.delegation_id})
        authorization = _authorization(
            stack,
            agent_id=child_agent_id,
            task_id=child_task_id,
            scope={
                "action_classes": ["SEARCH"],
                "resource_classes": ["web"],
                "provider_classes": ["approved-provider"],
            },
            delegation_id=delegation.delegation_id,
        )
        child_actor = Actor(
            controller_id=stack["controller_id"],
            principal_id=stack["principal_id"],
            agent_id=child_agent_id,
            agent_instance_id=child_instance_id,
        )
        scope_context = ScopeContext(resource_class="web", provider_class="approved-provider")
        event = stack["governed"].record(
            actor=child_actor,
            execution_context=stack["ec"],
            task_id=child_task_id,
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=child_key_id,
            authorization_id=authorization.authorization_id,
            delegation_id=delegation.delegation_id,
            scope_context=scope_context,
        )
        assert event.delegation_chain == [delegation.delegation_id]

        with pytest.raises(GovernanceDenied):
            stack["governed"].record(
                actor=child_actor,
                execution_context=stack["ec"],
                task_id=child_task_id,
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=child_key_id,
                authorization_id=authorization.authorization_id,
                delegation_id=delegation.delegation_id,
                scope_context=ScopeContext(resource_class="web", provider_class="unapproved-provider"),
                record_denial=False,
            )

    def test_dual_approval_is_preserved_as_event_evidence(self, governed_stack) -> None:
        stack = governed_stack
        second_approver = str(make_identifier("principal", "principal-002"))
        second_key = str(make_identifier("key", "principal-key-002"))
        stack["registry"].register(second_approver, "principal")
        stack["keys"].create_key(second_key, bound_entity_id=second_approver)
        authorization = _authorization(stack, scope={"action_classes": ["DESTROY_KEY"]})
        approval_1 = stack["policy"].issue_approval(
            action="DESTROY_KEY",
            approver_id=stack["principal_id"],
            authorization_id=authorization.authorization_id,
            signing_key_id=stack["principal_key_id"],
        )
        approval_2 = stack["policy"].issue_approval(
            action="DESTROY_KEY",
            approver_id=second_approver,
            authorization_id=authorization.authorization_id,
            signing_key_id=second_key,
        )
        event = stack["governed"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=stack["task_id"],
            action="DESTROY_KEY",
            visibility="SEALED",
            signing_key_id=stack["agent_key_id"],
            authorization_id=authorization.authorization_id,
            approval_ids=[approval_1.approval_id, approval_2.approval_id],
            resource_id="urn:key:retired-key",
        )
        assert set(event.approval_ids) == {approval_1.approval_id, approval_2.approval_id}
        assert stack["policy"].get_approval(approval_1.approval_id).used  # type: ignore[union-attr]
        assert stack["policy"].get_approval(approval_2.approval_id).used  # type: ignore[union-attr]
