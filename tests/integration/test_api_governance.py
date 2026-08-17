"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/integration/test_api_governance.py
Purpose: Integration tests for governed API writes and public-safe reads
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from aegistrace.api.server import create_app
from aegistrace.authorization.engine import PolicyEngine
from aegistrace.delegation.broker import DelegationBroker
from aegistrace.events.collector import EventCollector
from aegistrace.events.models import Actor, ExecutionContext
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.identity.lifecycle import Registry
from aegistrace.ledger.append_only import AppendOnlyLedger


@pytest.fixture
def api_stack():
    keys = KeyService()
    registry = Registry()
    ledger = AppendOnlyLedger()
    policy = PolicyEngine(keys)
    delegations = DelegationBroker(keys)

    controller = str(make_identifier("controller", "org-001"))
    principal = str(make_identifier("principal", "principal-001"))
    agent = str(make_identifier("agent", "agent-001"))
    instance = str(make_identifier("agent-instance", "agent-001", version="run-001"))
    provider = str(make_identifier("provider", "provider-001"))
    model = str(make_identifier("model", "model-001"))
    model_version = str(make_identifier("model", "model-001", version="v1"))
    deployment = str(make_identifier("deployment", "deployment-001"))
    task = str(make_identifier("task", "task-001"))
    agent_key = str(make_identifier("key", "agent-key"))
    controller_key = str(make_identifier("key", "controller-key"))

    registry.register(controller, "controller")
    registry.register(principal, "principal", {"email": "private@example.invalid"})
    registry.register(agent, "agent", {"controller_id": controller})
    registry.register(instance, "agent-instance", {"agent_id": agent})
    registry.register(
        provider,
        "provider",
        {
            "public": True,
            "public_attributes": {"label": "Example Provider"},
            "internal_contract": "SECRET-CONTRACT",
        },
    )
    registry.register(model, "model")
    registry.register(model_version, "model")
    registry.register(deployment, "deployment")
    registry.register(task, "task")

    keys.create_key(agent_key, bound_entity_id=agent)
    keys.create_key(controller_key, bound_entity_id=controller)
    authorization = policy.issue_authorization(
        principal_id=principal,
        controller_id=controller,
        agent_id=agent,
        task_id=task,
        scope={"action_classes": ["SEARCH", "READ"]},
        signing_key_id=controller_key,
    )

    app = create_app(
        registry=registry,
        key_service=keys,
        ledger=ledger,
        policy_engine=policy,
        delegation_broker=delegations,
    )
    client = TestClient(app)
    payload = {
        "controller_id": controller,
        "principal_id": principal,
        "agent_id": agent,
        "agent_instance_id": instance,
        "provider_id": provider,
        "model_id": model,
        "model_version_id": model_version,
        "deployment_id": deployment,
        "task_id": task,
        "action": "SEARCH",
        "visibility": "PUBLIC",
        "signing_key_id": agent_key,
        "authorization_id": authorization.authorization_id,
        "resource_id": "urn:client:private-resource",
    }
    return {
        "client": client,
        "app": app,
        "keys": keys,
        "registry": registry,
        "ledger": ledger,
        "policy": policy,
        "delegations": delegations,
        "authorization": authorization,
        "payload": payload,
        "ids": {
            "controller": controller,
            "principal": principal,
            "agent": agent,
            "instance": instance,
            "provider": provider,
            "model": model,
            "model_version": model_version,
            "deployment": deployment,
            "task": task,
            "agent_key": agent_key,
        },
    }


