"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/security/test_attacks.py
Purpose: Adversarial security tests for identity, signatures, chain integrity, and governance
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import copy

import pytest

from aegistrace.authorization.engine import PolicyEngine
from aegistrace.delegation.broker import DelegationBroker
from aegistrace.events.collector import EventCollector
from aegistrace.events.models import Actor, Event, ExecutionContext
from aegistrace.governance.service import GovernanceDenied, GovernedEventService
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier
from aegistrace.signing.canonical import canonicalize_for_hash, canonicalize_for_signature
from aegistrace.signing.ed25519 import sha256_hex


@pytest.fixture
def stack():
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

    controller = str(make_identifier("controller", "org-001"))
    principal = str(make_identifier("principal", "p1"))
    agent = str(make_identifier("agent", "a1"))
    instance = str(make_identifier("agent-instance", "a1", version="r1"))
    provider = str(make_identifier("provider", "p1"))
    model = str(make_identifier("model", "m1"))
    model_version = str(make_identifier("model", "m1", version="v1"))
    deployment = str(make_identifier("deployment", "d1"))
    task = str(make_identifier("task", "t1"))
    agent_key = str(make_identifier("key", "k1"))
    controller_key = str(make_identifier("key", "controller-key"))

    registry.register(controller, "controller")
    registry.register(principal, "principal")
    registry.register(agent, "agent", {"controller_id": controller})
    registry.register(instance, "agent-instance", {"agent_id": agent})
    registry.register(provider, "provider")
    registry.register(model, "model")
    registry.register(model_version, "model")
    registry.register(deployment, "deployment")
    registry.register(task, "task")

    keys.create_key(agent_key, bound_entity_id=agent)
    keys.create_key(controller_key, bound_entity_id=controller)
    actor = Actor(
        controller_id=controller,
        principal_id=principal,
        agent_id=agent,
        agent_instance_id=instance,
    )
    execution_context = ExecutionContext(
        provider_id=provider,
        model_id=model,
        model_version_id=model_version,
        deployment_id=deployment,
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
        "task": task,
        "agent_key": agent_key,
        "controller_key": controller_key,
    }


def _record_one(stack, action: str = "SEARCH"):
    return stack["collector"].record(
        actor=stack["actor"],
        execution_context=stack["ec"],
        task_id=stack["task"],
        action=action,
        visibility="ORGANIZATION_PRIVATE",
        signing_key_id=stack["agent_key"],
        resource_id="urn:web:1",
    )


