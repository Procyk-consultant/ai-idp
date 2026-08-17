"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/conformance/test_conformance.py
Purpose: Executable conformance assertions for selected AI-IDP invariants
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from aegistrace.disclosure.public import SENSITIVE_EVENT_FIELDS, PublicEventProjector
from aegistrace.events.collector import EventCollector
from aegistrace.events.models import VISIBILITY_TIERS, Actor, ExecutionContext
from aegistrace.identity.ids import Identifier, make_identifier
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
    actor = Actor(
        controller_id=str(make_identifier("controller", "org-001")),
        principal_id=str(make_identifier("principal", "p1")),
        agent_id=str(make_identifier("agent", "a1")),
        agent_instance_id=str(make_identifier("agent-instance", "a1", version="r1")),
    )
    execution_context = ExecutionContext(
        provider_id=str(make_identifier("provider", "p1")),
        model_id=str(make_identifier("model", "m1")),
        model_version_id=str(make_identifier("model", "m1", version="v1")),
        deployment_id=str(make_identifier("deployment", "d1")),
    )
    key_id = str(make_identifier("key", "k1"))
    keys.create_key(key_id, bound_entity_id=actor.agent_id)
    return {
        "ledger": ledger,
        "keys": keys,
        "collector": collector,
        "actor": actor,
        "ec": execution_context,
        "key_id": key_id,
    }


def _record(stack, *, action: str = "SEARCH", visibility: str = "ORGANIZATION_PRIVATE", task: str = "t1"):
    return stack["collector"].record(
        actor=stack["actor"],
        execution_context=stack["ec"],
        task_id=str(make_identifier("task", task)),
        action=action,
        visibility=visibility,
        signing_key_id=stack["key_id"],
        resource_id=f"urn:resource:{task}",
    )


class TestConformance:
    def test_event_conforms_to_normative_schema(self, stack) -> None:
        event = _record(stack)
        jsonschema.validate(instance=event.to_dict(), schema=load_schema("event"))

    def test_noncanonical_actions_are_rejected(self, stack) -> None:
        for action in ("HACK", "BYPASS", "FORGE", "TAMPER"):
            with pytest.raises(ValueError):
                _record(stack, action=action)

    def test_visibility_tiers_are_exactly_canonical(self) -> None:
        assert set(VISIBILITY_TIERS) == {
            "PUBLIC",
            "CONTROLLED",
            "ORGANIZATION_PRIVATE",
            "SEALED",
        }

    def test_selected_core_identity_and_chain_invariants_are_executable(self, stack) -> None:
        for index in range(3):
            _record(stack, task=f"t{index}")
        events = stack["ledger"].events()
        for event in events:
            assert Identifier.parse(event.actor.agent_id).entity_type == "agent"
            assert Identifier.parse(event.actor.agent_instance_id).entity_type == "agent-instance"
            assert Identifier.parse(event.task_id).entity_type == "task"
            assert event.event_hash.startswith("sha256:")
            assert event.signature.startswith("Ed25519:")
        for index in range(1, len(events)):
            assert events[index].previous_event_hash == events[index - 1].event_hash

    def test_canonical_history_cannot_be_modified_through_returned_event_alias(self, stack) -> None:
        returned = _record(stack)
        canonical_hash = returned.event_hash
        returned.action = "DELETE"
        returned.resource_id = "urn:attacker:modified"
        stored = stack["ledger"].get(returned.event_id)
        assert stored is not None
        assert stored.action == "SEARCH"
        assert stored.resource_id == "urn:resource:t1"
        assert stored.event_hash == canonical_hash

        snapshots = stack["ledger"].events()
        snapshots[0].action = "DELETE"
        stored_again = stack["ledger"].get(returned.event_id)
        assert stored_again is not None and stored_again.action == "SEARCH"

    def test_public_projection_does_not_expose_raw_event_fields(self, stack) -> None:
        event = stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "public-task")),
            action="SEARCH",
            visibility="PUBLIC",
            signing_key_id=stack["key_id"],
            authorization_id=str(make_identifier("authorization", "internal-auth")),
            resource_id="urn:private:resource",
        )
        raw = event.to_dict()
        assert "actor" in raw and "authorization_id" in raw and "resource_id" in raw
        public = PublicEventProjector().project(event)
        assert not SENSITIVE_EVENT_FIELDS.intersection(public)
        serialized = json.dumps(public)
        assert stack["actor"].principal_id not in serialized
        assert "internal-auth" not in serialized
        assert "private:resource" not in serialized

    def test_full_signature_verification_requires_available_public_keys(self, stack) -> None:
        _record(stack)
        report = LedgerVerifier(stack["keys"]).verify(stack["ledger"])
        assert report.ok
        assert report.verified_signature_count == 1

        missing_keys = LedgerVerifier(KeyService()).verify(stack["ledger"])
        assert not missing_keys.ok
        assert any("verification key unavailable" in failure for failure in missing_keys.failures)

    def test_parallel_signature_verification_preserves_deterministic_result(self, stack) -> None:
        for index in range(50):
            _record(stack, task=f"parallel-{index}")
        sequential = LedgerVerifier(stack["keys"]).verify(stack["ledger"])
        parallel = LedgerVerifier(
            stack["keys"],
            parallel_signatures=True,
            max_workers=4,
        ).verify(stack["ledger"])
        assert sequential.ok and parallel.ok
        assert sequential.verified_signature_count == 50
        assert parallel.verified_signature_count == 50
        assert parallel.verification_mode == "hash-chain+parallel-signatures"