class TestAPIGovernance:
    def test_post_event_crosses_governed_boundary(self, api_stack) -> None:
        response = api_stack["client"].post("/events", json=api_stack["payload"])
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["governance_mode"] == "GOVERNED"
        assert body["authorization_id"] == api_stack["authorization"].authorization_id

    def test_missing_authorization_field_is_rejected_by_contract(self, api_stack) -> None:
        payload = dict(api_stack["payload"])
        payload.pop("authorization_id")
        response = api_stack["client"].post("/events", json=payload)
        assert response.status_code == 422

    def test_unknown_authorization_is_denied_not_executed(self, api_stack) -> None:
        payload = dict(api_stack["payload"])
        payload["visibility"] = "ORGANIZATION_PRIVATE"
        payload["authorization_id"] = str(make_identifier("authorization", "missing"))
        response = api_stack["client"].post("/events", json=payload)
        assert response.status_code == 403
        body = response.json()["detail"]
        assert body["reason"] == "authorization not found"
        assert body["denial_event_id"] is not None
        events = api_stack["ledger"].events()
        assert len(events) == 1
        assert events[0].action == "DENY"

    def test_public_list_is_strict_projection(self, api_stack) -> None:
        response = api_stack["client"].post("/events", json=api_stack["payload"])
        assert response.status_code == 200
        event_id = response.json()["event_id"]

        listing = api_stack["client"].get("/events")
        assert listing.status_code == 200
        records = listing.json()
        assert len(records) == 1
        public = records[0]
        assert public["event_id"] == event_id
        for forbidden_field in (
            "actor",
            "execution_context",
            "task_id",
            "action",
            "authorization_id",
            "resource_id",
            "approval_ids",
            "delegation_chain",
            "scope_context",
            "decision_reason",
        ):
            assert forbidden_field not in public
        serialized = json.dumps(public)
        assert api_stack["ids"]["principal"] not in serialized
        assert "private-resource" not in serialized

    def test_nonpublic_event_cannot_be_enumerated_or_fetched(self, api_stack) -> None:
        payload = dict(api_stack["payload"])
        payload["visibility"] = "ORGANIZATION_PRIVATE"
        payload["action"] = "READ"
        response = api_stack["client"].post("/events", json=payload)
        assert response.status_code == 200
        event_id = response.json()["event_id"]

        listing = api_stack["client"].get("/events")
        assert listing.status_code == 200
        assert listing.json() == []
        fetched = api_stack["client"].get(f"/events/{event_id}")
        assert fetched.status_code == 404

    def test_public_verification_keys_are_scoped_and_do_not_expose_bindings(self, api_stack) -> None:
        private_agent = str(make_identifier("agent", "private-agent"))
        private_instance = str(make_identifier("agent-instance", "private-agent", version="run-1"))
        private_key = str(make_identifier("key", "private-key"))
        api_stack["keys"].create_key(private_key, bound_entity_id=private_agent)
        collector = EventCollector(api_stack["ledger"], api_stack["keys"])
        collector.record(
            actor=Actor(
                controller_id=api_stack["ids"]["controller"],
                principal_id=api_stack["ids"]["principal"],
                agent_id=private_agent,
                agent_instance_id=private_instance,
            ),
            execution_context=ExecutionContext(
                provider_id=api_stack["ids"]["provider"],
                model_id=api_stack["ids"]["model"],
                model_version_id=api_stack["ids"]["model_version"],
                deployment_id=api_stack["ids"]["deployment"],
            ),
            task_id=api_stack["ids"]["task"],
            action="READ",
            visibility="ORGANIZATION_PRIVATE",
            signing_key_id=private_key,
        )
        public_response = api_stack["client"].post("/events", json=api_stack["payload"])
        assert public_response.status_code == 200

        response = api_stack["client"].get("/verification/keys")
        assert response.status_code == 200
        exported = response.json()["keys"]
        assert [record["key_id"] for record in exported] == [api_stack["ids"]["agent_key"]]
        assert all("bound_entity_id" not in record for record in exported)
        assert private_key not in json.dumps(exported)

    def test_public_registry_returns_only_reviewed_attributes(self, api_stack) -> None:
        provider_response = api_stack["client"].get(
            f"/registry/{api_stack['ids']['provider']}"
        )
        assert provider_response.status_code == 200
        assert provider_response.json()["attributes"] == {"label": "Example Provider"}
        assert "SECRET-CONTRACT" not in provider_response.text

        principal_response = api_stack["client"].get(
            f"/registry/{api_stack['ids']['principal']}"
        )
        assert principal_response.status_code == 404
        assert "private@example.invalid" not in principal_response.text

    def test_verify_endpoint_does_not_disclose_failure_details(self, api_stack) -> None:
        response = api_stack["client"].post("/events", json=api_stack["payload"])
        assert response.status_code == 200
        verification = api_stack["client"].post("/verify")
        assert verification.status_code == 200
        body = verification.json()
        assert body["ok"] is True
        assert "failures" not in body
        assert "failing_event_ids" not in body
        assert body["verified_signature_count"] == 1