class TestAttacks:
    def test_forged_agent_event_rejected_at_key_binding(self, stack) -> None:
        _record_one(stack)
        attacker_agent = str(make_identifier("agent", "attacker"))
        attacker_key = str(make_identifier("key", "attacker"))
        stack["keys"].create_key(attacker_key, bound_entity_id=attacker_agent)
        with pytest.raises(PermissionError):
            stack["collector"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=stack["task"],
                action="DELETE",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=attacker_key,
            )

    def test_revoked_key_cannot_produce_new_event(self, stack) -> None:
        _record_one(stack)
        stack["keys"].revoke(stack["agent_key"])
        with pytest.raises(PermissionError):
            _record_one(stack, "DELETE")
        assert len(stack["ledger"]) == 1

    def test_content_modification_with_recomputed_hash_fails_signature_verification(self, stack) -> None:
        original = _record_one(stack)
        tampered = copy.deepcopy(original.to_dict())
        original_signature = tampered["signature"]
        tampered["action"] = "DELETE"
        tampered["event_hash"] = sha256_hex(canonicalize_for_hash(tampered))
        tampered["signature"] = original_signature

        tampered_ledger = AppendOnlyLedger()
        tampered_ledger.append(Event.from_dict(tampered))
        report = LedgerVerifier(stack["keys"]).verify(tampered_ledger)
        assert not report.ok
        assert any("signature invalid" in failure for failure in report.failures)

    def test_compromised_middle_event_still_breaks_successor_chain(self, stack) -> None:
        for _ in range(3):
            _record_one(stack)
        events = stack["ledger"].events()
        tampered = copy.deepcopy(events[1].to_dict())
        tampered["action"] = "DELETE"
        tampered["event_hash"] = sha256_hex(canonicalize_for_hash(tampered))
        signing_key = stack["keys"].get_signing_key(stack["agent_key"])
        tampered["signature"] = signing_key.sign(canonicalize_for_signature(tampered))

        rebuilt = AppendOnlyLedger()
        rebuilt.append(events[0])
        rebuilt.append(Event.from_dict(tampered))
        with pytest.raises(ValueError, match="hash chain broken"):
            rebuilt.append(events[2])

    def test_event_deletion_is_detected(self, stack) -> None:
        for _ in range(3):
            _record_one(stack)
        events = stack["ledger"].events()
        rebuilt = AppendOnlyLedger()
        rebuilt.append(events[0])
        with pytest.raises(ValueError, match="hash chain broken"):
            rebuilt.append(events[2])

    def test_event_reordering_is_detected(self, stack) -> None:
        for _ in range(3):
            _record_one(stack)
        events = stack["ledger"].events()
        with pytest.raises(ValueError, match="hash chain broken"):
            AppendOnlyLedger().append(events[1])

    def test_duplicate_event_id_is_rejected(self, stack) -> None:
        event = _record_one(stack)
        with pytest.raises(ValueError, match="duplicate event_id"):
            stack["ledger"].append(event)

    def test_child_agent_cannot_bypass_missing_delegation(self, stack) -> None:
        child_agent = str(make_identifier("agent", "child"))
        child_instance = str(make_identifier("agent-instance", "child", version="run-1"))
        child_key = str(make_identifier("key", "child-key"))
        missing_delegation = str(make_identifier("delegation", "missing"))
        stack["registry"].register(
            child_agent,
            "agent",
            {
                "controller_id": stack["actor"].controller_id,
                "parent_delegation_id": missing_delegation,
            },
        )
        stack["registry"].register(child_instance, "agent-instance", {"agent_id": child_agent})
        stack["keys"].create_key(child_key, bound_entity_id=child_agent)
        authorization = stack["policy"].issue_authorization(
            principal_id=stack["actor"].principal_id,
            controller_id=stack["actor"].controller_id,
            agent_id=child_agent,
            task_id=stack["task"],
            scope={"action_classes": ["SEARCH"]},
            signing_key_id=stack["controller_key"],
            delegation_id=missing_delegation,
        )
        child_actor = Actor(
            controller_id=stack["actor"].controller_id,
            principal_id=stack["actor"].principal_id,
            agent_id=child_agent,
            agent_instance_id=child_instance,
        )
        with pytest.raises(GovernanceDenied, match="delegation chain"):
            stack["governed"].record(
                actor=child_actor,
                execution_context=stack["ec"],
                task_id=stack["task"],
                action="SEARCH",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=child_key,
                authorization_id=authorization.authorization_id,
                delegation_id=missing_delegation,
                record_denial=False,
            )
        assert len(stack["ledger"]) == 0

    def test_invalid_action_rejected(self, stack) -> None:
        with pytest.raises(ValueError):
            stack["collector"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=stack["task"],
                action="INVALID_ACTION",
                visibility="ORGANIZATION_PRIVATE",
                signing_key_id=stack["agent_key"],
            )

    def test_invalid_visibility_rejected(self, stack) -> None:
        with pytest.raises(ValueError):
            stack["collector"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=stack["task"],
                action="SEARCH",
                visibility="INVALID_TIER",
                signing_key_id=stack["agent_key"],
            )

    def test_signature_tampering_is_detected(self, stack) -> None:
        event = _record_one(stack)
        tampered = event.to_dict()
        tampered["signature"] = "Ed25519:" + "A" * 88
        tampered_ledger = AppendOnlyLedger()
        tampered_ledger.append(Event.from_dict(tampered))
        report = LedgerVerifier(stack["keys"]).verify(tampered_ledger)
        assert not report.ok
        assert any("signature" in failure.lower() for failure in report.failures)
