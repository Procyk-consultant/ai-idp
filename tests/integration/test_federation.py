"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: tests/integration/test_federation.py
Purpose: Signed federation agreement, resolution, break, and verification tests
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""
from __future__ import annotations

import copy
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from aegistrace.events.collector import EventCollector
from aegistrace.events.models import Actor, ExecutionContext
from aegistrace.federation.gateway import (
    FederationAgreement,
    FederationGateway,
    FederationResolutionError,
)
from aegistrace.identity.ids import make_identifier
from aegistrace.identity.keys import KeyService
from aegistrace.ledger.append_only import AppendOnlyLedger


def _timestamp(delta_seconds: int = 0) -> str:
    return (datetime.now(UTC) + timedelta(seconds=delta_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


class FakeRegistryClient:
    def __init__(self, entity: dict | None = None) -> None:
        self.entity = entity
        self.entity_calls = 0
        self.healthy = True
        self.raise_on_resolve = False

    def health(self) -> bool:
        return self.healthy

    def resolve_public_entity(self, entity_id: str) -> dict | None:
        self.entity_calls += 1
        if self.raise_on_resolve:
            raise OSError("remote unavailable")
        return copy.deepcopy(self.entity)

    def get_public_event(self, event_id: str) -> dict | None:
        return None

    def get_public_verification_keys(self) -> dict:
        return {"schema": "aegistrace.public_keys.v1", "keys": []}


def _signed_agreement(keys: KeyService):
    local = str(make_identifier("registry-authority", "local"))
    remote = str(make_identifier("registry-authority", "remote"))
    local_key = str(make_identifier("key", "federation-local"))
    remote_key = str(make_identifier("key", "federation-remote"))
    keys.create_key(local_key, bound_entity_id=local)
    keys.create_key(remote_key, bound_entity_id=remote)
    unsigned = FederationAgreement(
        agreement_id=str(make_identifier("federation-agreement", "agreement-1")),
        local_authority_id=local,
        remote_authority_id=remote,
        effective_at=_timestamp(-60),
        expires_at=_timestamp(3600),
        local_signing_key_id=local_key,
        remote_signing_key_id=remote_key,
        local_signature="",
        remote_signature="",
        allowed_visibility_tiers=("PUBLIC",),
        metadata={"purpose": "reference federation test"},
    )
    message = unsigned.signable_bytes()
    agreement = replace(
        unsigned,
        local_signature=keys.get_signing_key(local_key).sign(message),
        remote_signature=keys.get_signing_key(remote_key).sign(message),
    )
    return local, remote, agreement


def test_signed_federation_resolution_is_cached_and_allow_listed() -> None:
    keys = KeyService()
    local, remote, agreement = _signed_agreement(keys)
    entity_id = str(make_identifier("provider", "remote-provider"))
    client = FakeRegistryClient(
        {
            "entity_id": entity_id,
            "entity_type": "provider",
            "state": "active",
            "created_at": _timestamp(-600),
            "attributes": {"label": "Remote Provider"},
        }
    )
    gateway = FederationGateway(local, keys, cache_ttl_seconds=300)
    gateway.register_authority(agreement, client)

    first = gateway.resolve_public_entity(remote, entity_id)
    second = gateway.resolve_public_entity(remote, entity_id)
    assert first == second
    assert client.entity_calls == 1
    assert first is not None and first["attributes"] == {"label": "Remote Provider"}


def test_invalid_federation_signature_is_rejected() -> None:
    keys = KeyService()
    local, remote, agreement = _signed_agreement(keys)
    invalid = replace(agreement, remote_signature="Ed25519:" + "A" * 88)
    gateway = FederationGateway(local, keys)
    with pytest.raises(PermissionError, match="signatures"):
        gateway.register_authority(invalid, FakeRegistryClient())


def test_federation_break_is_recorded_and_failure_is_not_silently_cached() -> None:
    keys = KeyService()
    local, remote, agreement = _signed_agreement(keys)
    entity_id = str(make_identifier("provider", "remote-provider"))
    client = FakeRegistryClient()
    client.raise_on_resolve = True
    gateway = FederationGateway(local, keys)
    gateway.register_authority(agreement, client)

    with pytest.raises(FederationResolutionError, match="unavailable"):
        gateway.resolve_public_entity(remote, entity_id)
    breaks = gateway.federation_breaks()
    assert len(breaks) == 1
    assert breaks[0].authority_id == remote
    assert breaks[0].agreement_id == agreement.agreement_id


def test_disclosed_cross_registry_chain_is_cryptographically_verifiable() -> None:
    keys = KeyService()
    ledger = AppendOnlyLedger()
    agent = str(make_identifier("agent", "agent-1"))
    key_id = str(make_identifier("key", "agent-key"))
    keys.create_key(key_id, bound_entity_id=agent)
    collector = EventCollector(ledger, keys)
    actor = Actor(
        controller_id=str(make_identifier("controller", "org-1")),
        principal_id=str(make_identifier("principal", "p1")),
        agent_id=agent,
        agent_instance_id=str(make_identifier("agent-instance", "agent-1", version="run-1")),
    )
    context = ExecutionContext(
        provider_id=str(make_identifier("provider", "provider-1")),
        model_id=str(make_identifier("model", "model-1")),
        model_version_id=str(make_identifier("model", "model-1", version="v1")),
        deployment_id=str(make_identifier("deployment", "dep-1")),
    )
    for index in range(2):
        collector.record(
            actor=actor,
            execution_context=context,
            task_id=str(make_identifier("task", f"task-{index}")),
            action="SEARCH",
            visibility="CONTROLLED",
            signing_key_id=key_id,
            resource_id=f"urn:web:{index}",
        )
    events = [event.to_dict() for event in ledger.events()]
    public_keys = {key_id: keys.get_public_pem(key_id)}
    assert FederationGateway.verify_disclosed_chain(events, public_keys=public_keys)

    tampered = copy.deepcopy(events)
    tampered[1]["resource_id"] = "urn:web:tampered"
    assert not FederationGateway.verify_disclosed_chain(tampered, public_keys=public_keys)
