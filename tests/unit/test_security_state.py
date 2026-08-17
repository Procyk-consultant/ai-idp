"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/unit/test_security_state.py
Purpose: Durable replay and approval-consumption state tests
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

import pytest

from aegistrace.api.authentication import (
    ActionRequestAuthenticator,
    RequestAuthenticationError,
    action_request_message,
)
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.storage.sqlite import SQLiteStorage


def _timestamp(delta_seconds: int = 0) -> str:
    return (datetime.now(UTC) + timedelta(seconds=delta_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_sqlite_replay_reservation_persists_across_store_instances(tmp_path) -> None:
    path = tmp_path / "aegistrace.db"
    store_1 = SQLiteStorage(path)
    try:
        assert store_1.reserve_nonce(
            "aitrace://ca/key/k1",
            "0123456789abcdef",
            expires_at=_timestamp(300),
        )
    finally:
        store_1.close()

    store_2 = SQLiteStorage(path)
    try:
        assert not store_2.reserve_nonce(
            "aitrace://ca/key/k1",
            "0123456789abcdef",
            expires_at=_timestamp(300),
        )
    finally:
        store_2.close()


def test_sqlite_approval_consumption_is_atomic_and_persistent(tmp_path) -> None:
    path = tmp_path / "aegistrace.db"
    ids = (
        "aitrace://ca/approval/a1",
        "aitrace://ca/approval/a2",
    )
    store = SQLiteStorage(path)
    try:
        assert store.approvals_available(ids)
        assert store.consume_approvals(ids, used_at=_timestamp())
        assert not store.approvals_available(ids)
        assert not store.consume_approvals(ids, used_at=_timestamp())
    finally:
        store.close()

    reopened = SQLiteStorage(path)
    try:
        assert not reopened.approvals_available(ids)
    finally:
        reopened.close()


def test_authenticator_uses_durable_replay_store_across_instances(tmp_path) -> None:
    keys = KeyService()
    agent_id = str(make_identifier("agent", "a1"))
    key_id = str(make_identifier("key", "k1"))
    keys.create_key(key_id, bound_entity_id=agent_id)
    payload = {
        "controller_id": str(make_identifier("controller", "c1")),
        "principal_id": str(make_identifier("principal", "p1")),
        "agent_id": agent_id,
        "agent_instance_id": str(make_identifier("agent-instance", "a1", version="run-1")),
        "provider_id": str(make_identifier("provider", "provider-1")),
        "model_id": str(make_identifier("model", "model-1")),
        "model_version_id": str(make_identifier("model", "model-1", version="v1")),
        "deployment_id": str(make_identifier("deployment", "dep-1")),
        "task_id": str(make_identifier("task", "task-1")),
        "action": "SEARCH",
        "visibility": "ORGANIZATION_PRIVATE",
        "signing_key_id": key_id,
        "authorization_id": str(make_identifier("authorization", "auth-1")),
        "jurisdiction_id": "ca",
        "approval_ids": [],
        "request_timestamp": _timestamp(),
        "request_nonce": secrets.token_hex(16),
    }
    signature = keys.get_signing_key(key_id).sign(action_request_message(payload))
    path = tmp_path / "aegistrace.db"

    store_1 = SQLiteStorage(path)
    try:
        ActionRequestAuthenticator(keys, replay_store=store_1).verify_and_reserve(
            payload,
            signature,
        )
    finally:
        store_1.close()

    store_2 = SQLiteStorage(path)
    try:
        with pytest.raises(RequestAuthenticationError, match="already been used"):
            ActionRequestAuthenticator(keys, replay_store=store_2).verify_and_reserve(
                payload,
                signature,
            )
    finally:
        store_2.close()
