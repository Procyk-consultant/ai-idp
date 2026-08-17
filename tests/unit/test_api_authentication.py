"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_api_authentication.py
Purpose: Unit tests for signed API action-request authentication
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from aegistrace.api.authentication import (
    ActionRequestAuthenticator,
    RequestAuthenticationError,
    action_request_message,
)
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService


def _payload(agent_id: str, key_id: str, *, timestamp: str | None = None, nonce: str = "0123456789abcdef") -> dict:
    return {
        "controller_id": str(make_identifier("controller", "c1")),
        "principal_id": str(make_identifier("principal", "p1")),
        "agent_id": agent_id,
        "agent_instance_id": str(make_identifier("agent-instance", "a1", version="r1")),
        "provider_id": str(make_identifier("provider", "p1")),
        "model_id": str(make_identifier("model", "m1")),
        "model_version_id": str(make_identifier("model", "m1", version="v1")),
        "deployment_id": str(make_identifier("deployment", "d1")),
        "task_id": str(make_identifier("task", "t1")),
        "action": "SEARCH",
        "visibility": "ORGANIZATION_PRIVATE",
        "signing_key_id": key_id,
        "authorization_id": str(make_identifier("authorization", "auth-1")),
        "jurisdiction_id": "ca",
        "approval_ids": [],
        "request_timestamp": timestamp or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "request_nonce": nonce,
    }


class TestActionRequestAuthenticator:
    def test_valid_proof_of_possession_is_accepted_once(self) -> None:
        keys = KeyService()
        agent = str(make_identifier("agent", "a1"))
        key_id = str(make_identifier("key", "k1"))
        signing_key = keys.create_key(key_id, bound_entity_id=agent)
        payload = _payload(agent, key_id)
        signature = signing_key.sign(action_request_message(payload))
        authenticator = ActionRequestAuthenticator(keys)
        authenticator.verify_and_reserve(payload, signature)
        with pytest.raises(RequestAuthenticationError, match="already been used"):
            authenticator.verify_and_reserve(payload, signature)

    def test_tampered_payload_fails_signature(self) -> None:
        keys = KeyService()
        agent = str(make_identifier("agent", "a1"))
        key_id = str(make_identifier("key", "k1"))
        signing_key = keys.create_key(key_id, bound_entity_id=agent)
        payload = _payload(agent, key_id)
        signature = signing_key.sign(action_request_message(payload))
        payload["action"] = "DELETE"
        with pytest.raises(RequestAuthenticationError, match="signature"):
            ActionRequestAuthenticator(keys).verify_and_reserve(payload, signature)

    def test_stale_timestamp_is_rejected(self) -> None:
        keys = KeyService()
        agent = str(make_identifier("agent", "a1"))
        key_id = str(make_identifier("key", "k1"))
        signing_key = keys.create_key(key_id, bound_entity_id=agent)
        stale = (datetime.now(UTC) - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ")
        payload = _payload(agent, key_id, timestamp=stale)
        signature = signing_key.sign(action_request_message(payload))
        with pytest.raises(RequestAuthenticationError, match="clock-skew"):
            ActionRequestAuthenticator(keys, max_clock_skew_seconds=60).verify_and_reserve(payload, signature)

    def test_key_bound_to_different_agent_is_rejected(self) -> None:
        keys = KeyService()
        agent = str(make_identifier("agent", "a1"))
        attacker = str(make_identifier("agent", "attacker"))
        key_id = str(make_identifier("key", "attacker-key"))
        signing_key = keys.create_key(key_id, bound_entity_id=attacker)
        payload = _payload(agent, key_id)
        signature = signing_key.sign(action_request_message(payload))
        with pytest.raises(RequestAuthenticationError, match="not bound"):
            ActionRequestAuthenticator(keys).verify_and_reserve(payload, signature)
