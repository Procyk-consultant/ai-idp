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
from aegistrace.authorization.entitlements import (
    CompositeApproverEntitlementProvider,
    PrincipalApproverEntitlementProvider,
    StaticApproverEntitlementProvider,
)
from aegistrace.authorization.intent import ActionIntent
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

    ids = {
        "controller": str(make_identifier("controller", "org-001")),
        "principal": str(make_identifier("principal", "principal-001")),
        "second_approver": str(make_identifier("principal", "principal-002")),
        "agent": str(make_identifier("agent", "agent-001")),
        "instance": str(make_identifier("agent-instance", "agent-001", version="run-001")),
        "provider": str(make_identifier("provider", "provider-001")),
        "model": str(make_identifier("model", "model-001")),
        "model_version": str(make_identifier("model", "model-001", version="v1")),
        "deployment": str(make_identifier("deployment", "deployment-001")),
        "task": str(make_identifier("task", "task-001")),
        "controller_key": str(make_identifier("key", "controller-key")),
        "principal_key": str(make_identifier("key", "principal-key")),
        "second_approver_key": str(make_identifier("key", "principal-key-002")),
        "agent_key": str(make_identifier("key", "agent-key")),
    }

    entitlements = CompositeApproverEntitlementProvider(
        PrincipalApproverEntitlementProvider(),
        StaticApproverEntitlementProvider(
            {ids["second_approver"]: ["DESTROY_KEY"]}
        ),
    )
    policy = PolicyEngine(keys, approver_entitlements=entitlements)
    delegations = DelegationBroker(keys)
    governed = GovernedEventService(
        collector=EventCollector(ledger, keys),
        policy_engine=policy,
        delegation_broker=delegations,
        registry=registry,
    )

    registry.register(ids["controller"], "controller")
    registry.register(ids["principal"], "principal")
    registry.register(ids["second_approver"], "principal")
    registry.register(ids["agent"], "agent", {"controller_id": ids["controller"]})
    registry.register(ids["instance"], "agent-instance", {"agent_id": ids["agent"]})
    registry.register(ids["provider"], "provider")
    registry.register(ids["model"], "model")
    registry.register(ids["model_version"], "model")
    registry.register(ids["deployment"], "deployment")
    registry.register(ids["task"], "task")
    keys.create_key(ids["controller_key"], bound_entity_id=ids["controller"])
    keys.create_key(ids["principal_key"], bound_entity_id=ids["principal"])
    keys.create_key(ids["second_approver_key"], bound_entity_id=ids["second_approver"])
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
        "policy": policy,
        "delegations": delegations,
        "governed": governed,
        "actor": actor,
        "ec": execution_context,
        "ids": ids,
    }


def _authorization(
    stack,
    *,
    agent: str | None = None,
    task: str | None = None,
    scope=None,
    delegation=None,
):
    ids = stack["ids"]
    return stack["policy"].issue_authorization(
        principal_id=ids["principal"],
        controller_id=ids["controller"],
        agent_id=agent or ids["agent"],
        task_id=task or ids["task"],
        scope=scope or {"action_classes": ["SEARCH"]},
        signing_key_id=ids["controller_key"],
        delegation_id=delegation,
    )


def _intent_digest(
    stack,
    *,
    action: str,
    visibility: str,
    task_id: str | None = None,
    actor: Actor | None = None,
    delegation_id: str | None = None,
    resource_id: str | None = None,
    scope_context: ScopeContext | None = None,
) -> str:
    ids = stack["ids"]
    effective_actor = actor or stack["actor"]
    context = stack["ec"]
    return ActionIntent(
        controller_id=effective_actor.controller_id,
        principal_id=effective_actor.principal_id,
        agent_id=effective_actor.agent_id,
        agent_instance_id=effective_actor.agent_instance_id,
        provider_id=context.provider_id,
        model_id=context.model_id,
        model_version_id=context.model_version_id,
        deployment_id=context.deployment_id,
        task_id=task_id or ids["task"],
        action=action,
        visibility=visibility,
        delegation_id=delegation_id,
        resource_id=resource_id,
        scope_context=scope_context,
    ).digest()


