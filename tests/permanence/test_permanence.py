"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/permanence/test_permanence.py
Purpose: Permanence tests - revocation, termination, key rotation, archival
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import pytest

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
    controller = str(make_identifier("controller", "org-001"))
    principal = str(make_identifier("principal", "p1"))
    agent = str(make_identifier("agent", "a1"))
    instance = str(make_identifier("agent-instance", "a1", version="r1"))
    keys.create_key("aitrace://ca/key/k1", bound_entity_id=agent)
    for eid in [controller, principal, agent, instance]:
        registry.register(eid, eid.split("/")[3].split("#")[0])
    actor = Actor(controller_id=controller, principal_id=principal, agent_id=agent, agent_instance_id=instance)
    ec = ExecutionContext(
        provider_id=str(make_identifier("provider", "p1")),
        model_id=str(make_identifier("model", "m1")),
        model_version_id=str(make_identifier("model", "m1", version="v1")),
        deployment_id=str(make_identifier("deployment", "d1")),
    )
    return {"ledger": ledger, "keys": keys, "registry": registry, "collector": collector, "actor": actor, "ec": ec, "agent_id": agent}


class TestPermanence:
    def test_revoked_agent_remains_resolvable(self, stack) -> None:
        """A revoked agent's identifier remains resolvable."""
        stack["registry"].revoke(stack["agent_id"], "for cause")
        rec = stack["registry"].resolve(stack["agent_id"])
        assert rec.state == "revoked"
        assert rec.is_resolvable()

    def test_terminated_agent_remains_resolvable(self, stack) -> None:
        """A terminated agent's identifier remains resolvable."""
        stack["registry"].terminate(stack["agent_id"], "end of life")
        rec = stack["registry"].resolve(stack["agent_id"])
        assert rec.state == "terminated"
        assert rec.is_resolvable()

    def test_revoked_key_signatures_remain_verifiable(self, stack) -> None:
        """Signatures by a now-revoked key remain verifiable."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        stack["keys"].revoke("aitrace://ca/key/k1")
        # Verify ledger still passes
        verifier = LedgerVerifier(stack["keys"])
        report = verifier.verify(stack["ledger"])
        assert report.ok, report.failures

    def test_key_rotation_preserves_history(self, stack) -> None:
        """Key rotation produces a new key; old events remain verifiable."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        # Rotate
        new_sk = stack["keys"].rotate("aitrace://ca/key/k1", "aitrace://ca/key/k2")
        # Sign a new event with the new key
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t2")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k2",
            resource_id="urn:web:2",
        )
        # Both events verify
        verifier = LedgerVerifier(stack["keys"])
        report = verifier.verify(stack["ledger"])
        assert report.ok
        assert len(stack["ledger"]) == 2

    def test_permanent_identifier_survives_model_switch(self, stack) -> None:
        """Model switch creates new execution context but agent identity is unchanged."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        ec2 = ExecutionContext(
            provider_id=stack["ec"].provider_id,
            model_id=stack["ec"].model_id,
            model_version_id=str(make_identifier("model", "m1", version="v2")),
            deployment_id=stack["ec"].deployment_id,
        )
        stack["collector"].record(
            actor=stack["actor"], execution_context=ec2, task_id=str(make_identifier("task", "t2")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:2",
        )
        events = stack["ledger"].events()
        assert events[0].actor.agent_id == events[1].actor.agent_id

    def test_permanent_identifier_survives_provider_switch(self, stack) -> None:
        """Provider switch creates new execution context but agent identity is unchanged."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        ec2 = ExecutionContext(
            provider_id=str(make_identifier("provider", "p2")),
            model_id=stack["ec"].model_id,
            model_version_id=stack["ec"].model_version_id,
            deployment_id=str(make_identifier("deployment", "d2")),
        )
        stack["collector"].record(
            actor=stack["actor"], execution_context=ec2, task_id=str(make_identifier("task", "t2")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:2",
        )
        events = stack["ledger"].events()
        assert events[0].actor.agent_id == events[1].actor.agent_id

    def test_archive_preserves_resolvability(self, stack) -> None:
        """Archived entities remain resolvable."""
        stack["registry"].terminate(stack["agent_id"], "end of life")
        stack["registry"].archive(stack["agent_id"], "retention expired")
        rec = stack["registry"].resolve(stack["agent_id"])
        assert rec.state == "archived"
        assert rec.is_resolvable()

    def test_ledger_permanence_after_agent_termination(self, stack) -> None:
        """After agent termination, the ledger's events remain verifiable."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        stack["registry"].terminate(stack["agent_id"], "end of life")
        verifier = LedgerVerifier(stack["keys"])
        report = verifier.verify(stack["ledger"])
        assert report.ok
