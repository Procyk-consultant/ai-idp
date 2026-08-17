"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/privacy/test_redaction.py
Purpose: Privacy tests for projection, tier isolation, and pseudonymization
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json

import pytest

from aegistrace.authorization.scope import ScopeContext
from aegistrace.disclosure.public import (
    PUBLIC_EVENT_PROOF_FIELDS,
    SENSITIVE_EVENT_FIELDS,
    PublicEventProjector,
    PublicProjectionError,
)
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
    principal = str(make_identifier("principal", "user-XYZ"))
    agent = str(make_identifier("agent", "a1"))
    instance = str(make_identifier("agent-instance", "a1", version="r1"))
    key_id = str(make_identifier("key", "k1"))
    keys.create_key(key_id, bound_entity_id=agent)
    actor = Actor(
        controller_id=controller,
        principal_id=principal,
        agent_id=agent,
        agent_instance_id=instance,
    )
    execution_context = ExecutionContext(
        provider_id=str(make_identifier("provider", "p1")),
        model_id=str(make_identifier("model", "m1")),
        model_version_id=str(make_identifier("model", "m1", version="v1")),
        deployment_id=str(make_identifier("deployment", "d1")),
    )
    return {
        "ledger": ledger,
        "keys": keys,
        "collector": collector,
        "actor": actor,
        "ec": execution_context,
        "key_id": key_id,
        "projector": PublicEventProjector(),
    }


class TestPrivacy:
    def test_principal_identifier_is_pseudonymous(self, stack) -> None:
        assert "user-" in stack["actor"].principal_id
        assert "@" not in stack["actor"].principal_id
        assert stack["actor"].principal_id.startswith("aitrace://ca/principal/")

    def test_all_visibility_tiers_are_canonical(self, stack) -> None:
        for tier in VISIBILITY_TIERS:
            stack["collector"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=str(make_identifier("task", f"t-{tier.lower()}")),
                action="SEARCH",
                visibility=tier,
                signing_key_id=stack["key_id"],
                resource_id=f"urn:web:{tier}",
            )
        assert {event.visibility for event in stack["ledger"].events()} == set(VISIBILITY_TIERS)

    def test_public_projection_is_allowlist_based(self, stack) -> None:
        event = stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "public-task")),
            action="PUBLISH",
            visibility="PUBLIC",
            signing_key_id=stack["key_id"],
            authorization_id=str(make_identifier("authorization", "auth-public")),
            approval_ids=[
                str(make_identifier("approval", "approval-1")),
                str(make_identifier("approval", "approval-2")),
            ],
            delegation_id=str(make_identifier("delegation", "delegation-1")),
            delegation_chain=[str(make_identifier("delegation", "delegation-1"))],
            scope_context=ScopeContext(
                task_class="confidential-task-class",
                resource_class="client-file",
                geography="ca-qc",
                tool_class="internal-tool",
                model_class="internal-model-class",
                provider_class="internal-provider-class",
            ),
            governance_mode="GOVERNED",
            decision_reason="internal approval rationale",
            resource_id="urn:client:confidential-resource",
            before_digest="sha256:" + "a" * 64,
            after_digest="sha256:" + "b" * 64,
        )
        raw = event.to_dict()
        assert SENSITIVE_EVENT_FIELDS.intersection(raw)

        public = stack["projector"].project(event)
        assert set(public) == set(PUBLIC_EVENT_PROOF_FIELDS)
        assert not SENSITIVE_EVENT_FIELDS.intersection(public)
        serialized = json.dumps(public, sort_keys=True)
        for forbidden in (
            stack["actor"].principal_id,
            stack["actor"].agent_id,
            "confidential-resource",
            "internal approval rationale",
            "client-file",
            "approval-1",
            "delegation-1",
        ):
            assert forbidden not in serialized

    def test_public_projection_rejects_nonpublic_records(self, stack) -> None:
        for tier in ("CONTROLLED", "ORGANIZATION_PRIVATE", "SEALED"):
            event = stack["collector"].record(
                actor=stack["actor"],
                execution_context=stack["ec"],
                task_id=str(make_identifier("task", f"t-{tier.lower()}")),
                action="READ",
                visibility=tier,
                signing_key_id=stack["key_id"],
                resource_id=f"urn:private:{tier}",
            )
            with pytest.raises(PublicProjectionError):
                stack["projector"].project(event)

    def test_project_many_excludes_nonpublic_events(self, stack) -> None:
        public_event = stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "public")),
            action="SEARCH",
            visibility="PUBLIC",
            signing_key_id=stack["key_id"],
        )
        stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "private")),
            action="ACCESS_SECRET",
            visibility="SEALED",
            signing_key_id=stack["key_id"],
            resource_id="urn:secret:vault-1",
        )
        projections = stack["projector"].project_many(stack["ledger"].events())
        assert len(projections) == 1
        assert projections[0]["event_id"] == public_event.event_id

    def test_public_key_export_does_not_disclose_private_binding(self, stack) -> None:
        exported = stack["keys"].export_public_registry(key_ids=[stack["key_id"]])
        assert len(exported["keys"]) == 1
        key_record = exported["keys"][0]
        assert "public_pem" in key_record
        assert "bound_entity_id" not in key_record
        serialized = json.dumps(exported)
        assert stack["actor"].agent_id not in serialized

    def test_raw_event_contains_no_accidental_real_contact_literals(self, stack) -> None:
        event = stack["collector"].record(
            actor=stack["actor"],
            execution_context=stack["ec"],
            task_id=str(make_identifier("task", "t1")),
            action="SEARCH",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=stack["key_id"],
            resource_id="urn:web:1",
        )
        serialized = repr(event.to_dict())
        assert "p.procyk.media@gmail.com" not in serialized
        assert "+1 (581)" not in serialized
        assert "linkedin.com" not in serialized