class TestGovernedExecutionBoundary:
    def test_valid_root_action_is_governed_and_verifiable(self, governed_stack) -> None:
        stack = governed_stack
        authorization = _authorization(stack)
        event = stack["governed"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=stack["ids"]["task"],
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["ids"]["agent_key"],
            authorization_id=authorization.authorization_id,
            resource_id="urn:web:example",
        )
        assert event.governance_mode == "GOVERNED"
        assert event.authorization_id == authorization.authorization_id
        assert LedgerVerifier(stack["keys"]).verify(stack["ledger"]).ok

    def test_unknown_authorization_is_denied_and_recorded(self, governed_stack) -> None:
        stack = governed_stack
        with pytest.raises(GovernanceDenied) as exc_info:
            stack["governed"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=stack["ids"]["task"],
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["ids"]["agent_key"],
                authorization_id=str(make_identifier("authorization", "missing")),
            )
        assert exc_info.value.denial_event_id is not None
        denial = stack["ledger"].events()[0]
        assert denial.action == "DENY"
        assert denial.governance_mode == "DENIAL"

    def test_authorization_task_binding_fails_closed(self, governed_stack) -> None:
        stack = governed_stack
        authorization = _authorization(stack)
        other_task = str(make_identifier("task", "other-task"))
        stack["registry"].register(other_task, "task")
        with pytest.raises(GovernanceDenied, match="task"):
            stack["governed"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=other_task,
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["ids"]["agent_key"],
                authorization_id=authorization.authorization_id,
                record_denial=False,
            )

    def test_registry_relationship_mismatch_is_denied(self, governed_stack) -> None:
        stack = governed_stack
        authorization = _authorization(stack)
        stack["registry"].update(
            stack["ids"]["agent"],
            {"controller_id": str(make_identifier("controller", "other-controller"))},
        )
        with pytest.raises(GovernanceDenied, match="controller"):
            stack["governed"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=stack["ids"]["task"],
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["ids"]["agent_key"],
                authorization_id=authorization.authorization_id,
                record_denial=False,
            )

    def test_high_impact_approval_is_exact_consumed_and_not_reusable(self, governed_stack) -> None:
        stack = governed_stack
        authorization = _authorization(stack, scope={"action_classes": ["PUBLISH"]})
        digest = _intent_digest(
            stack,
            action="PUBLISH",
            visibility="ORGANIZATION_PRIVATE",
            resource_id="urn:artifact:report",
        )
        approval = stack["policy"].issue_approval(
            action="PUBLISH",
            action_digest=digest,
            approver_id=stack["ids"]["principal"],
            authorization_id=authorization.authorization_id,
            signing_key_id=stack["ids"]["principal_key"],
        )
        event = stack["governed"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=stack["ids"]["task"],
            action="PUBLISH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["ids"]["agent_key"],
            authorization_id=authorization.authorization_id,
            approval_id=approval.approval_id,
            resource_id="urn:artifact:report",
        )
        assert event.action_intent_digest == digest
        assert event.approval_ids == [approval.approval_id]
        approval_record = stack["policy"].get_approval(approval.approval_id)
        assert approval_record is not None and approval_record.used
        with pytest.raises(GovernanceDenied):
            stack["governed"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=stack["ids"]["task"],
                action="PUBLISH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["ids"]["agent_key"],
                authorization_id=authorization.authorization_id,
                approval_id=approval.approval_id,
                resource_id="urn:artifact:report",
                record_denial=False,
            )

    def test_delegated_child_action_requires_verified_scope_and_lineage(self, governed_stack) -> None:
        stack = governed_stack
        ids = stack["ids"]
        child = str(make_identifier("agent", "child-agent"))
        child_instance = str(make_identifier("agent-instance", "child-agent", version="run-1"))
        child_task = str(make_identifier("task", "child-task"))
        child_key = str(make_identifier("key", "child-key"))
        stack["registry"].register(child, "agent", {"controller_id": ids["controller"]})
        stack["registry"].register(child_instance, "agent-instance", {"agent_id": child})
        stack["registry"].register(child_task, "task")
        stack["keys"].create_key(child_key, bound_entity_id=child)
        delegation = stack["delegations"].create(
            parent_agent_id=ids["agent"],
            parent_instance_id=ids["instance"],
            child_agent_id=child,
            principal_id=ids["principal"],
            controller_id=ids["controller"],
            scope=DelegationScope(
                action_classes=["SEARCH"],
                resource_classes=["web"],
                provider_classes=["approved-provider"],
                delegation_depth=0,
            ),
            signing_key_id=ids["agent_key"],
        )
        stack["registry"].update(child, {"parent_delegation_id": delegation.delegation_id})
        authorization = _authorization(
            stack,
            agent=child,
            task=child_task,
            scope={
                "action_classes": ["SEARCH"],
                "resource_classes": ["web"],
                "provider_classes": ["approved-provider"],
            },
            delegation=delegation.delegation_id,
        )
        child_actor = Actor(
            controller_id=ids["controller"],
            principal_id=ids["principal"],
            agent_id=child,
            agent_instance_id=child_instance,
        )
        allowed_context = ScopeContext(resource_class="web", provider_class="approved-provider")
        event = stack["governed"].record(
            actor=child_actor,
            execution_context=stack["ec"],
            task_id=child_task,
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=child_key,
            authorization_id=authorization.authorization_id,
            delegation_id=delegation.delegation_id,
            scope_context=allowed_context,
        )
        assert event.delegation_chain == [delegation.delegation_id]
        with pytest.raises(GovernanceDenied):
            stack["governed"].record(
                actor=child_actor,
                execution_context=stack["ec"],
                task_id=child_task,
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=child_key,
                authorization_id=authorization.authorization_id,
                delegation_id=delegation.delegation_id,
                scope_context=ScopeContext(
                    resource_class="web",
                    provider_class="unapproved-provider",
                ),
                record_denial=False,
            )

    def test_dual_approval_is_preserved_as_exact_event_evidence(self, governed_stack) -> None:
        stack = governed_stack
        ids = stack["ids"]
        authorization = _authorization(stack, scope={"action_classes": ["DESTROY_KEY"]})
        resource_id = "urn:key:retired-key"
        digest = _intent_digest(
            stack,
            action="DESTROY_KEY",
            visibility="SEALED",
            resource_id=resource_id,
        )
        approval_1 = stack["policy"].issue_approval(
            action="DESTROY_KEY",
            action_digest=digest,
            approver_id=ids["principal"],
            authorization_id=authorization.authorization_id,
            signing_key_id=ids["principal_key"],
        )
        approval_2 = stack["policy"].issue_approval(
            action="DESTROY_KEY",
            action_digest=digest,
            approver_id=ids["second_approver"],
            authorization_id=authorization.authorization_id,
            signing_key_id=ids["second_approver_key"],
        )
        event = stack["governed"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=ids["task"],
            action="DESTROY_KEY",
            visibility="SEALED",
            signing_key_id=ids["agent_key"],
            authorization_id=authorization.authorization_id,
            approval_ids=[approval_1.approval_id, approval_2.approval_id],
            resource_id=resource_id,
        )
        assert event.action_intent_digest == digest
        assert set(event.approval_ids) == {approval_1.approval_id, approval_2.approval_id}
        first = stack["policy"].get_approval(approval_1.approval_id)
        second = stack["policy"].get_approval(approval_2.approval_id)
        assert first is not None and first.used
        assert second is not None and second.used
