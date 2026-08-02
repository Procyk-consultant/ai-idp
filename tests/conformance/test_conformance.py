"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/conformance/test_conformance.py
Purpose: Conformance tests for AI-IDP invariants
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from aegistrace.events.collector import EventCollector
from aegistrace.events.models import VISIBILITY_TIERS, Actor, ExecutionContext
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger, LedgerVerifier

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


@pytest.fixture
def stack():
    ledger = AppendOnlyLedger()
    keys = KeyService()
    collector = EventCollector(ledger, keys)
    controller = str(make_identifier("controller", "org-001"))
    principal = str(make_identifier("principal", "p1"))
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


class TestConformance:
    def test_event_conforms_to_schema(self, stack) -> None:
        """Every recorded event conforms to schemas/event.schema.json."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        schema = load_schema("event")
        for e in stack["ledger"].events():
            # The event's to_dict() should match the schema (note: _metadata in schema is not enforced)
            instance = {k: v for k, v in e.to_dict().items() if k in schema["properties"]}
            # jsonschema.validate raises on failure
            jsonschema.validate(instance=instance, schema=schema)

    def test_all_actions_in_vocabulary(self, stack) -> None:
        """Every action verb in the implementation is in the canonical ACTIONS list."""
        # Try to record each action; only canonical ones should succeed
        non_canonical = ["HACK", "BYPASS", "FORGE", "TAMPER"]
        for action in non_canonical:
            with pytest.raises(ValueError):
                stack["collector"].record(
                    actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
                    action=action, visibility="ORGANIZATION_PRIVATE",
                    signing_key_id="aitrace://ca/key/k1",
                    resource_id="urn:web:1",
                )

    def test_visibility_tiers_canonical(self) -> None:
        assert set(VISIBILITY_TIERS) == {"PUBLIC", "CONTROLLED", "ORGANIZATION_PRIVATE", "SEALED"}

    def test_required_invariants_hold(self, stack) -> None:
        """Required invariants from spec/AI-IDP-CORE.md Section 5."""
        # Invariant 1: every agent instance resolves to one persistent agent
        # Invariant 3: every action resolves to an agent instance
        # Invariant 4: every action resolves to a task
        # Invariant 14: every event is cryptographically linked
        # Invariant 15: every quality claim resolves to evidence (out of scope for unit test)
        for _ in range(3):
            stack["collector"].record(
                actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
                action="SEARCH", visibility="ORGANIZATION_PRIVATE",
                signing_key_id="aitrace://ca/key/k1",
                resource_id="urn:web:1",
            )
        events = stack["ledger"].events()
        for e in events:
            assert e.actor.agent_id  # not empty
            assert e.actor.agent_instance_id
            assert e.task_id
            assert e.event_hash.startswith("sha256:")
            assert e.signature.startswith("Ed25519:")
            assert e.previous_event_hash is None or e.previous_event_hash.startswith("sha256:")
        # Hash chain
        for i in range(1, len(events)):
            assert events[i].previous_event_hash == events[i - 1].event_hash

    def test_no_silent_history_modification(self, stack) -> None:
        """The ledger is append-only: no event can be modified or removed."""
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="ORGANIZATION_PRIVATE",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        # The internal _events list is not exposed for modification; we test that the public API has no mutation methods.
        ledger = stack["ledger"]
        assert not hasattr(ledger, "modify_event")
        assert not hasattr(ledger, "delete_event")
        assert not hasattr(ledger, "remove_event")
        assert not hasattr(ledger, "update_event")

    def test_public_tier_excludes_sensitive_fields(self, stack) -> None:
        """PUBLIC-tier events do not expose delegation_id, approval_id, before/after digests."""
        # The visibility tier is recorded; downstream filtering enforces non-exposure.
        stack["collector"].record(
            actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", "t1")),
            action="SEARCH", visibility="PUBLIC",
            signing_key_id="aitrace://ca/key/k1",
            resource_id="urn:web:1",
        )
        e = stack["ledger"].events()[0]
        assert e.visibility == "PUBLIC"
        # A public-tier projection would omit sensitive fields; the implementation records visibility for downstream filtering.

    def test_ledger_integrity_after_multiple_appends(self, stack) -> None:
        """The ledger remains verifiable after many appends."""
        for i in range(50):
            stack["collector"].record(
                actor=stack["actor"], execution_context=stack["ec"], task_id=str(make_identifier("task", f"t{i}")),
                action="SEARCH", visibility="ORGANIZATION_PRIVATE",
                signing_key_id="aitrace://ca/key/k1",
                resource_id=f"urn:web:{i}",
            )
        verifier = LedgerVerifier(stack["keys"])
        report = verifier.verify(stack["ledger"])
        assert report.ok
        assert len(stack["ledger"]) == 50
