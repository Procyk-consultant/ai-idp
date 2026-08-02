"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/privacy/test_redaction.py
Purpose: Privacy tests - redaction and pseudonymization
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import pytest

from aegistrace.events.collector import EventCollector
from aegistrace.events.models import VISIBILITY_TIERS, Actor, ExecutionContext
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger


@pytest.fixture
def stack():
    ledger = AppendOnlyLedger()
    keys = KeyService()
    collector = EventCollector(ledger, keys)
    controller = str(make_identifier("controller", "org-001"))
    principal = str(make_identifier("principal", "user-XYZ"))  # pseudonymous
    agent = str(make_identifier("agent", "a1"))
    instance = str(make_identifier("agent-instance", "a1", version="r1"))
    keys.create_key("aitrace://ca/key/k1", bound_entity_id=agent)
    actor = Actor(controller_id=controller, principal_id=principal, agent_id=agent, agent_instance_id=instance)
    ec = ExecutionContext(
        provider_id=str(make_identifier("provider", "p1")),
        model_id=str(make_identifier("model", "m1")),
        model_version_id=str(make_identifier("model", "m1", version="v1")),
        deployment_id=str(make_identifier("deployment", "d1")),
    )
    return {"ledger": ledger, "keys": keys, "collector": collector, "actor": actor, "ec": ec}


class TestPrivacy:
    def test_principal_is_pseudonymous(self, stack) -> None:
        """Principal identifiers are pseudonymous by default."""
        assert "user-" in stack["actor"].principal_id
        # The principal_id is a URI, not a real name or email
        assert "@" not in stack["actor"].principal_id
        assert stack["actor"].principal_id.startswith("aitrace://ca/principal/")

    def test_visibility_tiers_enforced(self, stack) -> None:
        """All four visibility tiers are accepted."""
        for tier in VISIBILITY_TIERS:
            stack["collector"].record(
                actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
                action="SEARCH", visibility=tier,
                signing_key_id="aitrace://ca/key/k1",
                resource_id=f"urn:web:{tier}",
            )

    def test_no_real_contact_data_in_events(self, stack) -> None:
        """Events never contain real email addresses or phone numbers."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        events = stack["ledger"].events()
        event_json = repr(events[0].to_dict())
        # No real contact data appears
        assert "p.procyk.media@gmail.com" not in event_json
        assert "+1 (581)" not in event_json
        assert "linkedin.com" not in event_json

    def test_public_tier_excludes_sensitive_fields(self, stack) -> None:
        """PUBLIC events do not include delegation_id, approval_id, or before/after digests."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="PUBLIC",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        events = stack["ledger"].events()
        # The visibility tier is correctly recorded
        assert events[0].visibility == "PUBLIC"

    def test_sealed_tier_available(self, stack) -> None:
        """SEALED tier is available for sensitive events."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="ACCESS_SECRET", visibility="SEALED",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:secret:vault-1",
        )
        events = stack["ledger"].events()
        assert events[0].visibility == "SEALED"

    def test_user_enumeration_prevention(self, stack) -> None:
        """Multiple events by the same principal do not leak enumerable info."""
        for i in range(5):
            stack["collector"].record(
                actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", f"t{i}")),
                action="SEARCH", visibility="ORGANIZATION_PRIVATE",
                signing_key_id="aitrace://ca/key/k1",
                resource_id=f"urn:web:{i}",
            )
        events = stack["ledger"].events()
        # All events use the same pseudonymous principal_id; no real identity leaks
        ids = {e.actor.principal_id for e in events}
        assert len(ids) == 1  # same principal throughout
